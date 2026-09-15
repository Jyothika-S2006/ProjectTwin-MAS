import hashlib
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple
from core.models import (
    RawExecutionEvent, CandidateMatch, ScheduleUpdateCandidate,
    RoutingStatus, AuditLogEntry, ActivityStatus
)

class ValidationAgent:
    """
    Validation & Logic Checks Agent.
    Enforces CPM precedence integrity, cross-source contradiction detection,
    confidence-based routing, and evidence-bound audit logging.
    """
    def __init__(self, schedule_engine):
        self.schedule_engine = schedule_engine
        self.pending_candidates: Dict[str, ScheduleUpdateCandidate] = {}
        self.audit_log: List[AuditLogEntry] = []

    def validate_and_route(
        self,
        event: RawExecutionEvent,
        candidates: List[CandidateMatch]
    ) -> ScheduleUpdateCandidate:
        """
        Applies confidence routing rules, CPM sequence validation, and contradiction checks.
        """
        top_match = candidates[0] if candidates else None
        top_confidence = top_match.composite_confidence if top_match else 0.0

        routing_reasons = []
        has_contradiction = False
        contradiction_details = None
        precedence_violation = False
        precedence_details = None

        target_act_id = top_match.activity_id if top_match else None

        # 1. Precedence & CPM Sequence Check
        if target_act_id and target_act_id in self.schedule_engine.baseline_activities:
            is_valid, warnings = self.schedule_engine.check_precedence(target_act_id)
            if not is_valid:
                precedence_violation = True
                precedence_details = "; ".join(warnings)
                routing_reasons.append(f"CPM Precedence Alert: {precedence_details}")

        # 2. Contradiction Detection across sources
        if target_act_id and target_act_id in self.schedule_engine.actual_states:
            current_actual = self.schedule_engine.actual_states[target_act_id]
            # Check for contradiction: Event says "DELAYED" or 0% progress but current state was already claimed 100%
            if event.reported_status == "DELAYED" and current_actual.status == ActivityStatus.COMPLETED:
                has_contradiction = True
                contradiction_details = (
                    f"Contradiction: Event reports DELAYED/stoppage on {event.event_date}, "
                    f"but schedule already marked {target_act_id} as COMPLETED."
                )
                routing_reasons.append(contradiction_details)
            elif event.progress_pct and current_actual.progress_pct > event.progress_pct + 30.0:
                has_contradiction = True
                contradiction_details = (
                    f"Progress regression: Event claims {event.progress_pct}%, "
                    f"while current record holds {current_actual.progress_pct}%."
                )
                routing_reasons.append(contradiction_details)

        # 3. Confidence-Based Routing Logic (Slide 3 Matrix)
        if top_confidence >= 90.0 and not has_contradiction and not precedence_violation:
            decision = RoutingStatus.AUTO_SOFT_UPDATE
            routing_reasons.append("High confidence (>=90%) with zero logical or precedence conflicts -> Auto-Link.")
        elif top_confidence >= 60.0 or has_contradiction or precedence_violation:
            decision = RoutingStatus.PLANNER_REVIEW
            if top_confidence >= 60.0:
                routing_reasons.append(f"Medium confidence ({top_confidence:.1f}%) requires human planner verification.")
            if has_contradiction:
                routing_reasons.append("Contradiction detected: Escalated to Planner Review Queue.")
            if precedence_violation:
                routing_reasons.append("Precedence anomaly detected: Escalated to Planner Review Queue.")
        else:
            decision = RoutingStatus.SUPERVISOR_CLARIFICATION
            routing_reasons.append(f"Low confidence ({top_confidence:.1f}% < 60%) -> Routed back to Supervisor for clarification.")

        candidate_id = f"CAND-{uuid.uuid4().hex[:8].upper()}"
        candidate = ScheduleUpdateCandidate(
            candidate_id=candidate_id,
            raw_event=event,
            top_matches=candidates,
            selected_activity_id=target_act_id if decision == RoutingStatus.AUTO_SOFT_UPDATE else None,
            composite_confidence=top_confidence,
            routing_decision=decision,
            routing_reasons=routing_reasons,
            has_contradiction=has_contradiction,
            precedence_violation=precedence_violation,
            contradiction_details=contradiction_details,
            precedence_details=precedence_details,
            status="COMMITTED" if decision == RoutingStatus.AUTO_SOFT_UPDATE else "PENDING",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # If auto-soft update, commit directly to protected actuals layer
        if decision == RoutingStatus.AUTO_SOFT_UPDATE and target_act_id:
            self._commit_update(candidate, actor="System Auto-Agent")

        self.pending_candidates[candidate_id] = candidate
        return candidate

    def _commit_update(self, candidate: ScheduleUpdateCandidate, actor: str = "System Auto-Agent") -> AuditLogEntry:
        """Commits candidate update to ScheduleEngine's Actuals Layer with evidence cryptographic hash."""
        act_id = candidate.selected_activity_id or (candidate.top_matches[0].activity_id if candidate.top_matches else None)
        if not act_id:
            raise ValueError("No target activity specified for commit.")

        event = candidate.raw_event
        # Calculate SHA-256 evidence hash
        raw_bytes = f"{event.raw_text}|{event.source_reference}|{event.event_date}".encode("utf-8")
        evidence_hash = hashlib.sha256(raw_bytes).hexdigest()[:16]

        # Update actuals in protected layer
        old_state = self.schedule_engine.actual_states.get(act_id)
        old_pct = old_state.progress_pct if old_state else 0.0
        old_status = old_state.status.value if old_state else "NOT_STARTED"

        new_state = self.schedule_engine.update_actuals(
            activity_id=act_id,
            actual_start=event.event_date if event.reported_status in ["IN_PROGRESS", "COMPLETED"] else None,
            actual_finish=event.event_date if event.reported_status == "COMPLETED" or (event.progress_pct and event.progress_pct >= 100.0) else None,
            progress_pct=event.progress_pct,
            evidence_source=f"[{event.source_type}] {event.source_reference}",
            delay_reason=event.blocker,
            blocker_category=event.delay_category
        )

        audit_entry = AuditLogEntry(
            audit_id=f"AUDIT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            activity_id=act_id,
            action="ACTUALS_UPDATED",
            actor=actor,
            confidence=candidate.composite_confidence,
            evidence_hash=evidence_hash,
            raw_text_citation=event.text_citation or event.raw_text,
            diff_summary=f"Progress: {old_pct:.1f}% -> {new_state.progress_pct:.1f}%",
            status_change=f"{old_status} -> {new_state.status.value}"
        )
        self.audit_log.append(audit_entry)
        candidate.status = "COMMITTED"
        candidate.resolved_by = actor
        return audit_entry

    def resolve_planner_candidate(
        self,
        candidate_id: str,
        selected_act_id: str,
        action: str = "ACCEPT", # "ACCEPT", "REJECT", "MODIFY"
        planner_name: str = "R. Sharma (Lead Planner)",
        notes: str = "Verified with site inspection log"
    ) -> ScheduleUpdateCandidate:
        """Allows human planner to review, reassign candidate activity, and commit with audit trail."""
        if candidate_id not in self.pending_candidates:
            raise KeyError(f"Candidate {candidate_id} not found.")

        cand = self.pending_candidates[candidate_id]
        cand.selected_activity_id = selected_act_id
        cand.resolution_notes = notes

        if action == "REJECT":
            cand.status = "REJECTED"
            cand.resolved_by = planner_name
        else:
            self._commit_update(cand, actor=f"Planner [{planner_name}]")

        return cand

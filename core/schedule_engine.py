import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import networkx as nx
from core.models import (
    BaselineActivity, ActualActivityState, ActivityStatus, DisciplineEnum
)

class ScheduleEngine:
    def __init__(self):
        self.baseline_activities: Dict[str, BaselineActivity] = {}
        self.actual_states: Dict[str, ActualActivityState] = {}
        self.graph = nx.DiGraph()
        self.project_start_date: Optional[datetime] = None
        self.project_finish_date: Optional[datetime] = None
        self.audit_trail: List[Dict] = []

    def load_baseline_csv(self, filepath: str) -> int:
        """Loads Primavera P6 / MS Project baseline schedule from CSV without modifying baseline."""
        self.baseline_activities.clear()
        self.actual_states.clear()
        self.graph.clear()

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                preds = [p.strip() for p in row.get("Predecessors", "").split(";") if p.strip()]
                dur = int(row.get("Planned_Duration_Days", 1))
                weight = float(row.get("Weightage", 1.0))
                
                act = BaselineActivity(
                    activity_id=row["Activity_ID"].strip(),
                    wbs_level=row.get("WBS_Level", "L5").strip(),
                    wbs_code=row.get("WBS_Code", "").strip(),
                    activity_name=row["Activity_Name"].strip(),
                    discipline=row.get("Discipline", "General").strip(),
                    planned_start=row["Planned_Start"].strip(),
                    planned_finish=row["Planned_Finish"].strip(),
                    planned_duration_days=dur,
                    predecessors=preds,
                    weightage=weight,
                    unit_area=row.get("Unit_Area", "General").strip()
                )
                self.baseline_activities[act.activity_id] = act

                # Initialize corresponding actual state in the protected layer
                self.actual_states[act.activity_id] = ActualActivityState(
                    activity_id=act.activity_id,
                    status=ActivityStatus.NOT_STARTED,
                    progress_pct=0.0,
                    evidence_progress_pct=0.0,
                    last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

        self._build_cpm_graph()
        self.calculate_cpm()
        return len(self.baseline_activities)

    def load_baseline_xml(self, filepath: str) -> int:
        """Loads Primavera P6 XML export."""
        self.baseline_activities.clear()
        self.actual_states.clear()
        self.graph.clear()

        tree = ET.parse(filepath)
        root = tree.getroot()
        ns = {"pm": "http://www.primavera.com/pm/xml"} if "primavera" in root.tag else {}
        
        acts = root.findall(".//pm:Activity", ns) if ns else root.findall(".//Activity")
        for a in acts:
            act_id = (a.find("pm:Id", ns) if ns else a.find("Id")).text.strip()
            name = (a.find("pm:Name", ns) if ns else a.find("Name")).text.strip()
            wbs = (a.find("pm:WBSCode", ns) if ns else a.find("WBSCode"))
            wbs_text = wbs.text.strip() if wbs is not None and wbs.text else "1.0"
            disc = (a.find("pm:Discipline", ns) if ns else a.find("Discipline"))
            disc_text = disc.text.strip() if disc is not None and disc.text else "General"
            start_elem = (a.find("pm:PlannedStartDate", ns) if ns else a.find("PlannedStartDate"))
            p_start = start_elem.text.strip() if start_elem is not None else "2026-10-01"
            finish_elem = (a.find("pm:PlannedFinishDate", ns) if ns else a.find("PlannedFinishDate"))
            p_finish = finish_elem.text.strip() if finish_elem is not None else "2026-10-10"
            dur_elem = (a.find("pm:DurationDays", ns) if ns else a.find("DurationDays"))
            p_dur = int(dur_elem.text.strip()) if dur_elem is not None else 5
            pred_elem = (a.find("pm:Predecessors", ns) if ns else a.find("Predecessors"))
            preds = [p.strip() for p in pred_elem.text.split(";")] if pred_elem is not None and pred_elem.text else []
            wt_elem = (a.find("pm:Weightage", ns) if ns else a.find("Weightage"))
            wt = float(wt_elem.text.strip()) if wt_elem is not None and wt_elem.text else 1.0

            act = BaselineActivity(
                activity_id=act_id,
                wbs_level="L5",
                wbs_code=wbs_text,
                activity_name=name,
                discipline=disc_text,
                planned_start=p_start,
                planned_finish=p_finish,
                planned_duration_days=p_dur,
                predecessors=preds,
                weightage=wt
            )
            self.baseline_activities[act.activity_id] = act
            self.actual_states[act.activity_id] = ActualActivityState(
                activity_id=act.activity_id,
                status=ActivityStatus.NOT_STARTED,
                progress_pct=0.0
            )

        self._build_cpm_graph()
        self.calculate_cpm()
        return len(self.baseline_activities)

    def _build_cpm_graph(self):
        self.graph.clear()
        for act_id, act in self.baseline_activities.items():
            self.graph.add_node(act_id, duration=act.planned_duration_days, name=act.activity_name)
            for pred in act.predecessors:
                if pred in self.baseline_activities:
                    self.graph.add_edge(pred, act_id)

    def calculate_cpm(self):
        """Calculates Critical Path Method (Early Start/Finish, Late Start/Finish, Float)."""
        if not self.baseline_activities:
            return

        dates = [datetime.strptime(act.planned_start, "%Y-%m-%d") for act in self.baseline_activities.values()]
        self.project_start_date = min(dates) if dates else datetime(2026, 10, 1)

        # Topological order for Forward Pass
        try:
            topo_order = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            # Cycle detected; handle gracefully
            topo_order = list(self.baseline_activities.keys())

        # Forward Pass
        for node in topo_order:
            act = self.baseline_activities[node]
            preds = list(self.graph.predecessors(node))
            if not preds:
                # Start offset from project start
                p_start_dt = datetime.strptime(act.planned_start, "%Y-%m-%d")
                es = max(0, (p_start_dt - self.project_start_date).days)
            else:
                es = max(self.baseline_activities[p].early_finish for p in preds)
            
            ef = es + act.planned_duration_days
            act.early_start = es
            act.early_finish = ef

        # Maximum project duration
        max_ef = max((act.early_finish for act in self.baseline_activities.values() if act.early_finish is not None), default=0)

        # Backward Pass
        for node in reversed(topo_order):
            act = self.baseline_activities[node]
            succs = list(self.graph.successors(node))
            if not succs:
                lf = max_ef
            else:
                lf = min(self.baseline_activities[s].late_start for s in succs)
            
            ls = lf - act.planned_duration_days
            act.late_start = ls
            act.late_finish = lf
            act.total_float = max(0, ls - (act.early_start or 0))
            act.is_critical = (act.total_float == 0)

    def get_critical_path(self) -> List[str]:
        """Returns list of activity IDs on the critical path."""
        return [act_id for act_id, act in self.baseline_activities.items() if act.is_critical]

    def check_precedence(self, activity_id: str) -> Tuple[bool, List[str]]:
        """
        Validates if predecessors for an activity are completed or adequately in progress.
        Returns: (is_valid, list_of_warning_messages)
        """
        if activity_id not in self.baseline_activities:
            return False, [f"Activity {activity_id} not found in baseline."]

        act = self.baseline_activities[activity_id]
        warnings = []
        is_valid = True

        for pred_id in act.predecessors:
            if pred_id in self.actual_states:
                pred_actual = self.actual_states[pred_id]
                pred_baseline = self.baseline_activities[pred_id]
                if pred_actual.progress_pct < 80.0:  # If predecessor isn't sufficiently complete
                    is_valid = False
                    warnings.append(
                        f"Predecessor '{pred_baseline.activity_name}' ({pred_id}) is only {pred_actual.progress_pct}% complete."
                    )

        return is_valid, warnings

    def update_actuals(
        self,
        activity_id: str,
        actual_start: Optional[str] = None,
        actual_finish: Optional[str] = None,
        progress_pct: Optional[float] = None,
        evidence_source: str = "",
        delay_reason: Optional[str] = None,
        blocker_category: Optional[str] = None
    ) -> ActualActivityState:
        """
        Updates actual execution progress in the Protected Actuals Layer without touching baseline.
        """
        if activity_id not in self.actual_states:
            raise KeyError(f"Activity {activity_id} does not exist.")

        state = self.actual_states[activity_id]
        if actual_start:
            state.actual_start = actual_start
        if actual_finish:
            state.actual_finish = actual_finish
        if progress_pct is not None:
            state.progress_pct = max(0.0, min(100.0, progress_pct))
            # Evidence progress is weighted by source confidence
            state.evidence_progress_pct = state.progress_pct

        if state.progress_pct >= 100.0:
            state.status = ActivityStatus.COMPLETED
            if not state.actual_finish:
                state.actual_finish = datetime.now().strftime("%Y-%m-%d")
        elif state.progress_pct > 0.0:
            state.status = ActivityStatus.IN_PROGRESS
            if not state.actual_start:
                state.actual_start = datetime.now().strftime("%Y-%m-%d")

        if delay_reason:
            if delay_reason not in state.delay_reasons:
                state.delay_reasons.append(delay_reason)
            state.status = ActivityStatus.DELAYED
        
        if blocker_category:
            state.blocker_category = blocker_category

        if evidence_source and evidence_source not in state.evidence_sources:
            state.evidence_sources.append(evidence_source)

        state.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return state

    def get_summary(self) -> Dict:
        total_acts = len(self.baseline_activities)
        completed = sum(1 for s in self.actual_states.values() if s.status == ActivityStatus.COMPLETED)
        in_prog = sum(1 for s in self.actual_states.values() if s.status == ActivityStatus.IN_PROGRESS)
        delayed = sum(1 for s in self.actual_states.values() if s.status == ActivityStatus.DELAYED)
        not_started = total_acts - completed - in_prog - delayed
        crit_count = sum(1 for a in self.baseline_activities.values() if a.is_critical)

        return {
            "total_activities": total_acts,
            "completed": completed,
            "in_progress": in_prog,
            "delayed": delayed,
            "not_started": max(0, not_started),
            "critical_activities": crit_count,
            "critical_path": self.get_critical_path()
        }

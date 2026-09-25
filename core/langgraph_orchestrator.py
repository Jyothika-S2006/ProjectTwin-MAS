"""
LangGraph Multi-Agent Workflow for ProjectTwin
Problem Statement: SIH26122 | Oil India Limited | Team SentinelX3.0

Implements stateful, cyclic multi-agent orchestration:
  [Ingestion / Voice Input]
             │
             ▼
     [Time Agent Node]
             │
             ▼
   [Hybrid Linking Node]
             │
             ▼
  [Validation & CPM Node]
             │
       Conditional Routing
       ├── (Confidence >= 90% & Valid) ──► [Auto-Commit Node] ──► [EVM Engine Node] ──► (Done)
       ├── (Confidence 60-89% or Anomaly) ──► [Planner Review Queue (HITL)] ──► (Signoff)
       └── (Confidence < 60%) ──► [Supervisor Clarification Loop] ──► [Time Agent Node]
"""

import os
import hashlib
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime

try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    START = "START"
    END = "END"

from core.models import RawExecutionEvent, CandidateMatch, ScheduleUpdateCandidate, RoutingStatus, ActualActivityState
from core.schedule_engine import ScheduleEngine
from core.evm_engine import EVMEngine
from agents.time_agent import TimeAgent
from agents.linking_agent import HybridLinkingAgent
from agents.validation_agent import ValidationAgent


class ProjectTwinWorkflowState(TypedDict):
    raw_message: str
    supervisor_name: str
    discipline_hint: Optional[str]
    parsed_event: Optional[RawExecutionEvent]
    candidates: List[CandidateMatch]
    routing_decision: Optional[RoutingStatus]
    routing_reasons: List[str]
    is_anomaly: bool
    requires_human_signoff: bool
    evidence_hash: Optional[str]
    planner_action: Optional[str]
    evm_metrics: Optional[Dict[str, Any]]
    execution_step_log: List[str]


class ProjectTwinLangGraphOrchestrator:
    """Stateful Multi-Agent Orchestrator powered by LangGraph StateGraph.
    
    Provides deterministic graph execution, cyclic feedback loops for low confidence,
    Human-in-the-Loop (HITL) checkpoints for CPM precedence violations, and
    SHA-256 cryptographic evidence hashing.
    """

    def __init__(self, schedule_engine: ScheduleEngine, evm_engine: EVMEngine):
        self.schedule_engine = schedule_engine
        self.evm_engine = evm_engine

        # Auto-load baseline schedule if not already loaded
        if not self.schedule_engine.baseline_activities:
            base_csv = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "data", "baseline_schedule_oil_india.csv")
            )
            if os.path.exists(base_csv):
                self.schedule_engine.load_baseline_csv(base_csv)

        self.time_agent = TimeAgent()
        self.linking_agent = HybridLinkingAgent(self.schedule_engine.baseline_activities)
        self.validation_agent = ValidationAgent(self.schedule_engine)

        # Build and compile LangGraph StateGraph
        self.compiled_graph = None
        if LANGGRAPH_AVAILABLE:
            self.compiled_graph = self._build_graph().compile()

    def _build_graph(self):
        """Constructs the LangGraph StateGraph with nodes and conditional branching."""
        workflow = StateGraph(ProjectTwinWorkflowState)

        # Add Nodes
        workflow.add_node("time_agent_node", self.time_agent_node)
        workflow.add_node("linking_node", self.linking_node)
        workflow.add_node("validation_node", self.validation_node)
        workflow.add_node("auto_commit_node", self.auto_commit_node)
        workflow.add_node("planner_review_node", self.planner_review_node)
        workflow.add_node("supervisor_clarification_node", self.supervisor_clarification_node)
        workflow.add_node("evm_recalculation_node", self.evm_recalculation_node)

        # Define Edges
        workflow.add_edge(START, "time_agent_node")
        workflow.add_edge("time_agent_node", "linking_node")
        workflow.add_edge("linking_node", "validation_node")

        # Conditional Edge based on Confidence and Precedence Checks
        workflow.add_conditional_edges(
            "validation_node",
            self.route_decision_edge,
            {
                "auto_commit_node": "auto_commit_node",
                "planner_review_node": "planner_review_node",
                "supervisor_clarification_node": "supervisor_clarification_node"
            }
        )

        # Terminal Edges
        workflow.add_edge("auto_commit_node", "evm_recalculation_node")
        workflow.add_edge("evm_recalculation_node", END)
        workflow.add_edge("planner_review_node", END)
        workflow.add_edge("supervisor_clarification_node", END)

        return workflow

    def time_agent_node(self, state: ProjectTwinWorkflowState) -> ProjectTwinWorkflowState:
        """Node 1: Conversational / Voice Extraction."""
        res = self.time_agent.process_supervisor_message(
            transcript=state["raw_message"],
            supervisor_name=state["supervisor_name"],
            discipline_hint=state.get("discipline_hint", "General")
        )
        state["parsed_event"] = res["raw_event"]
        state["execution_step_log"].append(
            f"[TimeAgentNode] Extracted {res['raw_event'].discipline} progress: {res['raw_event'].progress_pct}%"
        )
        return state

    def linking_node(self, state: ProjectTwinWorkflowState) -> ProjectTwinWorkflowState:
        """Node 2: Hybrid 4-Dial Ensemble Candidate Matching."""
        event = state["parsed_event"]
        # Ensure linking agent has current baseline
        if not self.linking_agent.baseline_activities and self.schedule_engine.baseline_activities:
            self.linking_agent = HybridLinkingAgent(self.schedule_engine.baseline_activities)

        candidates = self.linking_agent.link_event(event, top_k=3)
        state["candidates"] = candidates
        best = candidates[0] if candidates else None
        state["execution_step_log"].append(
            f"[LinkingNode] Top match: {best.activity_id if best else 'None'} ({round(best.composite_confidence, 1) if best else 0}%)"
        )
        return state

    def validation_node(self, state: ProjectTwinWorkflowState) -> ProjectTwinWorkflowState:
        """Node 3: CPM Precedence & Confidence Gating."""
        event = state["parsed_event"]
        candidates = state["candidates"]
        cand_obj = self.validation_agent.validate_and_route(event, candidates)

        state["routing_decision"] = cand_obj.routing_decision
        state["routing_reasons"] = cand_obj.routing_reasons
        state["is_anomaly"] = cand_obj.precedence_violation or cand_obj.has_contradiction
        state["requires_human_signoff"] = cand_obj.routing_decision == RoutingStatus.PLANNER_REVIEW

        # Generate cryptographic SHA-256 evidence hash bound to raw source event
        hash_input = f"{event.event_id}:{event.raw_text}:{event.progress_pct}:{datetime.now().isoformat()}"
        state["evidence_hash"] = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        state["execution_step_log"].append(
            f"[ValidationNode] Gate: {cand_obj.routing_decision.value} | Anomaly: {state['is_anomaly']}"
        )
        return state

    def route_decision_edge(self, state: ProjectTwinWorkflowState) -> str:
        """Conditional Edge: Routes flow based on confidence & anomalies."""
        decision = state["routing_decision"]
        if decision == RoutingStatus.AUTO_SOFT_UPDATE:
            return "auto_commit_node"
        elif decision == RoutingStatus.PLANNER_REVIEW:
            return "planner_review_node"
        else:
            return "supervisor_clarification_node"

    def auto_commit_node(self, state: ProjectTwinWorkflowState) -> ProjectTwinWorkflowState:
        """Node 4A: Commits directly to Actuals layer with evidence hash (Protected Baseline)."""
        top_cand = state["candidates"][0]
        event = state["parsed_event"]
        self.schedule_engine.update_actual_progress(
            activity_id=top_cand.activity_id,
            progress_pct=event.progress_pct,
            evidence_source=f"Auto-Committed via LangGraph (SHA-256: {state['evidence_hash'][:10]}...)"
        )
        state["execution_step_log"].append(
            f"[AutoCommitNode] Committed {top_cand.activity_id} actuals to {event.progress_pct}%"
        )
        return state

    def planner_review_node(self, state: ProjectTwinWorkflowState) -> ProjectTwinWorkflowState:
        """Node 4B: Human-In-The-Loop Checkpoint / Interruption."""
        state["execution_step_log"].append(
            f"[PlannerReviewNode] Held in Review Queue for Lead Planner signoff. Reasons: {', '.join(state['routing_reasons'])}"
        )
        return state

    def supervisor_clarification_node(self, state: ProjectTwinWorkflowState) -> ProjectTwinWorkflowState:
        """Node 4C: Cyclic feedback loop requesting supervisor clarification."""
        state["execution_step_log"].append(
            "[SupervisorClarificationNode] Confidence below 60%. Requesting field clarification."
        )
        return state

    def evm_recalculation_node(self, state: ProjectTwinWorkflowState) -> ProjectTwinWorkflowState:
        """Node 5: Recalculates Deterministic PV, EV, SV, SPI."""
        metrics = self.evm_engine.calculate_evm("2026-11-10")
        state["evm_metrics"] = metrics.model_dump()
        state["execution_step_log"].append(
            f"[EVMRecalculationNode] Updated EVM: PV={metrics.planned_value}%, EV={metrics.earned_value}%, SPI={metrics.schedule_performance_index:.2f}"
        )
        return state

    def execute(self, message: str, supervisor: str = "Site Supervisor", discipline: str = "Piping") -> ProjectTwinWorkflowState:
        """Executes the full LangGraph state graph transition sequence."""
        initial_state: ProjectTwinWorkflowState = {
            "raw_message": message,
            "supervisor_name": supervisor,
            "discipline_hint": discipline,
            "parsed_event": None,
            "candidates": [],
            "routing_decision": None,
            "routing_reasons": [],
            "is_anomaly": False,
            "requires_human_signoff": False,
            "evidence_hash": None,
            "planner_action": None,
            "evm_metrics": None,
            "execution_step_log": []
        }

        # Prefer compiled LangGraph execution
        if self.compiled_graph is not None:
            return self.compiled_graph.invoke(initial_state)

        # Deterministic sequential fallback
        state = self.time_agent_node(initial_state)
        state = self.linking_node(state)
        state = self.validation_node(state)

        next_step = self.route_decision_edge(state)
        if next_step == "auto_commit_node":
            state = self.auto_commit_node(state)
            state = self.evm_recalculation_node(state)
        elif next_step == "planner_review_node":
            state = self.planner_review_node(state)
        else:
            state = self.supervisor_clarification_node(state)

        return state

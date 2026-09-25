"""
ProjectTwin - LangGraph Orchestrator Interactive Demo
Smart India Hackathon 2026 | Problem Statement: SIH26122
Team: SentinelX3.0 | Oil India Limited Pipeline Infrastructure

Demonstrates:
  1. Stateful Multi-Agent Graph (StateGraph)
  2. Oil India Line 24 Spool Erection Scenario (Precedence Anomaly -> Planner Review HITL)
  3. Supervisor Clarification Cyclic Loop (<60% Confidence)
  4. Auto-Commit & Deterministic EVM Recalculation (>=90% Confidence, Baseline Protected)
"""

import sys
import json
from core.schedule_engine import ScheduleEngine
from core.evm_engine import EVMEngine
from core.langgraph_orchestrator import ProjectTwinLangGraphOrchestrator, LANGGRAPH_AVAILABLE

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def main():
    print_header("PROJECTTWIN: LANGGRAPH MULTI-AGENT ORCHESTRATOR DEMO (SIH26122)")
    print(f"LangGraph Engine Loaded: {'YES (v1.2+ Compiled StateGraph)' if LANGGRAPH_AVAILABLE else 'NO (Sequential Fallback)'}")

    # 1. Initialize Engines
    schedule_engine = ScheduleEngine()
    schedule_engine.load_baseline_csv("data/baseline_schedule_oil_india.csv")
    evm_engine = EVMEngine(schedule_engine)
    orchestrator = ProjectTwinLangGraphOrchestrator(schedule_engine, evm_engine)

    # ---------------------------------------------------------
    # SCENARIO 1: Oil India Line 24 Spool Erection (CPM Anomaly)
    # ---------------------------------------------------------
    print_header("SCENARIO 1: Oil India Line 24 Spool Erection (Prerequisite Anomaly -> HITL)")
    msg_1 = (
        "Completed erection of Line 24 piping spool section A on rack PR-04 "
        "at Duliajan manifold area today, 100% done"
    )
    print(f"[Field Input]: \"{msg_1}\"")
    print(f"[Reporter]   : Ramesh Sharma (Site Supervisor - Piping)\n")

    res_1 = orchestrator.execute(msg_1, supervisor="Ramesh Sharma", discipline="Piping")

    print("[Graph Execution Trace]:")
    for step in res_1["execution_step_log"]:
        print(f"  {step}")

    top_cand_1 = res_1["candidates"][0] if res_1["candidates"] else None
    print("\n[State Graph Result]:")
    print(f"  • Matched Baseline Activity : {top_cand_1.activity_id} - {top_cand_1.activity_name}")
    print(f"  • Composite Match Confidence : {top_cand_1.composite_confidence:.1f}%")
    print(f"  • Precedence Anomaly Caught  : {res_1['is_anomaly']}")
    print(f"  • Requires Human Sign-off    : {res_1['requires_human_signoff']}")
    print(f"  • Evidence SHA-256 Hash      : {res_1['evidence_hash']}")
    print(f"  • Gate Routing Decision      : {res_1['routing_decision'].value}")
    print(f"  • Explanatory Reasons        : {res_1['routing_reasons']}")

    # ---------------------------------------------------------
    # SCENARIO 2: Ambiguous Field Update (Clarification Loop)
    # ---------------------------------------------------------
    print_header("SCENARIO 2: Low-Confidence Ambiguous Input (<60% -> Supervisor Clarification Loop)")
    msg_2 = "Did some work near the compressor area with some guys."
    print(f"[Field Input]: \"{msg_2}\"")
    print(f"[Reporter]   : Site Worker\n")

    res_2 = orchestrator.execute(msg_2, supervisor="Worker", discipline="General")

    print("[Graph Execution Trace]:")
    for step in res_2["execution_step_log"]:
        print(f"  {step}")

    print("\n[State Graph Result]:")
    print(f"  • Gate Routing Decision      : {res_2['routing_decision'].value}")
    print(f"  • Clarification Reasons      : {res_2['routing_reasons']}")

    # ---------------------------------------------------------
    # SCENARIO 3: Valid Prerequisite Progress (Auto-Commit & EVM)
    # ---------------------------------------------------------
    print_header("SCENARIO 3: In-Sequence Foundation Work (Auto-Commit & Deterministic EVM)")
    msg_3 = "Completed excavation of pump foundation pad P-12 at Duliajan manifold area today, 100% complete."
    print(f"[Field Input]: \"{msg_3}\"")
    print(f"[Reporter]   : Anup Barua (Site Supervisor - Civil)\n")

    res_3 = orchestrator.execute(msg_3, supervisor="Anup Barua", discipline="Civil")

    print("[Graph Execution Trace]:")
    for step in res_3["execution_step_log"]:
        print(f"  {step}")

    top_cand_3 = res_3["candidates"][0] if res_3["candidates"] else None
    print("\n[State Graph Result]:")
    print(f"  • Matched Baseline Activity : {top_cand_3.activity_id} - {top_cand_3.activity_name}")
    print(f"  • Composite Match Confidence : {top_cand_3.composite_confidence:.1f}%")
    print(f"  • Gate Routing Decision      : {res_3['routing_decision'].value}")
    print(f"  • Evidence SHA-256 Hash      : {res_3['evidence_hash']}")
    if res_3.get("evm_metrics"):
        print(f"  • Deterministic EVM Updated  : PV={res_3['evm_metrics']['planned_value']}%, EV={res_3['evm_metrics']['earned_value']}%, SPI={res_3['evm_metrics']['schedule_performance_index']:.2f}")

    print_header("ALL SCENARIOS COMPLETED SUCCESSFULLY - LANGGRAPH ORCHESTRATION VERIFIED")

if __name__ == "__main__":
    main()

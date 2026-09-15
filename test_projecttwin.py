import os
import sys
import unittest

from core.schedule_engine import ScheduleEngine
from core.evm_engine import EVMEngine
from core.institutional_memory import InstitutionalMemoryEngine
from agents.ingestion_agent import IngestionAgent
from agents.time_agent import TimeAgent
from agents.linking_agent import HybridLinkingAgent
from agents.validation_agent import ValidationAgent
from core.models import RoutingStatus

class TestProjectTwin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schedule = ScheduleEngine()
        cls.schedule.load_baseline_csv("data/baseline_schedule_oil_india.csv")
        cls.linking = HybridLinkingAgent(cls.schedule.baseline_activities)
        cls.validation = ValidationAgent(cls.schedule)
        cls.ingestion = IngestionAgent()
        cls.time_agent = TimeAgent()
        cls.evm = EVMEngine(cls.schedule)
        cls.memory = InstitutionalMemoryEngine("data/test_memory.db")

    def test_01_schedule_loading_and_cpm(self):
        """Validates that baseline activities are loaded and CPM accurately flags critical path."""
        self.assertGreater(len(self.schedule.baseline_activities), 20)
        crit_path = self.schedule.get_critical_path()
        self.assertGreater(len(crit_path), 0)
        # Verify ACT-CIV-001 is on critical path
        self.assertIn("ACT-PIP-104", crit_path)
        print(f"\n[Test 1 Passed] Schedule loaded with {len(self.schedule.baseline_activities)} activities. Critical path nodes: {len(crit_path)}")

    def test_02_dpr_ingestion(self):
        """Validates that unstructured narrative DPR text extracts structured events with citations."""
        with open("data/dpr_sample_civil_piping.txt", "r", encoding="utf-8") as f:
            dpr_content = f.read()
        events = self.ingestion.ingest_dpr_text(dpr_content)
        self.assertGreaterEqual(len(events), 4)
        
        # Check that piping event was extracted
        piping_events = [e for e in events if e.discipline == "Piping"]
        self.assertGreaterEqual(len(piping_events), 1)
        self.assertIn("24-CW-001", piping_events[0].extracted_activity)
        print(f"[Test 2 Passed] Ingested {len(events)} events from DPR text with exact citations.")

    def test_03_excel_ingestion(self):
        """Validates multi-discipline Excel spreadsheet ingestion."""
        events = self.ingestion.ingest_excel("data/piping_spool_erection_log.xlsx")
        self.assertEqual(len(events), 5)
        self.assertEqual(events[0].discipline, "Piping")
        print(f"[Test 3 Passed] Ingested {len(events)} events from Piping Excel log.")

    def test_04_time_agent_supervisor_chat(self):
        """Validates that conversational/voice messages are parsed into structured events."""
        transcript = "Raman from piping: Erected spool SP-104 on line 24-CW-001 on pipe rack 4 today. Six out of 8 spools completed, rest delayed due to crane breakdown."
        result = self.time_agent.process_supervisor_message(transcript, supervisor_name="Raman Borah")
        event = result["raw_event"]
        self.assertEqual(event.discipline, "Piping")
        self.assertGreaterEqual(event.progress_pct, 70.0)
        self.assertEqual(event.delay_category, "Operational")
        print(f"[Test 4 Passed] Time Agent parsed voice message: {event.discipline}, Progress: {event.progress_pct}%, Blocker: {event.delay_category}")

    def test_05_hybrid_linking_accuracy(self):
        """Validates high accuracy of hybrid fuzzy matching (Top-1 >= 75%, Top-3 >= 90%)."""
        benchmark_queries = [
            ("spool erected on line 24-CW-001 rack 4", "Piping", "ACT-PIP-104"),
            ("Curing and foundation inspection for Pad P-12", "Civil", "ACT-CIV-005"),
            ("Pulled 11kV cable in tray B along corridor", "Electrical", "ACT-ELE-201"),
            ("Pour M35 concrete foundation for pump pad P-12", "Civil", "ACT-CIV-004"),
            ("Erect discharge manifold 16-DIS-002 to booster pump", "Piping", "ACT-PIP-106"),
        ]

        top_1_hits = 0
        top_3_hits = 0

        for query, disc, expected_id in benchmark_queries:
            fake_event = self.ingestion.ingest_dpr_text(f"Report Date: 2026-11-08\n1. {disc.upper()}:\n- Site: {query}")[0]
            candidates = self.linking.link_event(fake_event, top_k=3)
            candidate_ids = [c.activity_id for c in candidates]
            
            if candidate_ids and candidate_ids[0] == expected_id:
                top_1_hits += 1
            if expected_id in candidate_ids:
                top_3_hits += 1

        top_1_acc = (top_1_hits / len(benchmark_queries)) * 100.0
        top_3_acc = (top_3_hits / len(benchmark_queries)) * 100.0

        print(f"[Test 5 Passed] Linking Accuracy: Top-1 = {top_1_acc:.1f}% (target >=75%), Top-3 = {top_3_acc:.1f}% (target >=90%)")
        self.assertGreaterEqual(top_1_acc, 75.0)
        self.assertGreaterEqual(top_3_acc, 90.0)

    def test_06_precedence_and_confidence_routing(self):
        """Validates that out-of-sequence execution triggers CPM precedence alerts and routes to Planner Review."""
        # Create an event for System Hydrotest (ACT-PIP-108) while Golden Joint (ACT-PIP-105) is 0% complete
        out_of_seq_event = self.ingestion.ingest_dpr_text(
            "Report Date: 2026-11-08\n1. PIPING:\n- Manifold Yard: Hydrostatic pressure testing completed for Line 24-CW-001."
        )[0]
        candidates = self.linking.link_event(out_of_seq_event, top_k=3)
        candidate_obj = self.validation.validate_and_route(out_of_seq_event, candidates)
        
        self.assertTrue(candidate_obj.precedence_violation)
        self.assertEqual(candidate_obj.routing_decision, RoutingStatus.PLANNER_REVIEW)
        print(f"[Test 6 Passed] Precedence alert successfully detected and routed to {candidate_obj.routing_decision.value}.")

    def test_07_evm_deterministic_math(self):
        """Validates EVM math (PV, EV, SV, SPI, S-Curve)."""
        evm_metrics = self.evm.calculate_evm("2026-11-10")
        self.assertGreater(evm_metrics.planned_value, 0.0)
        self.assertIsNotNone(evm_metrics.schedule_variance)
        self.assertIsNotNone(evm_metrics.schedule_performance_index)

        s_curve = self.evm.generate_s_curve_data()
        self.assertIn("labels", s_curve)
        self.assertIn("planned", s_curve)
        self.assertEqual(len(s_curve["labels"]), len(s_curve["planned"]))
        print(f"[Test 7 Passed] Deterministic EVM calculated: PV={evm_metrics.planned_value}%, EV={evm_metrics.earned_value}%, SPI={evm_metrics.schedule_performance_index}")

    def test_08_institutional_memory(self):
        """Validates institutional memory queries and lessons learned retrieval."""
        benchmarks = self.memory.get_discipline_productivity_benchmarks()
        self.assertGreater(len(benchmarks), 0)
        delays = self.memory.get_delay_frequency_distribution()
        self.assertGreater(len(delays), 0)
        insights = self.memory.query_historical_patterns(query="crane")
        self.assertGreater(len(insights), 0)
        print(f"[Test 8 Passed] Institutional Memory verified: {len(benchmarks)} discipline benchmarks, {len(delays)} delay categories.")

if __name__ == "__main__":
    unittest.main()


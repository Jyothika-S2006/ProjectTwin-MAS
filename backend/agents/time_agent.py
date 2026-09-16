import re
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from core.models import RawExecutionEvent

class TimeAgent:
    """
    LLM/NLP conversational and voice interface ('Time Agent') for site supervisors across disciplines.
    Translates colloquial speech/transcripts into structured RawExecutionEvents.
    """
    def __init__(self):
        self.discipline_keywords = {
            "Piping": ["spool", "line", "pipe", "welder", "golden joint", "hydrotest", "flange", "rack", "valve", "manifold"],
            "Civil": ["foundation", "concrete", "pour", "curing", "rebar", "shuttering", "excavation", "m35", "pad", "ring beam"],
            "Electrical": ["cable", "tray", "bedding", "11kv", "feeder", "mcc", "substation", "earthing", "power supply"],
            "Mechanical": ["booster pump", "tank", "grout", "motor", "alignment", "compressor", "equipment"],
            "Instrumentation": ["transmitter", "plc", "loop check", "calibration", "ultrasonic", "flow meter", "instrument"]
        }

    def process_supervisor_message(
        self,
        transcript: str,
        supervisor_name: str = "Site Supervisor",
        discipline_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes voice transcript or conversational chat message and extracts structured progress event.
        """
        text = transcript.strip()
        
        # 1. Infer Discipline
        inferred_discipline = discipline_hint or "General"
        if not discipline_hint or discipline_hint == "Auto-Detect":
            disc_scores = {}
            low_text = text.lower()
            for disc, kws in self.discipline_keywords.items():
                score = sum(1 for kw in kws if kw in low_text)
                if score > 0:
                    disc_scores[disc] = score
            if disc_scores:
                inferred_discipline = max(disc_scores, key=disc_scores.get)

        # 2. Infer Status & Progress Percentage
        progress_pct = 50.0
        status = "IN_PROGRESS"
        low = text.lower()
        
        pct_match = re.search(r"(\d{1,3})\s*(?:percent|%)", low)
        fraction_match = re.search(r"(\d+)\s*(?:out of|/)\s*(\d+)", low)
        
        if pct_match:
            progress_pct = float(pct_match.group(1))
        elif fraction_match:
            n = float(fraction_match.group(1))
            d = float(fraction_match.group(2))
            if d > 0:
                progress_pct = round((n / d) * 100.0, 1)
        elif "hundred percent" in low or "completed" in low or "finished" in low or "signed off" in low:
            progress_pct = 100.0
            status = "COMPLETED"
        elif "started" in low or "began" in low or "mobilized" in low:
            progress_pct = 15.0
            status = "IN_PROGRESS"

        if progress_pct >= 100.0:
            status = "COMPLETED"

        # 3. Detect Delay & Root Causes
        blocker = None
        delay_cat = "None"
        if any(w in low for w in ["breakdown", "rupture", "failed", "crane", "winch", "equipment problem"]):
            delay_cat = "Operational"
            blocker = "Equipment operational disruption reported by supervisor."
        elif any(w in low for w in ["gasket", "material", "warehouse", "store", "supply", "not arrived", "shortage"]):
            delay_cat = "Material"
            blocker = "Material delivery bottleneck or store issue."
        elif any(w in low for w in ["approval", "inspector", "qc sign", "permit", "ptw", "client signoff"]):
            delay_cat = "Approval"
            blocker = "Permit or inspection clearance latency."
        elif any(w in low for w in ["rain", "monsoon", "drizzle", "waterlogging", "weather", "mud"]):
            delay_cat = "Weather"
            blocker = "Adverse weather conditions."

        if delay_cat != "None":
            status = "DELAYED"

        # 4. Extract Key Engineering Identifiers (Lines, Tags, Pads)
        tag_match = re.search(r"(?:line\s*)?([0-9]{2}-[A-Z]{2,4}-[0-9]{3}|P-\d{2}|TK-\d{3}|PR-\d{2}|C-\d|MCC-\d{2}|FT-\d{3}|PT-\d{3})", text, re.IGNORECASE)
        tag = tag_match.group(1).upper() if tag_match else ""

        # 5. Formulate Clean RawExecutionEvent
        event_id = f"EVT-VOICE-{uuid.uuid4().hex[:8].upper()}"
        raw_event = RawExecutionEvent(
            event_id=event_id,
            source_type="VOICE_AGENT",
            source_reference=f"Voice Note from {supervisor_name}",
            event_date=datetime.now().strftime("%Y-%m-%d"),
            raw_text=text,
            discipline=inferred_discipline,
            extracted_activity=f"{tag} {inferred_discipline} execution: {text[:120]}...",
            reported_status=status,
            progress_pct=progress_pct,
            quantity_info=None,
            blocker=blocker,
            delay_category=delay_cat,
            supervisor=supervisor_name,
            text_citation=text
        )

        confirmation_card = {
            "supervisor": supervisor_name,
            "discipline": inferred_discipline,
            "inferred_tag": tag or "General",
            "status": status,
            "progress_pct": progress_pct,
            "blocker_detected": blocker is not None,
            "delay_category": delay_cat,
            "formatted_summary": f"{supervisor_name} reported {progress_pct}% on {inferred_discipline} ({status}). " + (f"Blocker: {blocker}" if blocker else "No active blocker.")
        }

        return {
            "raw_event": raw_event,
            "confirmation_card": confirmation_card
        }

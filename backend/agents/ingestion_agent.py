import re
import uuid
from typing import List, Dict, Any, Optional
from core.models import RawExecutionEvent

class IngestionAgent:
    def __init__(self):
        pass

    def ingest_dpr_text(self, text: str, source_name: str = "DPR #142") -> List[RawExecutionEvent]:
        """
        Parses narrative DPR text into structured RawExecutionEvent objects with exact citation spans.
        """
        events = []
        lines = text.strip().split("\n")
        
        current_discipline = "General"
        date_match = re.search(r"Report Date:\s*(\d{4}-\d{2}-\d{2})", text)
        event_date = date_match.group(1) if date_match else "2026-11-08"

        # Regex patterns for activity and discipline detection
        discipline_headers = {
            "CIVIL": "Civil",
            "PIPING": "Piping",
            "MECHANICAL": "Mechanical",
            "ELECTRICAL": "Electrical",
            "INSTRUMENTATION": "Instrumentation",
            "HSE": "HSE"
        }

        bullet_regex = re.compile(r"^[-*•]\s*(?:([A-Za-z0-9\s/]+):\s*)?(.*)")
        pct_regex = re.compile(r"(\d{1,3})\s*%")
        delay_regex = re.compile(r"\[DELAY-\d+\]\s*Category:\s*([A-Za-z]+)\s*\|\s*(.*)", re.IGNORECASE)

        active_blocker = None
        active_delay_cat = None

        # Extract delays first if present in notes
        for line in lines:
            m = delay_regex.search(line)
            if m:
                active_delay_cat = m.group(1)
                active_blocker = m.group(2).strip()

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Check for section discipline headers
            upper = line_str.upper()
            for k, disc in discipline_headers.items():
                if k in upper and ("DISCIPLINE" in upper or ":" in upper):
                    current_discipline = disc
                    break

            # Check for bullet progress entries
            m = bullet_regex.match(line_str)
            if m:
                area_prefix = m.group(1) or ""
                content = m.group(2).strip()
                if len(content) < 15:
                    continue

                # Detect status & progress
                progress_pct = None
                pct_m = pct_regex.search(content)
                if pct_m:
                    progress_pct = float(pct_m.group(1))

                status = "IN_PROGRESS"
                if "concluded" in content.lower() or "completed" in content.lower() or "cleared" in content.lower():
                    status = "COMPLETED"
                    progress_pct = progress_pct or 100.0
                elif "halted" in content.lower() or "stopped" in content.lower() or "breakdown" in content.lower():
                    status = "DELAYED"
                elif "started" in content.lower() or "mobilized" in content.lower():
                    status = "IN_PROGRESS"
                    progress_pct = progress_pct or 15.0

                # Check if this entry corresponds to the blocker
                blocker = None
                delay_cat = None
                if "crane" in content.lower() or "halted" in content.lower() or "delay" in content.lower():
                    blocker = active_blocker or "Equipment operational stoppage"
                    delay_cat = active_delay_cat or "Operational"

                # Extract quantity if present
                qty = None
                qty_m = re.search(r"(\d+\s*(?:spools|meters|m3|cubic meters|tons))", content, re.IGNORECASE)
                if qty_m:
                    qty = qty_m.group(1)

                evt = RawExecutionEvent(
                    event_id=f"EVT-DPR-{uuid.uuid4().hex[:8].upper()}",
                    source_type="DPR",
                    source_reference=f"{source_name} - {area_prefix or current_discipline}",
                    event_date=event_date,
                    raw_text=content,
                    discipline=current_discipline,
                    extracted_activity=f"{area_prefix}: {content}" if area_prefix else content,
                    reported_status=status,
                    progress_pct=progress_pct or (100.0 if status == "COMPLETED" else 50.0),
                    quantity_info=qty,
                    blocker=blocker,
                    delay_category=delay_cat,
                    supervisor="Site Engineer (DPR)",
                    text_citation=line_str
                )
                events.append(evt)

        return events

    def ingest_excel(self, filepath: str, discipline_hint: str = "General") -> List[RawExecutionEvent]:
        """
        Ingests multi-column discipline spreadsheets (.xlsx or .csv) using pure-Python openpyxl / csv.
        """
        import csv
        events = []
        rows = []

        if filepath.endswith(".xlsx") or filepath.endswith(".xls"):
            import openpyxl
            wb = openpyxl.load_workbook(filepath, data_only=True)
            sheet = wb.active
            headers = [str(cell.value or "").strip() for cell in sheet[1]]
            for r in sheet.iter_rows(min_row=2, values_only=True):
                if any(r):
                    row_dict = {}
                    for h, v in zip(headers, r):
                        if h:
                            row_dict[h] = "" if v is None else v
                    rows.append(row_dict)
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

        if not rows:
            return events

        # Standardize column headers
        col_map = {}
        first_row = rows[0]
        for col in first_row.keys():
            c_low = str(col).lower().replace(" ", "_")
            if "date" in c_low:
                col_map["date"] = col
            elif "activity" in c_low or "spool" in c_low or "foundation" in c_low:
                col_map["activity"] = col
            elif "status" in c_low:
                col_map["status"] = col
            elif "progress" in c_low or "pct" in c_low:
                col_map["progress"] = col
            elif "remark" in c_low or "note" in c_low:
                col_map["remarks"] = col
            elif "line" in c_low:
                col_map["line"] = col
            elif "location" in c_low or "rack" in c_low:
                col_map["location"] = col

        disc = discipline_hint
        if "piping" in filepath.lower():
            disc = "Piping"
        elif "civil" in filepath.lower():
            disc = "Civil"
        elif "elec" in filepath.lower():
            disc = "Electrical"

        for idx, row in enumerate(rows):
            row_date = str(row.get(col_map.get("date"), "2026-11-08"))
            act_desc = str(row.get(col_map.get("activity"), f"Activity on row {idx+1}"))
            line_no = str(row.get(col_map.get("line"), "")) if "line" in col_map else ""
            status_raw = str(row.get(col_map.get("status"), "IN_PROGRESS")).upper()
            remarks = str(row.get(col_map.get("remarks"), "")) if "remarks" in col_map else ""

            # Calculate progress
            prog_val = 50.0
            raw_prog = row.get(col_map.get("progress"))
            if raw_prog not in (None, ""):
                try:
                    prog_val = float(str(raw_prog).replace("%", "").strip())
                except ValueError:
                    prog_val = 50.0
            elif "completed" in status_raw.lower() or "erected & bolted" in status_raw.lower():
                prog_val = 100.0

            # Delay / Blocker parsing from remarks
            blocker = None
            delay_cat = None
            if "breakdown" in remarks.lower() or "crane" in remarks.lower():
                blocker = remarks
                delay_cat = "Operational"
            elif "waiting" in remarks.lower() or "shortage" in remarks.lower() or "gasket" in remarks.lower():
                blocker = remarks
                delay_cat = "Material"
            elif "rain" in remarks.lower():
                blocker = remarks
                delay_cat = "Weather"

            full_desc = f"{line_no} {act_desc}".strip()
            if remarks and remarks.lower() != "nan":
                full_desc += f" - {remarks}"

            evt = RawExecutionEvent(
                event_id=f"EVT-XLS-{uuid.uuid4().hex[:8].upper()}",
                source_type="EXCEL",
                source_reference=f"{filepath} (Row {idx+2})",
                event_date=row_date[:10] if len(row_date) >= 10 else "2026-11-08",
                raw_text=f"Status: {status_raw} | Activity: {act_desc} | Remarks: {remarks}",
                discipline=disc,
                extracted_activity=full_desc,
                reported_status=status_raw,
                progress_pct=prog_val,
                quantity_info=None,
                blocker=blocker,
                delay_category=delay_cat,
                supervisor="Spreadsheet Ingestion",
                text_citation=f"Row {idx+2}: {act_desc} -> {status_raw}"
            )
            events.append(evt)

        return events

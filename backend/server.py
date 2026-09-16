import os
import shutil
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.schedule_engine import ScheduleEngine
from core.evm_engine import EVMEngine
from core.institutional_memory import InstitutionalMemoryEngine
from agents.ingestion_agent import IngestionAgent
from agents.time_agent import TimeAgent
from agents.linking_agent import HybridLinkingAgent
from agents.validation_agent import ValidationAgent
from core.models import RoutingStatus

app = FastAPI(
    title="ProjectTwin API - Real-Time Actual Progress Tracking",
    description="Intelligent Data Capture & Schedule-Linking Layer for Infrastructure Projects (Oil India Limited / SIH26122)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dynamic resolution for data directory
if os.path.exists(os.path.join(BASE_DIR, "data")):
    data_dir = os.path.join(BASE_DIR, "data")
else:
    data_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))

# Dynamic resolution for frontend directory
if os.path.exists(os.path.join(BASE_DIR, "frontend")):
    frontend_dir = os.path.join(BASE_DIR, "frontend")
elif os.path.exists(os.path.join(BASE_DIR, "..", "frontend")):
    frontend_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
else:
    frontend_dir = os.path.join(BASE_DIR, "web")

static_dir = os.path.join(frontend_dir, "static") if os.path.exists(os.path.join(frontend_dir, "static")) else os.path.join(frontend_dir, "web", "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize Core Engines
schedule_engine = ScheduleEngine()
baseline_csv_path = os.path.join(data_dir, "baseline_schedule_oil_india.csv")
if os.path.exists(baseline_csv_path):
    schedule_engine.load_baseline_csv(baseline_csv_path)

linking_agent = HybridLinkingAgent(schedule_engine.baseline_activities)
validation_agent = ValidationAgent(schedule_engine)
ingestion_agent = IngestionAgent()
time_agent = TimeAgent()
evm_engine = EVMEngine(schedule_engine)
memory_engine = InstitutionalMemoryEngine(os.path.join(data_dir, "projecttwin_memory.db"))

# Models for API
class TimeAgentRequest(BaseModel):
    message: str
    supervisor_name: str = "Site Supervisor"
    discipline: Optional[str] = "Auto-Detect"

class MatchQueryRequest(BaseModel):
    query: str
    discipline: Optional[str] = "General"

class PlannerResolveRequest(BaseModel):
    candidate_id: str
    selected_activity_id: str
    action: str = "ACCEPT"  # ACCEPT, REJECT, MODIFY
    planner_name: str = "R. Sharma (Lead Planner)"
    notes: str = "Verified with physical inspection report"

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    index_file = os.path.join(frontend_dir, "index.html")
    if not os.path.exists(index_file):
        index_file = os.path.join(frontend_dir, "templates", "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>ProjectTwin API Running</h1>")

@app.get("/api/schedule")
async def get_schedule():
    """Returns baseline activities, actual progress states, and CPM statistics."""
    summary = schedule_engine.get_summary()
    activities = []
    for act_id, base in schedule_engine.baseline_activities.items():
        actual = schedule_engine.actual_states.get(act_id)
        activities.append({
            "activity_id": base.activity_id,
            "wbs_code": base.wbs_code,
            "wbs_level": base.wbs_level,
            "activity_name": base.activity_name,
            "discipline": base.discipline,
            "planned_start": base.planned_start,
            "planned_finish": base.planned_finish,
            "planned_duration_days": base.planned_duration_days,
            "predecessors": base.predecessors,
            "weightage": base.weightage,
            "unit_area": base.unit_area,
            "is_critical": base.is_critical,
            "total_float": base.total_float,
            # Actuals
            "actual_start": actual.actual_start if actual else None,
            "actual_finish": actual.actual_finish if actual else None,
            "progress_pct": actual.progress_pct if actual else 0.0,
            "evidence_progress_pct": actual.evidence_progress_pct if actual else 0.0,
            "status": actual.status.value if actual else "NOT_STARTED",
            "evidence_sources": actual.evidence_sources if actual else [],
            "delay_reasons": actual.delay_reasons if actual else [],
            "blocker_category": actual.blocker_category if actual else None,
            "last_updated": actual.last_updated if actual else ""
        })
    return {
        "summary": summary,
        "activities": activities
    }

@app.get("/api/analytics/evm")
async def get_evm_analytics():
    """Returns deterministic EVM metrics (PV, EV, SV, SPI) and S-Curve coordinate series."""
    evm = evm_engine.calculate_evm("2026-11-10")
    s_curve = evm_engine.generate_s_curve_data()
    return {
        "metrics": evm.model_dump(),
        "s_curve": s_curve
    }

@app.post("/api/time-agent/message")
async def process_time_agent_message(req: TimeAgentRequest):
    """Processes conversational or voice update from site supervisor."""
    parsed = time_agent.process_supervisor_message(
        transcript=req.message,
        supervisor_name=req.supervisor_name,
        discipline_hint=req.discipline
    )
    event = parsed["raw_event"]
    candidates = linking_agent.link_event(event, top_k=3)
    candidate_obj = validation_agent.validate_and_route(event, candidates)

    return {
        "confirmation_card": parsed["confirmation_card"],
        "extracted_event": event.model_dump(),
        "top_candidates": [c.model_dump() for c in candidates],
        "routing_decision": candidate_obj.routing_decision.value,
        "routing_reasons": candidate_obj.routing_reasons,
        "status": candidate_obj.status
    }

@app.post("/api/linking/match")
async def match_text(req: MatchQueryRequest):
    """Fuzzy-matches freeform site text to L5/L6 baseline schedule nodes."""
    from core.models import RawExecutionEvent
    dummy_event = RawExecutionEvent(
        event_id="TEST-QUERY",
        source_type="MANUAL_QUERY",
        source_reference="Live Inspector",
        event_date=datetime.now().strftime("%Y-%m-%d"),
        raw_text=req.query,
        discipline=req.discipline or "General",
        extracted_activity=req.query,
        reported_status="IN_PROGRESS",
        text_citation=req.query
    )
    candidates = linking_agent.link_event(dummy_event, top_k=3)
    return {
        "query": req.query,
        "discipline": req.discipline,
        "candidates": [c.model_dump() for c in candidates]
    }

@app.get("/api/planner/queue")
async def get_planner_queue():
    """Returns all pending and committed schedule update candidates."""
    res = []
    for cand in validation_agent.pending_candidates.values():
        res.append(cand.model_dump())
    return {"queue": res}

@app.post("/api/planner/resolve")
async def resolve_planner_candidate(req: PlannerResolveRequest):
    """Allows human planner to review, resolve, and commit an update."""
    try:
        updated = validation_agent.resolve_planner_candidate(
            candidate_id=req.candidate_id,
            selected_act_id=req.selected_activity_id,
            action=req.action,
            planner_name=req.planner_name,
            notes=req.notes
        )
        return {"status": "SUCCESS", "candidate": updated.model_dump()}
    except KeyError:
        raise HTTPException(status_code=404, detail="Candidate ID not found.")

@app.post("/api/ingest/dpr")
async def ingest_dpr(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Ingests narrative DPR text or uploaded file, extracts events, and routes to schedule."""
    content = ""
    source_name = "DPR Upload"
    if file and file.filename:
        source_name = file.filename
        raw_bytes = await file.read()
        content = raw_bytes.decode("utf-8", errors="ignore")
    elif text:
        content = text
    else:
        raise HTTPException(status_code=400, detail="Provide either text or file.")

    events = ingestion_agent.ingest_dpr_text(content, source_name=source_name)
    processed_candidates = []
    for evt in events:
        candidates = linking_agent.link_event(evt, top_k=3)
        candidate_obj = validation_agent.validate_and_route(evt, candidates)
        processed_candidates.append(candidate_obj.model_dump())

    return {
        "source": source_name,
        "events_count": len(events),
        "candidates": processed_candidates
    }

@app.post("/api/ingest/excel")
async def ingest_excel(file: UploadFile = File(...), discipline: str = Form("General")):
    """Ingests multi-tab discipline Excel sheet (.xlsx / .csv)."""
    temp_path = os.path.join(data_dir, f"temp_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        events = ingestion_agent.ingest_excel(temp_path, discipline_hint=discipline)
        processed_candidates = []
        for evt in events:
            candidates = linking_agent.link_event(evt, top_k=3)
            candidate_obj = validation_agent.validate_and_route(evt, candidates)
            processed_candidates.append(candidate_obj.model_dump())
        return {
            "filename": file.filename,
            "discipline": discipline,
            "events_count": len(events),
            "candidates": processed_candidates
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/api/memory/benchmarks")
async def get_memory_benchmarks():
    """Returns discipline productivity benchmarks and delay taxonomy."""
    benchmarks = memory_engine.get_discipline_productivity_benchmarks()
    delays = memory_engine.get_delay_frequency_distribution()
    return {
        "benchmarks": benchmarks,
        "delays": delays
    }

@app.get("/api/memory/query")
async def query_memory(q: str = "", discipline: Optional[str] = "all"):
    """Queries institutional memory for historical project patterns and lessons."""
    records = memory_engine.query_historical_patterns(query=q, discipline=discipline)
    return {"records": records}

@app.get("/api/audit/logs")
async def get_audit_logs():
    """Returns immutable evidence audit trail with SHA256 hashes."""
    return {"audit_logs": [entry.model_dump() for entry in validation_agent.audit_log]}

@app.post("/api/demo/load-all")
async def load_all_sample_data():
    """Loads all Oil India realistic sample datasets and runs the complete multi-agent pipeline."""
    # 1. Re-initialize baseline
    schedule_engine.load_baseline_csv(baseline_csv_path)
    linking_agent.__init__(schedule_engine.baseline_activities)
    validation_agent.pending_candidates.clear()
    validation_agent.audit_log.clear()

    # 2. Ingest DPR
    dpr_file = os.path.join(data_dir, "dpr_sample_civil_piping.txt")
    with open(dpr_file, "r", encoding="utf-8") as f:
        dpr_events = ingestion_agent.ingest_dpr_text(f.read(), source_name="Oil India DPR #142")
    for evt in dpr_events:
        cands = linking_agent.link_event(evt, top_k=3)
        validation_agent.validate_and_route(evt, cands)

    # 3. Ingest Piping Excel
    piping_xls = os.path.join(data_dir, "piping_spool_erection_log.xlsx")
    piping_events = ingestion_agent.ingest_excel(piping_xls, discipline_hint="Piping")
    for evt in piping_events:
        cands = linking_agent.link_event(evt, top_k=3)
        validation_agent.validate_and_route(evt, cands)

    # 4. Ingest Civil Excel
    civil_xls = os.path.join(data_dir, "civil_foundation_log.xlsx")
    civil_events = ingestion_agent.ingest_excel(civil_xls, discipline_hint="Civil")
    for evt in civil_events:
        cands = linking_agent.link_event(evt, top_k=3)
        validation_agent.validate_and_route(evt, cands)

    # 5. Ingest Supervisor Voice Transcripts
    import json
    voice_file = os.path.join(data_dir, "supervisor_voice_transcripts.json")
    with open(voice_file, "r", encoding="utf-8") as f:
        voice_items = json.load(f)
    for v in voice_items:
        res = time_agent.process_supervisor_message(v["transcript"], supervisor_name=v["supervisor"], discipline_hint=v["discipline"])
        evt = res["raw_event"]
        cands = linking_agent.link_event(evt, top_k=3)
        validation_agent.validate_and_route(evt, cands)

    summary = schedule_engine.get_summary()
    evm = evm_engine.calculate_evm("2026-11-10")

    return {
        "status": "SUCCESS",
        "message": "Oil India Limited sample datasets loaded & processed successfully.",
        "summary": summary,
        "evm": evm.model_dump(),
        "total_candidates": len(validation_agent.pending_candidates),
        "audit_entries": len(validation_agent.audit_log)
    }


# -------------------- AUTHENTICATION & ROLE-BASED ACCESS --------------------
USERS_DB = {
    "planner@oilindia.in": {
        "email": "planner@oilindia.in",
        "password": "admin123",
        "name": "R. Sharma",
        "role": "ADMIN_PLANNER",
        "title": "Lead Project Planner",
        "discipline": "Project Controls",
        "badge": "Admin / Planner",
        "permissions": ["all", "approve_queue", "modify_actuals", "export_reports"]
    },
    "supervisor@oilindia.in": {
        "email": "supervisor@oilindia.in",
        "password": "site123",
        "name": "Raman Borah",
        "role": "SITE_SUPERVISOR",
        "title": "Piping Field Supervisor",
        "discipline": "Piping",
        "badge": "Worker / Supervisor",
        "permissions": ["voice_agent", "ingest_logs", "view_schedule"]
    },
    "civil@oilindia.in": {
        "email": "civil@oilindia.in",
        "password": "site123",
        "name": "Debojit Saikia",
        "role": "SITE_SUPERVISOR",
        "title": "Civil Section Engineer",
        "discipline": "Civil",
        "badge": "Worker / Supervisor",
        "permissions": ["voice_agent", "ingest_logs", "view_schedule"]
    },
    "director@oilindia.in": {
        "email": "director@oilindia.in",
        "password": "oil2026",
        "name": "Dr. P. K. Goswami",
        "role": "EXECUTIVE_AUDITOR",
        "title": "Executive Project Director",
        "discipline": "Management",
        "badge": "Executive / OIL HQ",
        "permissions": ["view_cockpit", "view_s_curve", "view_audit", "query_memory"]
    }
}

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/login")
async def login_user(req: LoginRequest):
    user = USERS_DB.get(req.email.strip().lower())
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials. Check demo accounts.")
    return {
        "status": "SUCCESS",
        "user": {
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "title": user["title"],
            "discipline": user["discipline"],
            "badge": user["badge"],
            "permissions": user["permissions"]
        }
    }

@app.get("/api/auth/accounts")
async def get_demo_accounts():
    """Returns pre-configured login credentials for demonstration."""
    return {
        "accounts": [
            {"email": u["email"], "password": u["password"], "role": u["role"], "badge": u["badge"], "name": u["name"], "title": u["title"]}
            for u in USERS_DB.values()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

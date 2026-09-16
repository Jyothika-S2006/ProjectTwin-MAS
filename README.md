# ProjectTwin: Intelligent Data Capture & Schedule-Linking Layer
### Smart India Hackathon 2026 | Problem Statement ID: SIH26122
**Organization**: Oil India Limited  
**Category**: Software | **Theme**: Smart Automation  
**Team**: SentinelX3.0  
**Pitch**: *From Fragmented Field Updates to Trusted Project Intelligence*

---

## 1. Problem Overview
Infrastructure project schedules cascade from macro milestones (L1) down to micro, executable activities (L5/L6), spanning multiple engineering disciplines: **Civil, Piping, Mechanical, Electrical, Instrumentation, and HSE**.

While the baseline plan is defined in Primavera P6 or MS Project, actual execution flows through unstructured Daily Progress Reports (DPRs), site diaries, discipline spreadsheets, and verbal supervisor messages. Because site descriptions use field jargon (e.g., *"spool erected on rack 4"*) rather than formal WBS codes (e.g., *"Erect Line 24"-CW-001 Spool on Pipe Rack PR-04"*), project management suffers from:
- **Severe Reconciliation Latency**: Schedule updates lag by days or weeks.
- **Data Fragmentation & Blind Progress**: Unverified progress claims and untracked bottlenecks.
- **Loss of Institutional Memory**: What actually happened (real durations, delays, productivity) is forgotten once projects close.

---

## 2. Core Innovations in ProjectTwin
1. **Supervisor-Orchestrated Multi-Agent Pipeline**:
   - **Ingestion Agent**: Collects narrative DPRs, multi-tab discipline Excel spreadsheets, and audio logs.
   - **Time Agent**: Conversational/voice interface for site supervisors to report progress with zero friction.
   - **Hybrid Linking Agent**: BM25 keyword matching + RapidFuzz syntactic token sets + sub-word character n-gram TF-IDF cosine similarity + engineering metadata boosting.
   - **Validation & Logic Checks Agent**: Validates CPM precedence logic, detects cross-source contradictions, enforces confidence-based routing, and generates evidence-bound audit trails.
2. **Controlled Intelligence & Protected Baseline**:
   - The Primavera P6 baseline schedule is strictly immutable.
   - Progress is committed to an **Actuals Progress Layer** tied to baseline nodes with SHA-256 evidence hashes.
3. **Deterministic Progress & EVM Math**:
   - Earned Value Management ($PV, EV, SPI, SV$) and S-Curve mathematics are calculated with deterministic Python algorithms (zero LLM hallucination).
4. **Institutional Memory Knowledge Base**:
   - SQLite-backed repository capturing real execution patterns, delay root causes (Material, Operational, Approval, Weather), and discipline-specific productivity factors.

---

## 3. Decoupled Architecture: Frontend & Backend Separation

The repository is organized into cleanly decoupled layers for modularity, independent scalability, and ease of hackathon portal submission:

```
ProjectTwin-MAS/
├── frontend/                     # Pure Client UI & Command Center Layer
│   ├── index.html                # Industrial Black & Gold Command Center
│   ├── static/
│   │   ├── css/style.css         # Minimalist theme, animations, dark mode
│   │   └── js/app.js             # RBAC auth, EVM charts, speech & API client
│   └── README.md                 # Frontend architecture and hosting instructions
│
├── backend/                      # Intelligence, Core Engines & Multi-Agent Layer
│   ├── agents/                   # Ingestion, Time, Linking, and Validation Agents
│   ├── core/                     # CPM DAG solver, EVM Engine, Institutional Memory
│   ├── data/                     # Oil India Primavera P6 baseline, DPRs, Excel logs
│   ├── server.py                 # FastAPI REST API & WebSocket handlers
│   ├── run.py                    # Standalone backend launcher
│   ├── test_projecttwin.py       # Comprehensive 12-suite automated test runner
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Backend technical specs & math models
│
├── run.py                        # Root convenience launcher (starts server & opens UI)
├── requirements.txt              # Root dependency reference
└── README.md                     # Main repository documentation
```

---

## 4. Confidence-Based Decision Routing
| Confidence Score | Conflict / Precedence Anomaly | Action Taken |
| :--- | :--- | :--- |
| $\ge 90\%$ | No Conflicts | **Auto-Soft-Update Queue** (Committed immediately) |
| $60\% - 89\%$ | Yes or No | **Planner Review Queue** (Human-in-the-loop signoff) |
| $< 60\%$ | &mdash; | **Supervisor Clarification Queue** (Clarification requested) |

---

## 5. Quick Start & Execution

### Run the Server & Interactive Web Command Center
```bash
# Run launcher with auto-browser launch
uv run python run.py

# Or directly with uvicorn
uv run python -m uvicorn server:app --host 127.0.0.1 --port 8000
```
Open your browser at: `http://127.0.0.1:8000`

### Run the Backend Test Suite
```bash
uv run python test_projecttwin.py
# Or inside backend:
cd backend && uv run python test_projecttwin.py
```

---

## 5. Demonstration Workflow for Evaluators
1. **Open the Executive Cockpit**:
   - Click **"Load Oil India Demo Dataset"** in the top bar.
   - Observe real-time EVM calculations: Planned Value (PV), Evidence Earned (EV), Claimed Progress, SPI, and Critical Path Slippage.
   - Inspect the interactive **Deterministic S-Curve** and **Progress Integrity Bar** (Claimed vs Evidence-Supported).
2. **Supervisor "Time Agent"**:
   - Switch to the **Supervisor "Time Agent"** tab.
   - Click one of the simulation presets (e.g. *Piping: Raman Borah* or *Civil: Debojit Saikia*) or click **"Simulate Voice Recording"**.
   - Click **"Process & Auto-Link Event"**.
   - Inspect structured extraction (Discipline, Status %, Blocker, Suggested Schedule Node, and Routing Decision).
3. **Multi-Format Ingestion**:
   - Switch to **Multi-Format Ingestion**.
   - Click **"Load Sample DPR #142"** and click **"Parse & Extract Events"**.
   - Review how narrative text is parsed into discipline-wise events with verbatim citation spans.
4. **Hybrid Linking Visualizer**:
   - Switch to **Hybrid Linking Visualizer**.
   - Type any colloquial site phrase (e.g., *"hung spool on rack 4"* or *"poured footing P-12"*) and select discipline.
   - View top-3 matches with individual metric dials: RapidFuzz, BM25, TF-IDF Cosine, and Domain Boost.
5. **Planner Review Queue**:
   - Switch to **Planner Review Queue**.
   - Review items flagged for medium confidence, precedence violations, or contradictions.
   - Click **"Accept"** or **"Reject"** to test human-in-the-loop decision-making.
6. **Institutional Memory & Audit Trail**:
   - Inspect historical delay distributions and discipline productivity factors.
   - Query past project lessons (e.g. search *"crane"* or *"gasket"*).
   - View the **Protected Baseline Audit Trail** showing SHA-256 evidence hashes and diff summaries.

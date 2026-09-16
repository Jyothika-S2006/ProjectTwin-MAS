# ProjectTwin - Backend Architecture & Intelligence Layer

### Problem Statement: SIH26122 | Oil India Limited | Team SentinelX3.0

The ProjectTwin Backend is a deterministic, multi-agent execution tracking and Earned Value Management (EVM) engine designed to bridge Primavera P6 baseline schedules with unstructured field reality.

---

## 1. Multi-Agent System (MAS) Components

1. **Ingestion Agent (`backend/agents/ingestion_agent.py`)**:
   - Parses multi-tab discipline Excel spreadsheets (`piping_spool_erection_log.xlsx`, `civil_foundation_log.xlsx`).
   - Extracts structured work packages from narrative Daily Progress Reports (DPRs).
   - Ingests audio logs and voice transcripts.

2. **Time Agent (`backend/agents/time_agent.py`)**:
   - Converts natural language voice memos and site chat messages into structured `ProgressObservationEvent` schemas.
   - Extracts activity references, percentage completions, physical quantities, and blocker tags.

3. **Hybrid Linking Agent (`backend/agents/linking_agent.py`)**:
   - Sub-word character n-gram TF-IDF vectorizer + Cosine Similarity.
   - RapidFuzz token-set syntactic matching.
   - Engineering metadata boosting (Discipline alignment, unit area matching, WBS hierarchy).
   - Delivers sub-50ms query latency without heavy external C-extensions.

4. **Validation & Logic Checks Agent (`backend/agents/validation_agent.py`)**:
   - Evaluates Critical Path Method (CPM) precedence DAG logic.
   - Identifies cross-source progress contradictions.
   - Routes updates into three confidence gates:
     - **$\ge 90\%$**: Auto-Soft-Update (Automated baseline actuals update)
     - **$60\% - 89\%$**: Planner Review Queue (Human-in-the-loop signoff)
     - **$< 60\%$**: Supervisor Clarification Queue (Re-query site)

---

## 2. Core Engines

- **`backend/core/schedule_engine.py`**:
  - Topological sort, CPM early/late date forward/backward passes, total float computation.
  - Strictly protected, immutable Primavera P6 baseline layer with SHA-256 evidence hashing.
- **`backend/core/evm_engine.py`**:
  - Deterministic $PV, EV, SV, SPI$ mathematics (zero LLM hallucinations).
  - S-Curve coordinate generator.
- **`backend/core/institutional_memory.py`**:
  - SQLite database tracking delay root causes, historical execution durations, and productivity multipliers.

---

## 3. API Endpoints

| Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves frontend Command Center UI |
| `GET` | `/api/schedule` | Baseline activities, actual progress states, and CPM statistics |
| `GET` | `/api/analytics/evm` | Deterministic EVM metrics ($PV, EV, SV, SPI$) & S-Curve points |
| `POST`| `/api/time-agent/message` | Supervisor voice/conversational progress ingestion |
| `POST`| `/api/linking/query` | Test matching engine on raw field strings |
| `GET` | `/api/planner/pending-queue` | Retrieves events queued for human planner review |
| `POST`| `/api/planner/resolve` | Planner signoff (Accept / Reject / Modify) |
| `GET` | `/api/memory/delays` | Institutional delay analytics by category |

---

## 4. How to Run

```bash
# Run standalone server
uv run python -m uvicorn server:app --host 127.0.0.1 --port 8000

# Or execute root launcher
uv run python run.py

# Run test suite
uv run python test_projecttwin.py
```

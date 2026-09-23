# ProjectTwin - Frontend Client (Command Center)

### Problem Statement: SIH26122 | Oil India Limited | Team SentinelX3.0

The ProjectTwin Frontend is an industrial **Black & Gold minimalist** dashboard designed for enterprise project intelligence, schedule reconciliation, and field data capture.

---

## Features
1. **Protected Baseline Visibility**: Real-time view of 27 Primavera P6 WBS activities (L1–L6) across Civil, Piping, Mechanical, and Electrical disciplines.
2. **Deterministic EVM & S-Curve Analytics**: Interactive Chart.js charts rendering Planned Value ($PV$), Earned Value ($EV$), Schedule Variance ($SV$), and Schedule Performance Index ($SPI$).
3. **Site Supervisor Quick Entry**: Conversational voice & text input for immediate field updates.
4. **Planner Review Queue**: Human-in-the-loop decision interface for low/medium-confidence linking events.
5. **Role-Based Authentication (RBAC)**:
   - **Lead Planner (Admin)**: `planner@oilindia.in` / `admin123`
   - **Site Supervisor (Worker)**: `supervisor@oilindia.in` / `site123`
   - **Executive Director**: `director@oilindia.in` / `oil2026`

---

## Directory Structure
```
frontend/
├── index.html            # Main Command Center UI
├── static/
│   ├── css/
│   │   └── style.css     # Black & Gold matte design system
│   └── js/
│       └── app.js        # Dynamic state, EVM charts, and API client
└── README.md             # Frontend guide
```

---

## How to Run & Deploy
### Option 1: Live Demo Link
The live system is currently running at:
👉 **[https://split-stem-award-hispanic.trycloudflare.com](https://split-stem-award-hispanic.trycloudflare.com)**

### Option 2: Live with Local ProjectTwin Backend
When the FastAPI backend is running (`uv run python -m uvicorn server:app`), the frontend is served directly at:
```
http://127.0.0.1:8000/
```

### Option 3: Standalone Static Hosting (Netlify / GitHub Pages)
Because the frontend is pure HTML5, CSS3, and modern JavaScript:
- Drag and drop this `frontend/` folder directly into https://app.netlify.com/drop
- Or open `index.html` directly in your web browser.

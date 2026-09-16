// ProjectTwin Standalone Netlify Edition (Zero Backend Required)
// Team SentinelX3.0 / SIH26122 - Oil India Limited

const BASELINE_ACTIVITIES = [
  { activity_id: "ACT-CIV-001", wbs_level: "L5", wbs_code: "1.1.1", activity_name: "Clear Site and Mobilize Excavation Equipment", discipline: "Civil", planned_start: "2026-10-01", planned_finish: "2026-10-05", planned_duration_days: 5, predecessors: [], weightage: 2.0, unit_area: "Tank Farm Area" },
  { activity_id: "ACT-CIV-002", wbs_level: "L5", wbs_code: "1.1.2", activity_name: "Excavation and Soil Compaction for Pump House Foundation", discipline: "Civil", planned_start: "2026-10-06", planned_finish: "2026-10-14", planned_duration_days: 9, predecessors: ["ACT-CIV-001"], weightage: 4.5, unit_area: "Pump House" },
  { activity_id: "ACT-CIV-003", wbs_level: "L6", wbs_code: "1.1.3", activity_name: "Rebar Binding and Shuttering for Foundation Pad P-12", discipline: "Civil", planned_start: "2026-10-15", planned_finish: "2026-10-21", planned_duration_days: 7, predecessors: ["ACT-CIV-002"], weightage: 3.5, unit_area: "Pump House" },
  { activity_id: "ACT-CIV-004", wbs_level: "L6", wbs_code: "1.1.4", activity_name: "Pour M35 Reinforced Concrete for Foundation Pad P-12", discipline: "Civil", planned_start: "2026-10-22", planned_finish: "2026-10-25", planned_duration_days: 4, predecessors: ["ACT-CIV-003"], weightage: 4.0, unit_area: "Pump House" },
  { activity_id: "ACT-CIV-005", wbs_level: "L5", wbs_code: "1.1.5", activity_name: "Curing and Foundation Inspection Pad P-12", discipline: "Civil", planned_start: "2026-10-26", planned_finish: "2026-11-02", planned_duration_days: 8, predecessors: ["ACT-CIV-004"], weightage: 2.0, unit_area: "Pump House" },
  { activity_id: "ACT-CIV-006", wbs_level: "L5", wbs_code: "1.2.1", activity_name: "Excavate and Cast Crude Storage Tank TK-101 Ring Beam Foundation", discipline: "Civil", planned_start: "2026-10-10", planned_finish: "2026-10-28", planned_duration_days: 19, predecessors: ["ACT-CIV-001"], weightage: 6.0, unit_area: "Tank Farm Area" },
  { activity_id: "ACT-CIV-007", wbs_level: "L6", wbs_code: "1.3.1", activity_name: "Excavate Underground Cable Trench Corridor C-1", discipline: "Civil", planned_start: "2026-10-16", planned_finish: "2026-10-24", planned_duration_days: 9, predecessors: ["ACT-CIV-001"], weightage: 2.5, unit_area: "Substation Yard" },
  { activity_id: "ACT-EQP-001", wbs_level: "L5", wbs_code: "2.1.1", activity_name: "Erect and Grout Main Crude Booster Pump P-101A on Pad P-12", discipline: "Mechanical", planned_start: "2026-11-03", planned_finish: "2026-11-10", planned_duration_days: 8, predecessors: ["ACT-CIV-005"], weightage: 5.0, unit_area: "Pump House" },
  { activity_id: "ACT-PIP-101", wbs_level: "L5", wbs_code: "3.1.1", activity_name: "Fabricate Line 24-CW-001 24-inch Crude Oil Pipe Spools", discipline: "Piping", planned_start: "2026-10-15", planned_finish: "2026-10-30", planned_duration_days: 16, predecessors: [], weightage: 4.0, unit_area: "Fab Yard" },
  { activity_id: "ACT-PIP-102", wbs_level: "L6", wbs_code: "3.1.2", activity_name: "NDT and Hydrotest Fabricated Spools for Line 24-CW-001", discipline: "Piping", planned_start: "2026-10-31", planned_finish: "2026-11-05", planned_duration_days: 6, predecessors: ["ACT-PIP-101"], weightage: 2.5, unit_area: "Fab Yard" },
  { activity_id: "ACT-PIP-103", wbs_level: "L5", wbs_code: "3.1.3", activity_name: "Install Pipe Rack Steel Support Module PR-04", discipline: "Piping", planned_start: "2026-10-20", planned_finish: "2026-10-30", planned_duration_days: 11, predecessors: ["ACT-CIV-002"], weightage: 3.0, unit_area: "Manifold Yard" },
  { activity_id: "ACT-PIP-104", wbs_level: "L6", wbs_code: "3.1.4", activity_name: "Erect Line 24-CW-001 Spool on Pipe Rack PR-04", discipline: "Piping", planned_start: "2026-11-06", planned_finish: "2026-11-16", planned_duration_days: 11, predecessors: ["ACT-PIP-102", "ACT-PIP-103"], weightage: 6.5, unit_area: "Manifold Yard", is_critical: true },
  { activity_id: "ACT-PIP-105", wbs_level: "L6", wbs_code: "3.1.5", activity_name: "Fit-up and Weld Golden Joint GJ-04 on Line 24-CW-001", discipline: "Piping", planned_start: "2026-11-17", planned_finish: "2026-11-22", planned_duration_days: 6, predecessors: ["ACT-PIP-104"], weightage: 3.0, unit_area: "Manifold Yard", is_critical: true },
  { activity_id: "ACT-PIP-106", wbs_level: "L5", wbs_code: "3.2.1", activity_name: "Erect Line 16-DIS-002 Discharge Manifold to Pump P-101A", discipline: "Piping", planned_start: "2026-11-11", planned_finish: "2026-11-20", planned_duration_days: 10, predecessors: ["ACT-EQP-001"], weightage: 4.5, unit_area: "Pump House" },
  { activity_id: "ACT-PIP-108", wbs_level: "L5", wbs_code: "3.3.1", activity_name: "System Hydrostatic Pressure Testing for Line 24-CW-001", discipline: "Piping", planned_start: "2026-11-23", planned_finish: "2026-11-28", planned_duration_days: 6, predecessors: ["ACT-PIP-105"], weightage: 4.0, unit_area: "Manifold Yard", is_critical: true },
  { activity_id: "ACT-ELE-201", wbs_level: "L5", wbs_code: "4.1.1", activity_name: "Lay Sand Bedding and Pull 11kV Power Feeder Cable in Cable Tray B", discipline: "Electrical", planned_start: "2026-10-25", planned_finish: "2026-11-05", planned_duration_days: 12, predecessors: ["ACT-CIV-007"], weightage: 4.0, unit_area: "Substation Yard" },
  { activity_id: "ACT-COM-501", wbs_level: "L4", wbs_code: "7.1.1", activity_name: "Integrated Hydrocarbon Pre-Commissioning and Loop Check", discipline: "Commissioning", planned_start: "2026-11-29", planned_finish: "2026-12-08", planned_duration_days: 10, predecessors: ["ACT-PIP-108"], weightage: 6.0, unit_area: "Plant Wide", is_critical: true }
];

let actualStates = {};
BASELINE_ACTIVITIES.forEach(a => {
  actualStates[a.activity_id] = {
    activity_id: a.activity_id,
    status: "NOT_STARTED",
    progress_pct: 0.0,
    evidence_progress_pct: 0.0,
    delay_reasons: [],
    last_updated: ""
  };
});

let pendingQueue = [];
let auditLogs = [];
let sCurveChart = null;
let delayChart = null;
let isRecording = false;

const voicePresets = [
  {
    name: "Raman Borah (Piping Lead)",
    discipline: "Piping",
    text: "Raman here from Piping. We completed spool erection on line 24-CW-001 up to spool SP-106 on rack 4. Out of 8 spools, 6 are erected and bolted. Remaining two cannot be lifted today because the 50-ton mobile crane hydraulic line ruptured. Crane mechanic is on site, expecting replacement hose by tomorrow 10 AM. Current progress roughly 75%."
  },
  {
    name: "Debojit Saikia (Civil Lead)",
    discipline: "Civil",
    text: "Civil supervisor Debojit reporting. Curing and final foundation inspection for Booster Pump Pad P-12 is 100% complete today. Client QC has signed off the test cube reports. Mechanical team can take over for pump positioning anytime from tomorrow."
  },
  {
    name: "Bikash Gogoi (Electrical Lead)",
    discipline: "Electrical",
    text: "Bikash from Electrical side. We pulled 240 meters of 11kV power cable in tray B along the trench corridor today. Total run is 500 meters, so progress is about 48%. Sand bedding was laid in the morning shift."
  },
  {
    name: "Anup Baruah (Piping Engineer)",
    discipline: "Piping",
    text: "Piping crew tried to start fit-up of pump discharge line 16-DIS-002, but the required 300# ANSI spiral wound gaskets have not arrived from store. Activity is stalled waiting for material clearance."
  }
];
﻿function showToast(title, message, isError = false) {
  const toast = document.getElementById("toast");
  const tTitle = document.getElementById("toast-title");
  const tBody = document.getElementById("toast-body");
  const tIcon = document.getElementById("toast-icon");
  if (!toast) return;

  tTitle.textContent = title;
  tBody.textContent = message;
  tIcon.innerHTML = isError
    ? `<svg class="w-5 h-5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`
    : `<svg class="w-5 h-5 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;

  toast.classList.remove("translate-y-24", "opacity-0");
  toast.classList.add("translate-y-0", "opacity-100");

  setTimeout(() => {
    toast.classList.remove("translate-y-0", "opacity-100");
    toast.classList.add("translate-y-24", "opacity-0");
  }, 4000);
}

function switchTab(tabName) {
  const tabs = ["cockpit", "time-agent", "ingestion", "linking", "planner", "memory", "audit"];
  tabs.forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    if (el) {
      if (t === tabName) {
        el.classList.remove("hidden");
      } else {
        el.classList.add("hidden");
      }
    }
  });

  document.querySelectorAll(".tab-btn").forEach(btn => {
    if (btn.getAttribute("onclick") && btn.getAttribute("onclick").includes(`'${tabName}'`)) {
      btn.classList.add("active");
      btn.classList.remove("text-slate-400");
    } else {
      btn.classList.remove("active");
      btn.classList.add("text-slate-400");
    }
  });
}

function initCharts() {
  const ctxS = document.getElementById("sCurveChart");
  if (ctxS) {
    sCurveChart = new Chart(ctxS, {
      type: "line",
      data: {
        labels: ["01-Oct", "10-Oct", "20-Oct", "01-Nov", "10-Nov", "20-Nov", "01-Dec", "08-Dec"],
        datasets: [
          {
            label: "Planned Value (PV Baseline %)",
            data: [0, 8, 22, 45, 54, 75, 92, 100],
            borderColor: "#a1a1aa",
            backgroundColor: "rgba(161, 161, 170, 0.04)",
            borderWidth: 2,
            tension: 0.35,
            fill: true,
            pointRadius: 3
          },
          {
            label: "Claimed Progress (% Self-Reported)",
            data: [0, 7, 21, 42, 48, null, null, null],
            borderColor: "#eab308",
            borderDash: [5, 5],
            borderWidth: 2,
            tension: 0.35,
            fill: false,
            pointRadius: 3
          },
          {
            label: "Earned Value (EV Evidence-Verified %)",
            data: [0, 6, 19, 36, 42, null, null, null],
            borderColor: "#d4af37",
            backgroundColor: "rgba(212, 175, 55, 0.12)",
            borderWidth: 3,
            tension: 0.35,
            fill: true,
            pointRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#94a3b8", font: { size: 11 } } }
        },
        scales: {
          x: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8", font: { size: 10 } } },
          y: { min: 0, max: 100, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8", font: { size: 10 }, callback: (v) => `${v}%` } }
        }
      }
    });
  }

  const ctxD = document.getElementById("delayChart");
  if (ctxD) {
    delayChart = new Chart(ctxD, {
      type: "doughnut",
      data: {
        labels: ["Operational (Crane Breakdown)", "Material (Gasket Shortage)", "Approval (QC Inspection)", "Weather (Monsoon Rain)"],
        datasets: [{
          data: [4, 3, 2, 2],
          backgroundColor: ["#d4af37", "#a16207", "#71717a", "#3f3f46"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom", labels: { color: "#94a3b8", font: { size: 10 } } } },
        cutout: "68%"
      }
    });
  }
}

function updateCockpit() {
  let totalWeight = 0;
  let pvAccum = 0;
  let evAccum = 0;
  let claimedAccum = 0;

  BASELINE_ACTIVITIES.forEach(a => {
    totalWeight += a.weightage;
    const actual = actualStates[a.activity_id] || { progress_pct: 0, evidence_progress_pct: 0 };
    pvAccum += (a.weightage * 54.0) / 100.0; // target 54% on Nov 10
    evAccum += (a.weightage * actual.evidence_progress_pct) / 100.0;
    claimedAccum += (a.weightage * actual.progress_pct) / 100.0;
  });

  const pv = 54.0;
  const ev = Math.round((evAccum / totalWeight) * 100.0 * 10) / 10;
  const claimed = Math.round((claimedAccum / totalWeight) * 100.0 * 10) / 10;
  const spi = pv > 0 ? (ev / pv).toFixed(2) : "1.00";

  document.getElementById("kpi-pv").textContent = `${pv}%`;
  document.getElementById("kpi-ev").textContent = `${ev}%`;
  document.getElementById("kpi-claimed").textContent = `${claimed}%`;
  document.getElementById("kpi-spi").textContent = spi;
  document.getElementById("kpi-delay").textContent = `3 Days`;

  const barEv = document.getElementById("bar-evidence");
  const barGap = document.getElementById("bar-gap");
  const gap = Math.max(0, claimed - ev);

  barEv.style.width = `${Math.min(100, ev)}%`;
  barEv.textContent = ev > 5 ? `${ev}%` : "";
  barGap.style.width = `${Math.min(100 - ev, gap)}%`;
  barGap.textContent = gap > 5 ? `${gap.toFixed(1)}%` : "";

  document.getElementById("integrity-label").textContent =
    `Evidence: ${ev}% | Claimed: ${claimed}% (Gap: ${gap.toFixed(1)}%)`;

  // Critical path list
  const critList = document.getElementById("crit-path-list");
  critList.innerHTML = "";
  const critActs = BASELINE_ACTIVITIES.filter(a => a.is_critical);

  critActs.forEach(act => {
    const isDelayed = act.activity_id === "ACT-PIP-104";
    const el = document.createElement("div");
    el.className = `p-2.5 rounded-lg border text-xs flex justify-between items-center ${
      isDelayed ? "bg-rose-950/30 border-rose-800/60" : "bg-slate-900/60 border-slate-800"
    }`;
    const state = actualStates[act.activity_id] || { progress_pct: 0, status: "NOT_STARTED" };
    el.innerHTML = `
      <div class="space-y-0.5 truncate pr-2">
        <div class="flex items-center space-x-1.5">
          <span class="font-mono text-[10px] text-cyan-400">${act.activity_id}</span>
          <span class="text-slate-200 font-medium truncate">${act.activity_name}</span>
        </div>
        <p class="text-[10px] text-slate-400">${act.discipline} &bull; Float: 0d &bull; ${act.planned_start} to ${act.planned_finish}</p>
      </div>
      <div class="text-right whitespace-nowrap">
        <span class="text-xs font-bold ${isDelayed ? 'text-rose-400' : 'text-slate-300'}">${state.progress_pct}%</span>
        <span class="block text-[9px] uppercase font-semibold ${isDelayed ? 'text-rose-400' : 'text-slate-500'}">${isDelayed ? 'DELAYED' : state.status}</span>
      </div>
    `;
    critList.appendChild(el);
  });
}

function loadVoicePreset(index) {
  const p = voicePresets[index];
  if (!p) return;
  document.getElementById("agent-supervisor-name").value = p.name;
  document.getElementById("agent-discipline-select").value = p.discipline;
  document.getElementById("agent-message-input").value = p.text;
  showToast("Preset Loaded", `Loaded transcript for ${p.name}`);
}

function toggleMicRecording() {
  const micBtn = document.getElementById("mic-btn");
  const micStatus = document.getElementById("mic-status-text");
  const micIcon = document.getElementById("mic-icon");

  if (!isRecording) {
    isRecording = true;
    micBtn.classList.add("recording-pulse", "bg-rose-900/60", "border-rose-500");
    micStatus.textContent = "Listening to Field Supervisor...";
    micIcon.classList.remove("text-teal-400");
    micIcon.classList.add("text-rose-400");

    setTimeout(() => {
      loadVoicePreset(0);
      isRecording = false;
      micBtn.classList.remove("recording-pulse", "bg-rose-900/60", "border-rose-500");
      micStatus.textContent = "Simulate Voice Recording";
      micIcon.classList.remove("text-rose-400");
      micIcon.classList.add("text-teal-400");
      showToast("Speech Transcribed", "Simulated voice audio transcribed via field ASR.");
    }, 2000);
  }
}

function sendTimeAgentUpdate() {
  const supervisor = document.getElementById("agent-supervisor-name").value;
  const discipline = document.getElementById("agent-discipline-select").value;
  const message = document.getElementById("agent-message-input").value;

  if (!message.trim()) {
    showToast("Input Required", "Please enter or speak an update.", true);
    return;
  }

  document.getElementById("agent-result-empty").classList.add("hidden");
  document.getElementById("agent-result-content").classList.remove("hidden");

  let actId = "ACT-PIP-104";
  let actName = "Erect Line 24-CW-001 Spool on Pipe Rack PR-04";
  let disc = discipline === "Auto-Detect" ? "Piping" : discipline;
  let prog = 75;
  let blocker = "Crane hydraulic line rupture";

  if (message.toLowerCase().includes("pad p-12") || message.toLowerCase().includes("curing")) {
    actId = "ACT-CIV-005";
    actName = "Curing and Foundation Inspection Pad P-12";
    disc = "Civil";
    prog = 100;
    blocker = "None";
  } else if (message.toLowerCase().includes("cable") || message.toLowerCase().includes("tray b")) {
    actId = "ACT-ELE-201";
    actName = "Lay Sand Bedding and Pull 11kV Power Feeder Cable in Cable Tray B";
    disc = "Electrical";
    prog = 48;
    blocker = "None";
  } else if (message.toLowerCase().includes("16-dis-002") || message.toLowerCase().includes("gasket")) {
    actId = "ACT-PIP-106";
    actName = "Erect Line 16-DIS-002 Discharge Manifold to Pump P-101A";
    disc = "Piping";
    prog = 10;
    blocker = "Gasket Shortage (Material)";
  }

  document.getElementById("card-supervisor").textContent = supervisor;
  document.getElementById("card-discipline").textContent = disc;
  document.getElementById("card-progress").textContent = `${prog}% (IN_PROGRESS)`;
  document.getElementById("card-blocker").textContent = blocker;

  document.getElementById("card-confidence").textContent = `96.2% Confidence`;
  document.getElementById("card-target-activity").textContent = `${actId}: ${actName}`;
  document.getElementById("card-rationale").textContent = `Direct tag match '24-CW-001', Discipline '${disc}' (100%), Verb 'Erect' (+25%)`;

  const box = document.getElementById("card-routing-box");
  const decText = document.getElementById("card-routing-decision");
  const reasonText = document.getElementById("card-routing-reason");

  box.className = "p-3 rounded-lg border bg-amber-950/40 border-amber-800/60 text-amber-300 text-xs";
  decText.textContent = "Escalated to Planner Review Queue";
  document.getElementById("agent-status-badge").className = "badge badge-planner";
  document.getElementById("agent-status-badge").textContent = "Planner Review";
  reasonText.textContent = "High confidence (96.2%), but active operational delay flagged -> Sent to Planner Queue.";

  // Push to queue
  pendingQueue.unshift({
    candidate_id: "CAND-" + Math.random().toString(16).substring(2, 8).toUpperCase(),
    raw_event: { source_type: "VOICE_AGENT", event_date: "2026-11-08", extracted_activity: message.substring(0, 70) + "...", text_citation: message },
    top_matches: [{ activity_id: actId, activity_name: actName }],
    composite_confidence: 96.2,
    status: "PENDING",
    precedence_violation: false,
    has_contradiction: false
  });

  renderPlannerQueue();
  showToast("Update Processed", "Routed to Planner Review Queue");
}

function testFuzzyMatching() {
  const query = document.getElementById("match-query-input").value;
  const container = document.getElementById("match-results-container");
  container.innerHTML = "";

  const candidates = [
    { activity_id: "ACT-PIP-104", wbs_code: "3.1.4", activity_name: "Erect Line 24-CW-001 Spool on Pipe Rack PR-04", fuzzy: 94, bm25: 92, sem: 88, boost: 25, conf: 96.5, rationale: "Matched tag '24-CW-001', Discipline 'Piping' (100%), Tokens 'spool', 'erect' (+25%)" },
    { activity_id: "ACT-PIP-103", wbs_code: "3.1.3", activity_name: "Install Pipe Rack Steel Support Module PR-04", fuzzy: 72, bm25: 68, sem: 70, boost: 10, conf: 74.2, rationale: "Matched location tag 'PR-04', Discipline 'Piping'" },
    { activity_id: "ACT-PIP-105", wbs_code: "3.1.5", activity_name: "Fit-up and Weld Golden Joint GJ-04 on Line 24-CW-001", fuzzy: 64, bm25: 60, sem: 65, boost: 15, conf: 68.0, rationale: "Matched line number '24-CW-001'" }
  ];

  candidates.forEach((c, idx) => {
    const card = document.createElement("div");
    card.className = "glass-panel p-4 space-y-3";
    card.innerHTML = `
      <div class="flex justify-between items-start">
        <div class="space-y-0.5">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold px-2 py-0.5 rounded bg-slate-800 text-cyan-300">#${idx + 1} Match</span>
            <span class="font-mono text-xs text-white">${c.activity_id}</span>
            <span class="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">WBS ${c.wbs_code}</span>
          </div>
          <h4 class="text-sm font-semibold text-white mt-1">${c.activity_name}</h4>
        </div>
        <span class="badge ${c.conf >= 90 ? 'badge-auto' : 'badge-planner'}">${c.conf}% Composite</span>
      </div>
      <div class="grid grid-cols-4 gap-2 pt-1 text-center text-xs">
        <div class="bg-slate-900/80 p-2 rounded border border-slate-800"><span class="text-slate-400 block text-[10px]">RapidFuzz</span><span class="font-mono font-bold text-teal-400">${c.fuzzy}%</span></div>
        <div class="bg-slate-900/80 p-2 rounded border border-slate-800"><span class="text-slate-400 block text-[10px]">BM25 Keyword</span><span class="font-mono font-bold text-cyan-400">${c.bm25}%</span></div>
        <div class="bg-slate-900/80 p-2 rounded border border-slate-800"><span class="text-slate-400 block text-[10px]">TF-IDF Cosine</span><span class="font-mono font-bold text-indigo-400">${c.sem}%</span></div>
        <div class="bg-slate-900/80 p-2 rounded border border-slate-800"><span class="text-slate-400 block text-[10px]">Domain Boost</span><span class="font-mono font-bold text-amber-400">+${c.boost}%</span></div>
      </div>
      <p class="text-xs text-slate-400 italic">${c.rationale}</p>
    `;
    container.appendChild(card);
  });
}

function loadSampleDPR() {
  document.getElementById("dpr-textarea").value = `OIL INDIA LIMITED - INFRASTRUCTURE PROJECT MONITORING
DAILY PROGRESS REPORT (DPR) #142 | Date: 2026-11-08
1. CIVIL:
- Pump House: Foundation Pad P-12 curing concluded today with client QC signoff.
2. PIPING:
- Manifold Yard: Erected 6 out of 8 spools on line 24-CW-001 on pipe rack PR-04. Halted at 15:30 due to crane breakdown.
3. ELECTRICAL:
- Substation Corridor: Pulled 240m of 11kV cable in tray B along trench corridor.
[DELAY-01] Category: Operational | Crane breakdown on Line 24-CW-001 spool erection.`;
}

function submitDPR() {
  showToast("DPR Ingested", "Extracted 4 activity events with citations.");
  loadDemoDataset();
}

function loadSampleExcel(type) {
  showToast("Excel Log Ingested", `Processed ${type} discipline log and extracted events.`);
  loadDemoDataset();
}

function renderPlannerQueue() {
  const tableBody = document.getElementById("planner-table-body");
  if (!tableBody) return;
  tableBody.innerHTML = "";

  const pendingCount = pendingQueue.filter(q => q.status === "PENDING").length;
  const badge = document.getElementById("queue-badge");
  if (badge) {
    if (pendingCount > 0) {
      badge.textContent = pendingCount;
      badge.classList.remove("hidden");
    } else {
      badge.classList.add("hidden");
    }
  }

  if (pendingQueue.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-slate-500">No items in review queue.</td></tr>`;
    return;
  }

  pendingQueue.forEach(item => {
    const tr = document.createElement("tr");
    tr.className = item.status === "PENDING" ? "bg-amber-950/10 hover:bg-slate-900" : "hover:bg-slate-900 opacity-60";
    const topMatch = item.top_matches[0];
    tr.innerHTML = `
      <td class="p-3 whitespace-nowrap">
        <span class="font-semibold text-white block">${item.raw_event.source_type}</span>
        <span class="text-[10px] text-slate-400">${item.raw_event.event_date}</span>
      </td>
      <td class="p-3 max-w-xs">
        <p class="font-medium text-slate-200 truncate">${item.raw_event.extracted_activity}</p>
        <span class="text-[10px] text-slate-400 block italic">"${item.raw_event.text_citation}"</span>
      </td>
      <td class="p-3">
        <span class="font-mono text-cyan-300 block">${topMatch.activity_id}</span>
        <span class="text-[11px] text-slate-300 truncate block">${topMatch.activity_name}</span>
      </td>
      <td class="p-3 whitespace-nowrap">
        <span class="badge ${item.composite_confidence >= 90 ? 'badge-auto' : 'badge-planner'}">${item.composite_confidence}%</span>
      </td>
      <td class="p-3 max-w-xs">
        ${item.precedence_violation ? '<span class="text-rose-400 text-[10px] font-semibold block">Precedence Anomaly</span>' : '<span class="text-emerald-400 text-[10px]">Clean Logic</span>'}
      </td>
      <td class="p-3 whitespace-nowrap">
        <span class="text-xs font-semibold ${item.status === 'COMMITTED' ? 'text-emerald-400' : 'text-amber-400'}">${item.status}</span>
      </td>
      <td class="p-3 text-right whitespace-nowrap">
        ${item.status === 'PENDING' ? `
          <div class="flex justify-end space-x-1.5">
            <button onclick="resolveCandidate('${item.candidate_id}', 'ACCEPT')" class="px-2.5 py-1 rounded bg-teal-600 hover:bg-teal-500 text-white text-[11px] font-semibold">Accept</button>
            <button onclick="resolveCandidate('${item.candidate_id}', 'REJECT')" class="px-2.5 py-1 rounded bg-rose-600 hover:bg-rose-500 text-white text-[11px]">Reject</button>
          </div>
        ` : '<span class="text-[11px] text-slate-500">Committed</span>'}
      </td>
    `;
    tableBody.appendChild(tr);
  });
}

function resolveCandidate(candidateId, action) {
  const item = pendingQueue.find(q => q.candidate_id === candidateId);
  if (item) {
    item.status = action === "ACCEPT" ? "COMMITTED" : "REJECTED";
    if (action === "ACCEPT") {
      actualStates[item.top_matches[0].activity_id].progress_pct = 75;
      actualStates[item.top_matches[0].activity_id].evidence_progress_pct = 75;
      auditLogs.unshift({
        audit_id: "AUDIT-" + Math.random().toString(16).substring(2, 8).toUpperCase(),
        timestamp: new Date().toLocaleString(),
        activity_id: item.top_matches[0].activity_id,
        actor: "Planner [R. Sharma]",
        evidence_hash: "a4f9e10d" + Math.random().toString(16).substring(2, 10),
        diff_summary: "Progress: 0% -> 75%",
        raw_text_citation: item.raw_event.text_citation
      });
      renderAuditLogs();
      updateCockpit();
    }
    renderPlannerQueue();
    showToast("Queue Updated", `Candidate marked as ${action}ED`);
  }
}

function renderAuditLogs() {
  const tbody = document.getElementById("audit-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";
  auditLogs.forEach(log => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-900/60";
    tr.innerHTML = `
      <td class="p-3 whitespace-nowrap"><span class="font-mono text-xs text-cyan-300 block">${log.audit_id}</span><span class="text-[10px] text-slate-400">${log.timestamp}</span></td>
      <td class="p-3 font-mono text-white whitespace-nowrap">${log.activity_id}</td>
      <td class="p-3 text-slate-300 whitespace-nowrap">${log.actor}</td>
      <td class="p-3 whitespace-nowrap"><span class="font-mono text-[10px] bg-slate-900 px-2 py-1 rounded text-teal-400 border border-slate-800">${log.evidence_hash}</span></td>
      <td class="p-3 text-slate-300 whitespace-nowrap font-medium">${log.diff_summary}</td>
      <td class="p-3 text-slate-400 max-w-sm truncate italic">"${log.raw_text_citation}"</td>
    `;
    tbody.appendChild(tr);
  });
}

function loadDemoDataset() {
  actualStates["ACT-CIV-005"].progress_pct = 100;
  actualStates["ACT-CIV-005"].evidence_progress_pct = 100;
  actualStates["ACT-PIP-104"].progress_pct = 75;
  actualStates["ACT-PIP-104"].evidence_progress_pct = 75;
  actualStates["ACT-ELE-201"].progress_pct = 48;
  actualStates["ACT-ELE-201"].evidence_progress_pct = 48;

  pendingQueue = [
    {
      candidate_id: "CAND-01",
      raw_event: { source_type: "DPR #142", event_date: "2026-11-08", extracted_activity: "Erect 6/8 spools line 24-CW-001 PR-04 (Crane halt)", text_citation: "Erected 6/8 spools on line 24-CW-001 on pipe rack PR-04. Halted at 15:30 due to crane breakdown." },
      top_matches: [{ activity_id: "ACT-PIP-104", activity_name: "Erect Line 24-CW-001 Spool on Pipe Rack PR-04" }],
      composite_confidence: 96.5,
      status: "PENDING",
      precedence_violation: false,
      has_contradiction: false
    },
    {
      candidate_id: "CAND-02",
      raw_event: { source_type: "EXCEL Piping", event_date: "2026-11-09", extracted_activity: "Line 16-DIS-002 fit-up on hold (Waiting 300# gasket)", text_citation: "Piping spool log row 4: Waiting for 300# ANSI spiral wound gasket" },
      top_matches: [{ activity_id: "ACT-PIP-106", activity_name: "Erect Line 16-DIS-002 Discharge Manifold to Pump P-101A" }],
      composite_confidence: 88.0,
      status: "PENDING",
      precedence_violation: false,
      has_contradiction: false
    },
    {
      candidate_id: "CAND-03",
      raw_event: { source_type: "DPR #142", event_date: "2026-11-08", extracted_activity: "System Hydrotest claim before Golden Joint welding complete", text_citation: "Hydrostatic testing prep on 24-CW-001" },
      top_matches: [{ activity_id: "ACT-PIP-108", activity_name: "System Hydrostatic Pressure Testing for Line 24-CW-001" }],
      composite_confidence: 82.0,
      status: "PENDING",
      precedence_violation: true,
      has_contradiction: false
    }
  ];

  auditLogs = [
    {
      audit_id: "AUDIT-INIT-01",
      timestamp: "2026-11-08 17:35:00",
      activity_id: "ACT-CIV-005",
      actor: "Auto-Agent (QC Verified)",
      evidence_hash: "9b12a84ef301cd20",
      diff_summary: "Progress: 0% -> 100%",
      raw_text_citation: "Pad P-12 curing concluded today. QC team issued clearance certificate."
    }
  ];

  updateCockpit();
  renderPlannerQueue();
  renderAuditLogs();
  showToast("Oil India Demo Loaded", "Linked DPR, Excel & Voice updates across 6 disciplines.");
}

function searchInstitutionalMemory() {
  const q = (document.getElementById("memory-search-input").value || "").toLowerCase();
  const records = [
    { name: "Erect 24-inch Spool on Pipe Rack", project: "Duliajan Tank Farm Ph-1", disc: "Piping", var: 4, cause: "Mobile crane breakdown & hydraulic hose replacement delay", lesson: "Mandate on-site spare hydraulic hoses for >40T cranes during peak spool erection." },
    { name: "Erect Discharge Manifold to Booster Pump", project: "Numaligarh Dispatch Manifold", disc: "Piping", var: 4, cause: "Class 300 ANSI spiral wound gaskets delayed in transit", lesson: "Procure specialized RTJ and spiral wound gaskets 6 weeks prior to mobilization." },
    { name: "Curing & Foundation Inspection Pad P-12", project: "Guwahati Pumping Station", disc: "Civil", var: 2, cause: "Third-party inspector unavailable for rebound hammer test", lesson: "Schedule joint inspection window 48 hours prior to 7-day curing threshold." },
    { name: "Pull 11kV Power Feeder Cable in Cable Tray", project: "Duliajan Terminal Electrification", disc: "Electrical", var: 4, cause: "Cable winch slippage and tight bend radius in trench C-1", lesson: "Utilize motorized cable pulling rollers every 10m to prevent insulation pinch." },
    { name: "Excavate Storage Tank Ring Beam", project: "Moran Crude Gathering Station", disc: "Civil", var: 7, cause: "Waterlogging in foundation trench during monsoon rain", lesson: "Deploy high-capacity dewatering sludge pumps before beginning excavation in Brahmaputra basin." }
  ];

  const filtered = q ? records.filter(r => r.name.toLowerCase().includes(q) || r.cause.toLowerCase().includes(q) || r.lesson.toLowerCase().includes(q)) : records;
  const container = document.getElementById("memory-results-container");
  container.innerHTML = "";

  filtered.forEach(r => {
    const card = document.createElement("div");
    card.className = "p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1.5";
    card.innerHTML = `
      <div class="flex justify-between items-start">
        <div><span class="font-bold text-white">${r.name}</span><span class="text-[10px] text-slate-400 block">${r.project} &bull; ${r.disc}</span></div>
        <span class="badge ${r.var > 0 ? 'badge-supervisor' : 'badge-auto'}">+${r.var}d Slippage</span>
      </div>
      <p class="text-slate-300 text-[11px]"><strong class="text-amber-400">Delay Bottleneck:</strong> ${r.cause}</p>
      <p class="text-teal-300 text-[11px] bg-teal-950/30 p-2 rounded border border-teal-900/40"><strong class="text-teal-400">Institutional Lesson:</strong> ${r.lesson}</p>
    `;
    container.appendChild(card);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) lucide.createIcons();
  initCharts();
  loadDemoDataset();
  searchInstitutionalMemory();

  // Benchmarks table
  const tbody = document.getElementById("memory-benchmark-body");
  if (tbody) {
    const benches = [
      { disc: "Civil", count: 4, plan: 9.8, act: 12.0, slip: 22.4, prod: "0.82x" },
      { disc: "Piping", count: 6, plan: 11.2, act: 14.8, slip: 32.1, prod: "0.76x" },
      { disc: "Electrical", count: 3, plan: 10.5, act: 13.0, slip: 23.8, prod: "0.81x" },
      { disc: "Instrumentation", count: 2, plan: 7.0, act: 8.0, slip: 14.3, prod: "0.88x" }
    ];
    tbody.innerHTML = "";
    benches.forEach(b => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td class="p-2.5 font-semibold text-white">${b.disc}</td><td class="p-2.5 text-slate-400">${b.count}</td><td class="p-2.5 text-slate-300">${b.plan}d</td><td class="p-2.5 text-slate-300">${b.act}d</td><td class="p-2.5 font-bold ${b.slip > 25 ? 'text-rose-400' : 'text-amber-400'}">+${b.slip}%</td><td class="p-2.5 text-teal-400 font-mono font-bold">${b.prod}</td>`;
      tbody.appendChild(tr);
    });
  }
});


// -------------------- ROLE-BASED AUTHENTICATION LOGIC --------------------
let currentUser = {
  email: "planner@oilindia.in",
  name: "R. Sharma",
  role: "ADMIN_PLANNER",
  title: "Lead Project Planner",
  badge: "Admin / Planner",
  icon: "??"
};

function openLoginModal() {
  const m = document.getElementById("login-modal");
  if (m) m.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}

function closeLoginModal() {
  const m = document.getElementById("login-modal");
  if (m) m.classList.add("hidden");
}

async function quickLogin(email, password) {
  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password })
    });
    if (res.ok) {
      const data = await res.json();
      applyUserRole(data.user);
    } else {
      // Standalone Netlify fallback
      applyUserRoleFallback(email);
    }
  } catch (err) {
    applyUserRoleFallback(email);
  }
}

function applyUserRoleFallback(email) {
  if (email.includes("supervisor")) {
    applyUserRole({
      email: "supervisor@oilindia.in",
      name: "Raman Borah",
      role: "SITE_SUPERVISOR",
      title: "Piping Field Supervisor",
      badge: "Worker / Supervisor",
      discipline: "Piping"
    });
  } else if (email.includes("civil")) {
    applyUserRole({
      email: "civil@oilindia.in",
      name: "Debojit Saikia",
      role: "SITE_SUPERVISOR",
      title: "Civil Section Engineer",
      badge: "Worker / Supervisor",
      discipline: "Civil"
    });
  } else if (email.includes("director")) {
    applyUserRole({
      email: "director@oilindia.in",
      name: "Dr. P. K. Goswami",
      role: "EXECUTIVE_AUDITOR",
      title: "Executive Project Director",
      badge: "Executive / OIL HQ"
    });
  } else {
    applyUserRole({
      email: "planner@oilindia.in",
      name: "R. Sharma",
      role: "ADMIN_PLANNER",
      title: "Lead Project Planner",
      badge: "Admin / Planner"
    });
  }
}

function applyUserRole(user) {
  currentUser = user;
  const iconMap = {
    "ADMIN_PLANNER": "??",
    "SITE_SUPERVISOR": "??",
    "EXECUTIVE_AUDITOR": "???"
  };
  currentUser.icon = iconMap[user.role] || "??";

  document.getElementById("user-display-name").textContent = user.name;
  document.getElementById("user-role-badge").textContent = user.badge;
  document.getElementById("user-role-icon").textContent = currentUser.icon;

  closeLoginModal();
  showToast("Role Switched", `Logged in as ${user.name} (${user.badge})`);

  // Adapt UI based on role
  if (user.role === "SITE_SUPERVISOR") {
    switchTab("time-agent");
    const nameInput = document.getElementById("agent-supervisor-name");
    if (nameInput) nameInput.value = `${user.name} (${user.title})`;
    if (user.discipline) {
      const discSelect = document.getElementById("agent-discipline-select");
      if (discSelect) discSelect.value = user.discipline;
    }
  } else if (user.role === "EXECUTIVE_AUDITOR") {
    switchTab("cockpit");
  } else {
    switchTab("planner");
  }

  // Refresh planner queue view with updated permissions
  if (typeof fetchPlannerQueue === "function") {
    fetchPlannerQueue();
  }
}

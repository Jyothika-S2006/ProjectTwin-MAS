// ProjectTwin Frontend Logic - Team SentinelX3.0 / SIH26122 (Oil India Limited)

let sCurveChart = null;
let delayChart = null;
let isRecording = false;
let voicePresets = [];

document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  initCharts();
  fetchScheduleAndEVM();
  fetchPlannerQueue();
  fetchInstitutionalMemory();
  fetchAuditLogs();

  // Voice presets definitions
  voicePresets = [
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
});

function showToast(title, message, isError = false) {
  const toast = document.getElementById("toast");
  const tTitle = document.getElementById("toast-title");
  const tBody = document.getElementById("toast-body");
  const tIcon = document.getElementById("toast-icon");

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
    if (btn.getAttribute("onclick").includes(`'${tabName}'`)) {
      btn.classList.add("active");
      btn.classList.remove("text-slate-400");
    } else {
      btn.classList.remove("active");
      btn.classList.add("text-slate-400");
    }
  });

  if (tabName === "planner") fetchPlannerQueue();
  if (tabName === "memory") fetchInstitutionalMemory();
  if (tabName === "audit") fetchAuditLogs();
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
            borderColor: "#06b6d4",
            backgroundColor: "rgba(6, 182, 212, 0.08)",
            borderWidth: 2,
            tension: 0.35,
            fill: true,
            pointRadius: 3
          },
          {
            label: "Claimed Progress (% Self-Reported)",
            data: [0, 7, 21, 42, 46, null, null, null],
            borderColor: "#f59e0b",
            borderDash: [5, 5],
            borderWidth: 2,
            tension: 0.35,
            fill: false,
            pointRadius: 3
          },
          {
            label: "Earned Value (EV Evidence-Verified %)",
            data: [0, 6, 19, 36, 41, null, null, null],
            borderColor: "#10b981",
            backgroundColor: "rgba(16, 185, 129, 0.15)",
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
          legend: {
            labels: { color: "#94a3b8", font: { size: 11 } }
          },
          tooltip: {
            callbacks: {
              label: (item) => `${item.dataset.label}: ${item.raw}%`
            }
          }
        },
        scales: {
          x: {
            grid: { color: "rgba(255,255,255,0.05)" },
            ticks: { color: "#94a3b8", font: { size: 10 } }
          },
          y: {
            min: 0,
            max: 100,
            grid: { color: "rgba(255,255,255,0.05)" },
            ticks: {
              color: "#94a3b8",
              font: { size: 10 },
              callback: (val) => `${val}%`
            }
          }
        }
      }
    });
  }

  const ctxD = document.getElementById("delayChart");
  if (ctxD) {
    delayChart = new Chart(ctxD, {
      type: "doughnut",
      data: {
        labels: ["Operational (Crane / Equip)", "Material Shortage", "Approval / Inspection", "Weather / Rain"],
        datasets: [{
          data: [4, 3, 2, 2],
          backgroundColor: ["#f43f5e", "#f59e0b", "#6366f1", "#06b6d4"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { color: "#94a3b8", font: { size: 10 } } }
        },
        cutout: "68%"
      }
    });
  }
}
﻿async function fetchScheduleAndEVM() {
  try {
    const [resSched, resEVM] = await Promise.all([
      fetch("/api/schedule"),
      fetch("/api/analytics/evm")
    ]);
    const dataSched = await resSched.json();
    const dataEVM = await resEVM.json();

    const evm = dataEVM.metrics;
    document.getElementById("kpi-pv").textContent = `${evm.planned_value}%`;
    document.getElementById("kpi-ev").textContent = `${evm.earned_value}%`;
    document.getElementById("kpi-claimed").textContent = `${evm.claimed_value}%`;
    document.getElementById("kpi-spi").textContent = evm.schedule_performance_index.toFixed(2);
    document.getElementById("kpi-delay").textContent = `${evm.critical_path_delay_days} Days`;

    const verificationRatio = evm.claimed_value > 0
      ? Math.min(100, Math.round((evm.earned_value / evm.claimed_value) * 100))
      : 100;
    document.getElementById("kpi-verification").textContent = `${verificationRatio}%`;

    // Update Progress Integrity Bar
    const barEv = document.getElementById("bar-evidence");
    const barGap = document.getElementById("bar-gap");
    const gap = Math.max(0, evm.claimed_value - evm.earned_value);

    barEv.style.width = `${Math.min(100, evm.earned_value)}%`;
    barEv.textContent = evm.earned_value > 5 ? `${evm.earned_value}%` : "";
    barGap.style.width = `${Math.min(100 - evm.earned_value, gap)}%`;
    barGap.textContent = gap > 5 ? `${gap.toFixed(1)}%` : "";

    document.getElementById("integrity-label").textContent =
      `Evidence: ${evm.earned_value}% | Claimed: ${evm.claimed_value}% (Gap: ${gap.toFixed(1)}%)`;

    // Render Critical Path List
    const critContainer = document.getElementById("crit-path-list");
    critContainer.innerHTML = "";
    const critActs = dataSched.activities.filter(a => a.is_critical);
    document.getElementById("crit-count-badge").textContent = `${critActs.length} Critical Nodes`;

    critActs.forEach(act => {
      const isDelayed = act.status === "DELAYED" || act.delay_reasons.length > 0;
      const el = document.createElement("div");
      el.className = `p-2.5 rounded-lg border text-xs flex justify-between items-center ${
        isDelayed ? "bg-rose-950/30 border-rose-800/60" : "bg-slate-900/60 border-slate-800"
      }`;
      el.innerHTML = `
        <div class="space-y-0.5 truncate pr-2">
          <div class="flex items-center space-x-1.5">
            <span class="font-mono text-[10px] text-cyan-400">${act.activity_id}</span>
            <span class="text-slate-200 font-medium truncate">${act.activity_name}</span>
          </div>
          <p class="text-[10px] text-slate-400">${act.discipline} &bull; Float: 0d &bull; ${act.planned_start} to ${act.planned_finish}</p>
        </div>
        <div class="text-right whitespace-nowrap">
          <span class="text-xs font-bold ${act.progress_pct >= 100 ? 'text-emerald-400' : isDelayed ? 'text-rose-400' : 'text-slate-300'}">${act.progress_pct}%</span>
          <span class="block text-[9px] uppercase font-semibold ${isDelayed ? 'text-rose-400' : 'text-slate-500'}">${act.status}</span>
        </div>
      `;
      critContainer.appendChild(el);
    });

    // Update S-Curve Chart
    if (sCurveChart && dataEVM.s_curve) {
      sCurveChart.data.labels = dataEVM.s_curve.labels;
      sCurveChart.data.datasets[0].data = dataEVM.s_curve.planned;
      sCurveChart.data.datasets[1].data = dataEVM.s_curve.claimed;
      sCurveChart.data.datasets[2].data = dataEVM.s_curve.earned;
      sCurveChart.update();
    }
  } catch (err) {
    console.error("Error fetching schedule/EVM:", err);
  }
}

async function loadDemoDataset() {
  const btn = document.getElementById("load-demo-btn");
  btn.disabled = true;
  btn.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg> Processing Multi-Agent Pipeline...`;

  try {
    const res = await fetch("/api/demo/load-all", { method: "POST" });
    const data = await res.json();
    if (data.status === "SUCCESS") {
      showToast("Oil India Demo Loaded", `${data.total_candidates} events linked across DPR, Excel & Voice inputs.`);
      await fetchScheduleAndEVM();
      await fetchPlannerQueue();
      await fetchInstitutionalMemory();
      await fetchAuditLogs();
    }
  } catch (err) {
    showToast("Error", "Failed to load demo dataset", true);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="play-circle" class="w-4 h-4 mr-1"></i><span>Load Oil India Demo Dataset</span>`;
    if (window.lucide) lucide.createIcons();
  }
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

    // Check for native SpeechRecognition
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-IN";

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("agent-message-input").value = transcript;
        stopMic();
      };
      recognition.onerror = () => {
        stopMic();
      };
      recognition.onend = () => {
        stopMic();
      };
      recognition.start();
    } else {
      // Simulate live speech recording
      setTimeout(() => {
        loadVoicePreset(0);
        stopMic();
        showToast("Speech Transcribed", "Simulated voice audio transcribed via field ASR.");
      }, 2000);
    }
  } else {
    stopMic();
  }
}

function stopMic() {
  isRecording = false;
  const micBtn = document.getElementById("mic-btn");
  const micStatus = document.getElementById("mic-status-text");
  const micIcon = document.getElementById("mic-icon");
  micBtn.classList.remove("recording-pulse", "bg-rose-900/60", "border-rose-500");
  micStatus.textContent = "Simulate Voice Recording";
  micIcon.classList.remove("text-rose-400");
  micIcon.classList.add("text-teal-400");
}

async function sendTimeAgentUpdate() {
  const supervisor = document.getElementById("agent-supervisor-name").value;
  const discipline = document.getElementById("agent-discipline-select").value;
  const message = document.getElementById("agent-message-input").value;

  if (!message.trim()) {
    showToast("Input Required", "Please type or speak an update first.", true);
    return;
  }

  try {
    const res = await fetch("/api/time-agent/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ supervisor_name: supervisor, discipline: discipline, message: message })
    });
    const data = await res.json();

    document.getElementById("agent-result-empty").classList.add("hidden");
    document.getElementById("agent-result-content").classList.remove("hidden");

    const conf = data.confirmation_card;
    document.getElementById("card-supervisor").textContent = conf.supervisor;
    document.getElementById("card-discipline").textContent = conf.discipline;
    document.getElementById("card-progress").textContent = `${conf.progress_pct}% (${conf.status})`;
    document.getElementById("card-blocker").textContent = conf.blocker_detected ? `${conf.delay_category} Bottleneck` : "None";

    const topMatch = data.top_candidates[0];
    if (topMatch) {
      document.getElementById("card-confidence").textContent = `${topMatch.composite_confidence}% Confidence`;
      document.getElementById("card-target-activity").textContent = `${topMatch.activity_id}: ${topMatch.activity_name}`;
      document.getElementById("card-rationale").textContent = topMatch.match_rationale;
    }

    const box = document.getElementById("card-routing-box");
    const decText = document.getElementById("card-routing-decision");
    const reasonText = document.getElementById("card-routing-reason");

    if (data.routing_decision === "AUTO_SOFT_UPDATE") {
      box.className = "p-3 rounded-lg border bg-emerald-950/40 border-emerald-800/60 text-emerald-300 text-xs";
      decText.textContent = "Soft-Update Committed (Auto-Linked)";
      document.getElementById("agent-status-badge").className = "badge badge-auto";
      document.getElementById("agent-status-badge").textContent = "Auto-Committed";
    } else if (data.routing_decision === "PLANNER_REVIEW") {
      box.className = "p-3 rounded-lg border bg-amber-950/40 border-amber-800/60 text-amber-300 text-xs";
      decText.textContent = "Escalated to Planner Review Queue";
      document.getElementById("agent-status-badge").className = "badge badge-planner";
      document.getElementById("agent-status-badge").textContent = "Planner Review";
    } else {
      box.className = "p-3 rounded-lg border bg-rose-950/40 border-rose-800/60 text-rose-300 text-xs";
      decText.textContent = "Supervisor Clarification Needed";
      document.getElementById("agent-status-badge").className = "badge badge-supervisor";
      document.getElementById("agent-status-badge").textContent = "Low Confidence";
    }
    reasonText.textContent = data.routing_reasons.join(" ");

    showToast("Update Processed", `Routed to ${data.routing_decision}`);
    await fetchScheduleAndEVM();
    await fetchPlannerQueue();
    await fetchAuditLogs();
  } catch (err) {
    showToast("Error", "Failed to process supervisor message", true);
  }
}

async function testFuzzyMatching() {
  const query = document.getElementById("match-query-input").value;
  const discipline = document.getElementById("match-discipline-select").value;

  try {
    const res = await fetch("/api/linking/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, discipline: discipline })
    });
    const data = await res.json();
    const container = document.getElementById("match-results-container");
    container.innerHTML = "";

    data.candidates.forEach((c, idx) => {
      const card = document.createElement("div");
      const badgeClass = c.composite_confidence >= 90 ? "badge-auto" : c.composite_confidence >= 60 ? "badge-planner" : "badge-supervisor";
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
          <span class="badge ${badgeClass}">${c.composite_confidence}% Composite</span>
        </div>

        <div class="grid grid-cols-4 gap-2 pt-1 text-center text-xs">
          <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
            <span class="text-slate-400 block text-[10px]">RapidFuzz</span>
            <span class="font-mono font-bold text-teal-400">${c.fuzzy_score}%</span>
          </div>
          <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
            <span class="text-slate-400 block text-[10px]">BM25 Keyword</span>
            <span class="font-mono font-bold text-cyan-400">${c.bm25_score}%</span>
          </div>
          <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
            <span class="text-slate-400 block text-[10px]">TF-IDF Cosine</span>
            <span class="font-mono font-bold text-indigo-400">${c.semantic_score}%</span>
          </div>
          <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
            <span class="text-slate-400 block text-[10px]">Domain Boost</span>
            <span class="font-mono font-bold text-amber-400">+${c.domain_boost}%</span>
          </div>
        </div>

        <p class="text-xs text-slate-400 italic">${c.match_rationale}</p>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    showToast("Error", "Fuzzy matching failed", true);
  }
}

async function loadSampleDPR() {
  const dprText = `OIL INDIA LIMITED - INFRASTRUCTURE PROJECT MONITORING
DAILY PROGRESS REPORT (DPR) #142 | Date: 2026-11-08
1. CIVIL:
- Pump House: Foundation Pad P-12 curing concluded today with client QC signoff.
2. PIPING:
- Manifold Yard: Erected 6 out of 8 spools on line 24-CW-001 on pipe rack PR-04. Halted at 15:30 due to crane breakdown.
3. ELECTRICAL:
- Substation Corridor: Pulled 240m of 11kV cable in tray B along trench corridor.
[DELAY-01] Category: Operational | Crane breakdown on Line 24-CW-001 spool erection.`;
  document.getElementById("dpr-textarea").value = dprText;
}

async function submitDPR() {
  const text = document.getElementById("dpr-textarea").value;
  if (!text.trim()) {
    showToast("Input Required", "Paste DPR text first", true);
    return;
  }
  const formData = new FormData();
  formData.append("text", text);

  try {
    const res = await fetch("/api/ingest/dpr", { method: "POST", body: formData });
    const data = await res.json();
    showToast("DPR Ingested", `Extracted ${data.events_count} activity events with citations.`);

    const stream = document.getElementById("ingestion-events-stream");
    stream.innerHTML = "";
    data.candidates.forEach(c => {
      const el = document.createElement("div");
      el.className = "p-3 rounded-lg bg-slate-900/70 border border-slate-800 text-xs space-y-1";
      el.innerHTML = `
        <div class="flex justify-between">
          <span class="font-semibold text-cyan-300">[${c.raw_event.discipline}] ${c.raw_event.extracted_activity}</span>
          <span class="badge ${c.routing_decision === 'AUTO_SOFT_UPDATE' ? 'badge-auto' : 'badge-planner'}">${c.routing_decision}</span>
        </div>
        <p class="text-slate-400 text-[11px]">Citation: "${c.raw_event.text_citation}"</p>
      `;
      stream.appendChild(el);
    });

    await fetchScheduleAndEVM();
    await fetchPlannerQueue();
    await fetchAuditLogs();
  } catch (err) {
    showToast("Error", "Failed to ingest DPR", true);
  }
}

function loadSampleExcel(type) {
  showToast("Excel Log Ingested", `Processed ${type} discipline log and extracted events.`);
  loadDemoDataset();
}

async function fetchPlannerQueue() {
  try {
    const res = await fetch("/api/planner/queue");
    const data = await res.json();
    const tableBody = document.getElementById("planner-table-body");
    tableBody.innerHTML = "";

    const pendingCount = data.queue.filter(q => q.status === "PENDING").length;
    const badge = document.getElementById("queue-badge");
    if (pendingCount > 0) {
      badge.textContent = pendingCount;
      badge.classList.remove("hidden");
    } else {
      badge.classList.add("hidden");
    }

    if (data.queue.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-slate-500">No items currently in review queue.</td></tr>`;
      return;
    }

    data.queue.forEach(item => {
      const tr = document.createElement("tr");
      tr.className = item.status === "PENDING" ? "bg-amber-950/10 hover:bg-slate-900" : "hover:bg-slate-900 opacity-60";
      const topMatch = item.top_matches[0];
      const hasConflict = item.has_contradiction || item.precedence_violation;

      tr.innerHTML = `
        <td class="p-3 whitespace-nowrap">
          <span class="font-semibold text-white block">${item.raw_event.source_type}</span>
          <span class="text-[10px] text-slate-400">${item.raw_event.event_date}</span>
        </td>
        <td class="p-3 max-w-xs">
          <p class="font-medium text-slate-200 truncate">${item.raw_event.extracted_activity}</p>
          <span class="text-[10px] text-slate-400 block italic">"${item.raw_event.text_citation || item.raw_event.raw_text}"</span>
        </td>
        <td class="p-3">
          <span class="font-mono text-cyan-300 block">${topMatch ? topMatch.activity_id : 'UNMATCHED'}</span>
          <span class="text-[11px] text-slate-300 truncate block">${topMatch ? topMatch.activity_name : 'No candidate'}</span>
        </td>
        <td class="p-3 whitespace-nowrap">
          <span class="badge ${item.composite_confidence >= 90 ? 'badge-auto' : 'badge-planner'}">${item.composite_confidence}%</span>
        </td>
        <td class="p-3 max-w-xs">
          ${item.precedence_violation ? `<span class="text-rose-400 text-[10px] font-semibold block flex items-center space-x-1"><i data-lucide="alert-circle" class="w-3 h-3"></i><span>Precedence Violation</span></span>` : ''}
          ${item.has_contradiction ? `<span class="text-amber-400 text-[10px] font-semibold block flex items-center space-x-1"><i data-lucide="alert-triangle" class="w-3 h-3"></i><span>Contradiction</span></span>` : ''}
          ${!hasConflict ? `<span class="text-emerald-400 text-[10px]">Clean Logic</span>` : ''}
        </td>
        <td class="p-3 whitespace-nowrap">
          <span class="text-xs font-semibold ${item.status === 'COMMITTED' ? 'text-emerald-400' : 'text-amber-400'}">${item.status}</span>
        </td>
        <td class="p-3 text-right whitespace-nowrap">
          ${item.status === 'PENDING' ? `
            <div class="flex justify-end space-x-1.5">
              <button onclick="resolveCandidate('${item.candidate_id}', '${topMatch ? topMatch.activity_id : ''}', 'ACCEPT')" class="px-2.5 py-1 rounded bg-teal-600 hover:bg-teal-500 text-white text-[11px] font-semibold">Accept</button>
              <button onclick="resolveCandidate('${item.candidate_id}', '${topMatch ? topMatch.activity_id : ''}', 'REJECT')" class="px-2.5 py-1 rounded bg-rose-600 hover:bg-rose-500 text-white text-[11px]">Reject</button>
            </div>
          ` : `<span class="text-[11px] text-slate-500">Committed</span>`}
        </td>
      `;
      tableBody.appendChild(tr);
    });

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error("Error fetching queue:", err);
  }
}

async function resolveCandidate(candidateId, actId, action) {
  try {
    const res = await fetch("/api/planner/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: candidateId,
        selected_activity_id: actId,
        action: action,
        planner_name: "R. Sharma (Lead Planner)",
        notes: "Approved by planner through ProjectTwin review interface"
      })
    });
    const data = await res.json();
    showToast("Queue Updated", `Candidate marked as ${action}ED`);
    await fetchPlannerQueue();
    await fetchScheduleAndEVM();
    await fetchAuditLogs();
  } catch (err) {
    showToast("Error", "Resolution failed", true);
  }
}

async function fetchInstitutionalMemory() {
  try {
    const res = await fetch("/api/memory/benchmarks");
    const data = await res.json();
    const benchBody = document.getElementById("memory-benchmark-body");
    benchBody.innerHTML = "";

    data.benchmarks.forEach(b => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="p-2.5 font-semibold text-white">${b.discipline}</td>
        <td class="p-2.5 text-slate-400">${b.sample_count}</td>
        <td class="p-2.5 text-slate-300">${b.avg_planned_days}d</td>
        <td class="p-2.5 text-slate-300">${b.avg_actual_days}d</td>
        <td class="p-2.5 font-bold ${b.avg_variance_pct > 20 ? 'text-rose-400' : 'text-amber-400'}">+${b.avg_variance_pct}%</td>
        <td class="p-2.5 text-teal-400 font-mono font-bold">${b.avg_productivity_index}x</td>
      `;
      benchBody.appendChild(tr);
    });

    if (delayChart && data.delays) {
      delayChart.data.labels = data.delays.map(d => `${d.delay_category} (${d.occurrences})`);
      delayChart.data.datasets[0].data = data.delays.map(d => d.occurrences);
      delayChart.update();
    }

    await searchInstitutionalMemory("");
  } catch (err) {
    console.error("Error fetching memory:", err);
  }
}

async function searchInstitutionalMemory(query = "") {
  const q = query || document.getElementById("memory-search-input").value;
  try {
    const res = await fetch(`/api/memory/query?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    const container = document.getElementById("memory-results-container");
    container.innerHTML = "";

    if (data.records.length === 0) {
      container.innerHTML = `<p class="text-xs text-slate-500 italic">No historical records matching query.</p>`;
      return;
    }

    data.records.forEach(r => {
      const card = document.createElement("div");
      card.className = "p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1.5";
      card.innerHTML = `
        <div class="flex justify-between items-start">
          <div>
            <span class="font-bold text-white">${r.activity_name}</span>
            <span class="text-[10px] text-slate-400 block">${r.project_name} &bull; ${r.discipline}</span>
          </div>
          <span class="badge ${r.variance_days > 0 ? 'badge-supervisor' : 'badge-auto'}">${r.variance_days > 0 ? `+${r.variance_days}d Slippage` : 'On Time'}</span>
        </div>
        <p class="text-slate-300 text-[11px]"><strong class="text-amber-400">Delay Bottleneck:</strong> ${r.delay_cause}</p>
        <p class="text-teal-300 text-[11px] bg-teal-950/30 p-2 rounded border border-teal-900/40"><strong class="text-teal-400">Institutional Lesson:</strong> ${r.lessons_learned}</p>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Error querying memory:", err);
  }
}

async function fetchAuditLogs() {
  try {
    const res = await fetch("/api/audit/logs");
    const data = await res.json();
    const tbody = document.getElementById("audit-table-body");
    tbody.innerHTML = "";

    if (data.audit_logs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-slate-500">No committed audit records yet.</td></tr>`;
      return;
    }

    data.audit_logs.forEach(log => {
      const tr = document.createElement("tr");
      tr.className = "hover:bg-slate-900/60";
      tr.innerHTML = `
        <td class="p-3 whitespace-nowrap">
          <span class="font-mono text-xs text-cyan-300 block">${log.audit_id}</span>
          <span class="text-[10px] text-slate-400">${log.timestamp}</span>
        </td>
        <td class="p-3 font-mono text-white whitespace-nowrap">${log.activity_id}</td>
        <td class="p-3 text-slate-300 whitespace-nowrap">${log.actor}</td>
        <td class="p-3 whitespace-nowrap">
          <span class="font-mono text-[10px] bg-slate-900 px-2 py-1 rounded text-teal-400 border border-slate-800">${log.evidence_hash}</span>
        </td>
        <td class="p-3 text-slate-300 whitespace-nowrap font-medium">${log.diff_summary}</td>
        <td class="p-3 text-slate-400 max-w-sm truncate italic">"${log.raw_text_citation}"</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Error fetching audit logs:", err);
  }
}

const state = {
  report: null,
  showBlocked: true,
  lastQuestion: "",
};

const API_ENDPOINT = "http://127.0.0.1:8765/analyze";

const fallbackReport = {
  title: "Nudge Engine Decision Report",
  executive_summary: {
    status: "hold",
    summary: "No report data could be loaded.",
    security_status: "unknown",
    uncertainty_status: "hold",
  },
  evidence_and_uncertainty: {
    uncertainty: {},
    gate: {
      status: "hold",
      summary: "Missing report data.",
      significance_claim_allowed: false,
    },
  },
  hypotheses: [],
  nudge_recommendations: [],
  segment_view: [],
  security_and_governance: {
    security_review: {},
    pii_redaction_summary: {},
    no_pii_in_segment_view: false,
  },
  result_quality: {
    pilot_readiness: "not_ready",
    decision_state: { state: "not_started", blockers: [] },
    data_readiness: { status: "hold", score: 0 },
    claim_permission: { evidence_level: "unknown", causal_claim_allowed: false },
    trust_warnings: ["missing_report_data"],
  },
  audit_lineage: {},
  next_actions: ["Load a report JSON payload."],
};

async function loadReport() {
  try {
    const response = await fetch("./data/sample-report.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Report load failed: ${response.status}`);
    state.report = await response.json();
  } catch (error) {
    state.report = fallbackReport;
    console.warn(error);
  }
  renderDashboard();
  seedChat();
}

function $(id) {
  return document.getElementById(id);
}

function text(id, value) {
  const element = $(id);
  if (element) element.textContent = value;
}

function statusClass(status = "") {
  return String(status).toLowerCase().replace(/[^a-z0-9_-]/g, "");
}

function formatValue(value, fallback = "-") {
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(3);
  return String(value);
}

function renderDashboard() {
  const report = state.report || fallbackReport;
  const executive = report.executive_summary || {};
  const evidence = report.evidence_and_uncertainty || {};
  const uncertainty = evidence.uncertainty || {};
  const gate = evidence.gate || {};
  const security = report.security_and_governance || {};
  const securityReview = security.security_review || {};

  text("report-title", report.title || "Nudge Engine Decision Report");
  text("report-summary", executive.summary || "");
  text("overall-status", executive.status || "hold");
  $("status-orb").className = `status-orb ${statusClass(executive.status)}`;

  text("kpi-decision", executive.status || "hold");
  text("kpi-uncertainty", gate.status || executive.uncertainty_status || "hold");
  text("kpi-ci-note", `${formatValue(uncertainty.ci_method, "missing")} method`);
  text("kpi-significance", gate.significance_claim_allowed ? "Allowed" : "Blocked");
  const activeNudges = (report.nudge_recommendations || []).filter((item) => item.selected_action && item.selected_action !== "no_action");
  text("kpi-nudges", String(activeNudges.length));
  text(
    "system-check-summary",
    `${securityReview.security_status || "unknown"} security, PII ${security.no_pii_in_segment_view ? "clean" : "needs review"}`,
  );

  renderCi(uncertainty, gate);
  renderHypotheses(report.hypotheses || []);
  renderNudges(report.nudge_recommendations || []);
  renderSystemChecks(securityReview, security.pii_redaction_summary || {}, security.no_pii_in_segment_view);
  renderResultQuality(report.result_quality || {}, report.audit_lineage || {});
  renderNextActions(report.next_actions || []);
}

function renderCi(uncertainty, gate) {
  const lower = Number(uncertainty.ci_lower ?? -1);
  const upper = Number(uncertainty.ci_upper ?? 1);
  const estimate = Number(uncertainty.effect_estimate ?? 0);
  const min = Math.min(lower, -0.05);
  const max = Math.max(upper, 0.05);
  const span = Math.max(max - min, 0.001);
  const left = ((lower - min) / span) * 100;
  const width = ((upper - lower) / span) * 100;
  const estimateLeft = ((estimate - min) / span) * 100;
  const nullLeft = ((0 - min) / span) * 100;

  text("ci-lower", formatValue(lower));
  text("ci-upper", formatValue(upper));
  text("ci-summary", gate.summary || "No CI summary available.");
  text("ci-pill", gate.significance_claim_allowed ? "significant" : "not stable");

  const band = $("ci-band");
  const marker = $("ci-estimate");
  const nullMarker = document.querySelector(".ci-null");
  if (band) {
    band.style.left = `${Math.max(0, Math.min(100, left))}%`;
    band.style.width = `${Math.max(2, Math.min(100, width))}%`;
  }
  if (marker) marker.style.left = `${Math.max(0, Math.min(100, estimateLeft))}%`;
  if (nullMarker) nullMarker.style.left = `${Math.max(0, Math.min(100, nullLeft))}%`;
}

function renderHypotheses(hypotheses) {
  const container = $("hypothesis-list");
  container.innerHTML = "";
  if (!hypotheses.length) {
    container.innerHTML = '<div class="stack-item">No hypotheses available.</div>';
    return;
  }
  hypotheses.forEach((item) => {
    const node = document.createElement("div");
    node.className = "stack-item";
    node.innerHTML = `
      <strong>${escapeHtml(item.id || "-")} · ${escapeHtml(item.mece_group || "hypothesis")}</strong>
      <div>${escapeHtml(item.statement || "")}</div>
      <span class="status ${statusClass(item.status)}">${escapeHtml(item.status || "unknown")}</span>
    `;
    container.appendChild(node);
  });
}

function renderNudges(items) {
  const tbody = $("nudge-table");
  tbody.innerHTML = "";
  const rows = state.showBlocked ? items : items.filter((item) => item.status !== "blocked");
  rows.forEach((item) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeHtml(item.subject_id || "-")}</td>
      <td>${escapeHtml(item.selected_action || "no_action")}</td>
      <td><span class="status ${statusClass(item.status)}">${escapeHtml(item.status || "unknown")}</span></td>
      <td>${escapeHtml(item.effect_evidence || item.claim_type || "-")}</td>
      <td>${escapeHtml(item.risk_tier || item.action_fit?.risk_tier || "-")}</td>
      <td>${item.human_review_required ? "required" : "not required"}</td>
      <td>${escapeHtml((item.reason_codes || []).join(", ") || "-")}</td>
      <td>${escapeHtml(formatValue(item.baseline_delta))}</td>
      <td>${escapeHtml(formatValue(item.no_action_reward))}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderSystemChecks(review, piiSummary, noPii) {
  const container = $("system-list");
  const items = [
    ["Security check status", review.security_status || "unknown"],
    ["Risk level", review.risk_level || "unknown"],
    ["Safe to reason", formatValue(review.safe_to_reason)],
    ["Safe to execute", formatValue(review.safe_to_execute)],
    ["No PII in segment view", formatValue(noPii)],
    ["Redacted field count", formatValue(piiSummary.redacted_field_count, "0")],
    ["Vault records", formatValue(piiSummary.vault_records, "0")],
  ];
  container.innerHTML = items
    .map(
      ([label, value]) => `
        <div class="stack-item">
          <strong>${escapeHtml(label)}</strong>
          <span class="status ${statusClass(value)}">${escapeHtml(value)}</span>
        </div>
      `,
    )
    .join("");
}

function renderResultQuality(quality, auditLineage) {
  const decisionState = quality.decision_state || {};
  const dataReadiness = quality.data_readiness || {};
  const claimPermission = quality.claim_permission || {};
  const warnings = quality.trust_warnings || [];

  text("quality-state", decisionState.state || "unknown");
  text("quality-data", `${dataReadiness.status || "unknown"} · ${formatValue(dataReadiness.score, "0")}`);
  text("quality-evidence", claimPermission.evidence_level || "unknown");
  text("quality-causal", claimPermission.causal_claim_allowed ? "allowed" : "blocked");
  text("quality-pill", quality.pilot_readiness || "not_ready");

  const warningsContainer = $("quality-warnings");
  warningsContainer.innerHTML = warnings.length
    ? warnings.map((warning) => `<div class="warning-item">${escapeHtml(warning)}</div>`).join("")
    : '<div class="warning-item ok">No trust warnings in loaded report.</div>';

  const auditItems = [
    ["Run", auditLineage.run_id],
    ["Decision", auditLineage.decision_state],
    ["Schema", auditLineage.input_schema_hash],
    ["Rows", auditLineage.input_row_count],
    ["Raw rows stored", auditLineage.stored_raw_rows],
  ];
  $("audit-lineage").innerHTML = auditItems
    .filter(([, value]) => value !== undefined && value !== null && value !== "")
    .map(([label, value]) => `<div class="warning-item"><strong>${escapeHtml(label)}:</strong> ${escapeHtml(formatValue(value))}</div>`)
    .join("") || '<div class="warning-item">Audit lineage not available in this report.</div>';
}

function renderNextActions(actions) {
  const list = $("next-actions");
  list.innerHTML = "";
  actions.forEach((action) => {
    const li = document.createElement("li");
    li.textContent = action;
    list.appendChild(li);
  });
}

function looksLikeEngineInput(payload) {
  return payload && Array.isArray(payload.customer_rows);
}

function looksLikeDecisionReport(payload) {
  return payload && payload.executive_summary && payload.evidence_and_uncertainty;
}

async function runEngineApi(payload, question) {
  const body = {
    question: question || payload.question || "Analyze activation and recommend safe next steps.",
    customer_rows: payload.customer_rows,
    config: payload.config || {},
    identity_fields: payload.identity_fields,
    confidence_level: payload.confidence_level,
  };
  const response = await fetch(API_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result?.error?.message || `Engine API failed with ${response.status}`);
  }
  return result;
}

function seedChat() {
  const log = $("chat-log");
  log.innerHTML = "";
  addMessage("bot", "Ask me about the result, recommended nudges, evidence, blockers or next actions. This is a local preview over the loaded analysis.");
}

function addMessage(type, message) {
  const bubble = document.createElement("div");
  bubble.className = `message ${type}`;
  bubble.textContent = message;
  $("chat-log").appendChild(bubble);
  $("chat-log").scrollTop = $("chat-log").scrollHeight;
}

function answerQuestion(question) {
  const report = state.report || fallbackReport;
  const normalized = question.toLowerCase();
  const executive = report.executive_summary || {};
  const evidence = report.evidence_and_uncertainty || {};
  const gate = evidence.gate || {};
  const security = report.security_and_governance || {};
  const review = security.security_review || {};

  if (normalized.includes("status") || normalized.includes("hold")) {
    return `Overall status is ${executive.status}. Reason: ${executive.summary || "No summary available."}`;
  }
  if (normalized.includes("ci") || normalized.includes("confidence") || normalized.includes("significant")) {
    return `CI gate is ${gate.status}. Significance allowed: ${gate.significance_claim_allowed ? "yes" : "no"}. ${gate.summary || ""}`;
  }
  if (normalized.includes("quality") || normalized.includes("pilot") || normalized.includes("readiness")) {
    const quality = report.result_quality || {};
    const decisionState = quality.decision_state || {};
    return `Pilot readiness is ${quality.pilot_readiness || "unknown"}. Decision state is ${decisionState.state || "unknown"}. Trust warnings: ${(quality.trust_warnings || []).join(", ") || "none"}.`;
  }
  if (normalized.includes("security") || normalized.includes("integrity") || normalized.includes("leonidas")) {
    return `Background security and integrity checks are ${review.security_status || "unknown"} with risk level ${review.risk_level || "unknown"}. This is an internal gate, not a product-facing recommendation agent.`;
  }
  if (normalized.includes("pii") || normalized.includes("privacy") || normalized.includes("vault")) {
    return `Privacy status: no PII in segment view is ${formatValue(security.no_pii_in_segment_view)}. The result view uses subject_id only.`;
  }
  if (normalized.includes("nudge") || normalized.includes("action")) {
    const nudges = report.nudge_recommendations || [];
    const active = nudges.filter((item) => item.selected_action && item.selected_action !== "no_action");
    return `${active.length} active nudge hypotheses are visible. Blocked rows remain visible so governance does not disappear.`;
  }
  return "I can answer from the loaded analysis: result status, evidence, nudges, blockers and next actions. Later this panel can call a report-grounded LLM endpoint.";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

$("toggle-blocked").addEventListener("click", () => {
  state.showBlocked = !state.showBlocked;
  $("toggle-blocked").textContent = state.showBlocked ? "Hide blockers" : "Show blockers";
  renderNudges((state.report || fallbackReport).nudge_recommendations || []);
});

$("toggle-system-details").addEventListener("click", () => {
  const details = $("system-details");
  const hidden = details.hasAttribute("hidden");
  if (hidden) {
    details.removeAttribute("hidden");
    $("toggle-system-details").textContent = "Hide details";
  } else {
    details.setAttribute("hidden", "");
    $("toggle-system-details").textContent = "Show details";
  }
});

$("analysis-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = $("analysis-question").value.trim();
  const file = $("report-upload").files[0];
  state.lastQuestion = question;

  if (file) {
    try {
      const raw = await file.text();
      const payload = JSON.parse(raw);
      if (looksLikeEngineInput(payload)) {
        text("analysis-note", "Running local engine API...");
        state.report = await runEngineApi(payload, question);
        text("analysis-note", "Local engine API result loaded. Review Result Quality before using any recommendation.");
      } else if (looksLikeDecisionReport(payload)) {
        state.report = payload;
        text("analysis-note", "Uploaded decision report loaded.");
      } else {
        text("analysis-note", "JSON parsed, but it is neither customer_rows input nor a decision report.");
      }
    } catch (error) {
      text("analysis-note", `Could not run analysis: ${error.message}. Keeping current report.`);
      console.warn(error);
    }
  } else {
    text("analysis-note", "Preview run complete using sample report. Upload customer_rows JSON to call the local API.");
  }

  renderDashboard();
  seedChat();
  if (question) {
    addMessage("user", question);
    window.setTimeout(() => addMessage("bot", answerQuestion(question)), 160);
  }
  window.location.hash = "#overview";
});

$("chat-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const input = $("chat-input");
  const question = input.value.trim();
  if (!question) return;
  addMessage("user", question);
  input.value = "";
  window.setTimeout(() => addMessage("bot", answerQuestion(question)), 160);
});

loadReport();

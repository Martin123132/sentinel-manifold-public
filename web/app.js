const state = {
  mode: "strict",
  policy: {
    relation_clamps: true,
    literal_guards: true,
    negation_guards: true,
    overclaim_guards: true,
  },
  policyProfile: "support",
  policies: [],
  provider: "local_demo",
  model: "sentinel-demo-v1",
  prompt: "",
  providers: [],
  auditHistory: [],
  apiKey: sessionStorage.getItem("sentinel-api-key") || "",
  authRequired: false,
  publicDemo: false,
  adminAuthConfigured: false,
  selectedEvidence: null,
  selectedEvidenceId: "",
  evidenceLoading: false,
  suiteResult: null,
  suiteLoading: false,
  references: [],
  candidates: [],
  result: null,
};

const candidateGrid = document.querySelector("#candidateGrid");
const referencesInput = document.querySelector("#referencesInput");
const runButton = document.querySelector("#runButton");
const loadDemoButton = document.querySelector("#loadDemoButton");
const clearButton = document.querySelector("#clearButton");
const exportButton = document.querySelector("#exportButton");
const exportBundleButton = document.querySelector("#exportBundleButton");
const policySelect = document.querySelector("#policySelect");
const providerSelect = document.querySelector("#providerSelect");
const modelInput = document.querySelector("#modelInput");
const promptInput = document.querySelector("#promptInput");
const generateButton = document.querySelector("#generateButton");
const apiKeyInput = document.querySelector("#apiKeyInput");
const unlockButton = document.querySelector("#unlockButton");
const sandboxBadge = document.querySelector("#sandboxBadge");
const railStatusLabel = document.querySelector("#railStatusLabel");
const historyCue = document.querySelector("#historyCue");
const historyTable = document.querySelector("#historyTable");
const evidenceInspector = document.querySelector("#evidenceInspector");
const exportEvidenceButton = document.querySelector("#exportEvidenceButton");
const suiteButton = document.querySelector("#suiteButton");
const topSuiteButton = document.querySelector("#topSuiteButton");
const suiteTable = document.querySelector("#suiteTable");
const suiteProofNote = document.querySelector("#suiteProofNote");
const sandboxLockCue = document.querySelector("#sandboxLockCue");
let bootstrapping = false;

function publicSandboxActive() {
  return state.publicDemo && !state.apiKey;
}

function iconSafe(text) {
  return String(text ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[char]);
}

async function loadDemo() {
  const response = await apiFetch("/api/demo");
  const payload = await response.json();
  state.policyProfile = payload.policy_profile || "support";
  state.provider = payload.provider || "local_demo";
  state.model = payload.model || "sentinel-demo-v1";
  state.prompt = payload.prompt || "";
  state.mode = payload.mode || "strict";
  state.policy = payload.policy || state.policy;
  state.references = payload.references || [];
  state.candidates = payload.candidates || [];
  state.result = null;
  syncForm();
  renderAll();
}

function syncForm() {
  referencesInput.value = state.references.join("\n");
  promptInput.value = state.prompt;
  providerSelect.value = state.provider;
  modelInput.value = state.model;
  policySelect.value = state.policyProfile;
  for (const key of Object.keys(state.policy)) {
    const input = document.querySelector(`#${key}`);
    if (input) input.checked = Boolean(state.policy[key]);
  }
  document.querySelectorAll(".segment").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === state.mode);
  });
}

function readForm() {
  state.references = referencesInput.value.split(/\n+/).map((line) => line.trim()).filter(Boolean);
  state.prompt = promptInput.value.trim();
  state.provider = providerSelect.value || "local_demo";
  state.model = modelInput.value.trim();
  state.policyProfile = policySelect.value || "support";
  for (const key of Object.keys(state.policy)) {
    const input = document.querySelector(`#${key}`);
    state.policy[key] = Boolean(input?.checked);
  }
  state.candidates = [...document.querySelectorAll("[data-candidate-id]")].map((card, index) => {
    const textArea = card.querySelector("textarea");
    return {
      id: card.dataset.candidateId,
      label: `Candidate ${String.fromCharCode(65 + index)}`,
      text: textArea.value.trim(),
    };
  }).filter((candidate) => candidate.text);
}

function renderCandidates() {
  const audits = new Map((state.result?.candidates || []).map((candidate) => [candidate.id, candidate]));
  candidateGrid.innerHTML = state.candidates.map((candidate, index) => {
    const audit = audits.get(candidate.id);
    const verdict = audit?.verdict || "READY";
    const risk = audit?.risk_score ?? 0;
    const riskClass = risk >= 58 ? "block" : risk >= 35 ? "warn" : "";
    return `
      <article class="candidate-card" data-candidate-id="${iconSafe(candidate.id)}" data-verdict="${iconSafe(verdict)}">
        <div class="candidate-head">
          <strong>${iconSafe(candidate.label || `Candidate ${String.fromCharCode(65 + index)}`)}</strong>
          <span class="verdict-chip ${verdict.toLowerCase()}">${iconSafe(verdict)}</span>
        </div>
        <textarea spellcheck="false" aria-label="${iconSafe(candidate.label)}">${iconSafe(candidate.text)}</textarea>
        <div class="candidate-foot">
          <span>Risk ${risk}</span>
          <span class="risk-meter"><span class="${riskClass}" style="width:${Math.min(100, risk)}%"></span></span>
        </div>
      </article>
    `;
  }).join("");
}

async function runCheck() {
  readForm();
  runButton.disabled = true;
  runButton.textContent = "Checking...";
  try {
    const response = await apiFetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mode: state.mode,
        policy_profile: state.policyProfile,
        provider: state.provider,
        model: state.model,
        prompt: state.prompt,
        policy: state.policy,
        references: state.references,
        candidates: state.candidates,
      }),
    });
    state.result = await response.json();
    await refreshAuditHistory();
    if (state.result.check_id && state.result.evidence?.saved !== false && !publicSandboxActive()) {
      await loadEvidencePack(state.result.check_id);
    }
    renderAll();
  } catch (error) {
    if (error.message !== "unauthorized") {
      alert(`Check failed: ${error.message}`);
    }
  } finally {
    runButton.disabled = false;
    runButton.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 5 11 7-11 7V5Z"/></svg>Run Check';
  }
}

async function runGenerateCheck() {
  readForm();
  generateButton.disabled = true;
  generateButton.textContent = "Generating...";
  try {
    const response = await apiFetch("/api/generate-check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mode: state.mode,
        policy_profile: state.policyProfile,
        provider: state.provider,
        model: state.model,
        prompt: state.prompt,
        policy: state.policy,
        references: state.references,
      }),
    });
    state.result = await response.json();
    if (state.result.error) {
      throw new Error(state.result.detail || state.result.error);
    }
    state.candidates = state.result.candidates.map((candidate) => ({
      id: candidate.id,
      label: candidate.label,
      text: candidate.text,
    }));
    await refreshAuditHistory();
    if (state.result.check_id && state.result.evidence?.saved !== false && !publicSandboxActive()) {
      await loadEvidencePack(state.result.check_id);
    }
    renderAll();
  } catch (error) {
    alert(`Generation failed: ${error.message}`);
  } finally {
    generateButton.disabled = false;
    generateButton.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>Generate & Check';
  }
}

function renderVerdict() {
  const result = state.result;
  const label = document.querySelector("#verdictLabel");
  const checkId = document.querySelector("#checkId");
  const headline = document.querySelector("#verdictHeadline");
  const summary = document.querySelector("#verdictSummary");
  const emitted = document.querySelector("#emittedBox p");
  const evidence = document.querySelector("#evidenceBox code");

  if (!result) {
    label.textContent = "READY";
    label.className = "verdict-label";
    checkId.textContent = "No check yet";
    headline.textContent = "Load the demo or paste your own references.";
    summary.textContent = "Sentinel Manifold will choose a safe candidate or block the whole pool.";
    emitted.textContent = "Waiting for a check.";
    evidence.textContent = "Not saved yet";
    updateMetrics(null);
    return;
  }

  const action = result.action || "BLOCK";
  label.textContent = action;
  label.className = `verdict-label ${action.toLowerCase()}`;
  checkId.textContent = result.check_id;
  headline.textContent = result.summary?.headline || "Guardrail check complete.";
  summary.textContent = `${result.summary?.blocked_count || 0} of ${result.summary?.candidate_count || 0} candidates blocked. ${result.summary?.reference_relations || 0} protected relations extracted.`;
  emitted.textContent = result.emitted_text || "No candidate was safe enough to emit.";
  evidence.textContent = result.evidence?.digest ? `${result.evidence.digest.slice(0, 18)}...` : "Evidence metadata unavailable";
  if (result.evidence?.saved === false) {
    evidence.textContent = "Not saved in public sandbox";
  }
  updateMetrics(result);
}

function updateMetrics(result) {
  document.querySelector("#metricAction").textContent = result?.action || "READY";
  document.querySelector("#metricRisk").textContent = result?.summary?.highest_risk_score ?? "--";
  document.querySelector("#metricRelations").textContent = result?.summary?.reference_relations ?? "--";
  document.querySelector("#metricBlocked").textContent = result?.summary?.blocked_count ?? "--";
}

function renderFindings() {
  const list = document.querySelector("#findingsList");
  if (!state.result) {
    list.innerHTML = `<div class="finding-item"><strong>No findings yet</strong><p>Run a check to populate the audit trail.</p></div>`;
    return;
  }

  const allFindings = state.result.candidates.flatMap((candidate) =>
    candidate.findings.map((finding) => ({ ...finding, candidate: candidate.label, verdict: candidate.verdict }))
  );

  if (!allFindings.length) {
    list.innerHTML = `<div class="finding-item"><strong>No guardrail findings</strong><p>All candidate outputs stayed inside the supplied reference structure.</p></div>`;
    return;
  }

  list.innerHTML = allFindings.slice(0, 9).map((finding) => `
    <div class="finding-item">
      <strong>${iconSafe(finding.label)} <code>${iconSafe(finding.candidate)}</code></strong>
      <p>${iconSafe(finding.message)}</p>
      <p><code>${iconSafe(finding.evidence)}</code></p>
    </div>
  `).join("");
}

function renderTrace() {
  const traceList = document.querySelector("#traceList");
  const model = state.result?.reference_model;
  if (!model) {
    traceList.innerHTML = `<div class="trace-item"><strong>Reference model empty</strong><p>Protected relations, entities, numbers, and units appear here after a run.</p></div>`;
    return;
  }

  const relationRows = (model.relations || []).slice(0, 6).map((relation) =>
    `<div class="trace-item"><strong>${iconSafe(relation.predicate)} <code>${iconSafe(relation.subject)} -> ${iconSafe(relation.object)}</code></strong><p>Protected relation extracted from supplied references.</p></div>`
  );
  const literalRow = `<div class="trace-item"><strong>Literals <code>${model.numbers.length} numbers / ${model.units.length} units</code></strong><p>${iconSafe([...model.numbers, ...model.units].join(", ") || "No protected literals extracted.")}</p></div>`;
  traceList.innerHTML = [...relationRows, literalRow].join("");
}

function renderSuite() {
  const result = state.suiteResult;
  const summary = result?.summary || {};
  const status = state.suiteLoading ? "RUNNING" : (result?.status || "READY");
  const statusClass = status === "PASS" ? "verified" : status === "READY" || status === "RUNNING" ? "neutral" : "warn";
  const evidenceStatus = publicSandboxActive()
    ? "Admin only"
    : result
      ? `${result.cases.filter((item) => item.evidence).length} saved`
      : "Ready";

  document.querySelector("#suiteStatus").innerHTML = `<span class="integrity-chip ${statusClass}">${iconSafe(status)}</span>`;
  document.querySelector("#suiteCases").textContent = summary.case_count ?? "--";
  document.querySelector("#suitePassed").textContent = summary.passed ?? "--";
  document.querySelector("#suiteFailed").textContent = summary.failed ?? "--";
  document.querySelector("#suiteEvidenceStatus").textContent = evidenceStatus;
  suiteProofNote.innerHTML = result
    ? `Observed: <strong>${iconSafe(status)}</strong>, <strong>${iconSafe(summary.case_count ?? "--")}</strong> cases, <strong>${iconSafe(summary.passed ?? "--")}</strong> passed, <strong>${iconSafe(summary.failed ?? "--")}</strong> failed.`
    : `Public proof target: <strong>PASS</strong>, <strong>5</strong> cases, <strong>5</strong> passed, <strong>0</strong> failed.`;

  if (state.suiteLoading) {
    suiteTable.innerHTML = `<tr><td colspan="5">Running the release gate...</td></tr>`;
    return;
  }
  if (!result) {
    suiteTable.innerHTML = `<tr><td colspan="5">No suite run yet.</td></tr>`;
    return;
  }

  suiteTable.innerHTML = result.cases.map((item) => {
    const chipClass = item.status === "PASS" ? "verified" : "warn";
    const evidenceLabel = item.evidence && item.check_id ? `<code>${iconSafe(item.check_id)}</code>` : "not saved";
    return `
      <tr>
        <td>${iconSafe(item.name || item.id)}</td>
        <td><span class="integrity-chip ${chipClass}">${iconSafe(item.status)}</span></td>
        <td>${iconSafe(item.action || "ERROR")}</td>
        <td>${iconSafe(item.highest_risk_score ?? "--")}</td>
        <td>${evidenceLabel}</td>
      </tr>
    `;
  }).join("");
}

function renderHistory() {
  const history = state.auditHistory;
  exportBundleButton.disabled = publicSandboxActive();
  historyCue.textContent = publicSandboxActive()
    ? "Public users can run the sandbox, but saved evidence and bundle export require the admin API key."
    : "Export Bundle downloads saved evidence, verification JSON, manifest counts, and summary.md.";
  if (publicSandboxActive()) {
    historyTable.innerHTML = `<tr><td colspan="6">Admin-only evidence history is locked in public sandbox mode.</td></tr>`;
    return;
  }
  if (!history.length) {
    historyTable.innerHTML = `<tr><td colspan="6">No saved evidence packs yet.</td></tr>`;
    return;
  }
  historyTable.innerHTML = history.map((item) => `
    <tr class="${state.selectedEvidenceId === item.check_id ? "selected-row" : ""}">
      <td>
        <button class="link-button" type="button" data-evidence-id="${iconSafe(item.check_id)}">
          <code>${iconSafe(item.check_id)}</code>
        </button>
      </td>
      <td>${iconSafe(item.action)}</td>
      <td>${iconSafe(item.emitted)}</td>
      <td>${iconSafe(item.risk)}</td>
      <td>${iconSafe(item.blocked)}</td>
      <td><span class="integrity-chip ${item.integrity_valid ? "verified" : "warn"}">${item.integrity_valid ? "Verified" : "Check"}</span></td>
    </tr>
  `).join("");
}

function renderEvidenceInspector() {
  const pack = state.selectedEvidence;
  exportEvidenceButton.disabled = !pack;
  if (publicSandboxActive()) {
    exportEvidenceButton.disabled = true;
    evidenceInspector.innerHTML = `<div class="inspector-empty"><strong>Admin evidence locked</strong><p>Public sandbox runs do not expose saved audit history, single-pack downloads, or evidence bundles. Unlock with the admin API key to inspect packs.</p></div>`;
    return;
  }
  if (state.evidenceLoading) {
    evidenceInspector.innerHTML = `<div class="inspector-empty"><strong>Loading evidence pack</strong><p>Fetching the selected local audit artifact.</p></div>`;
    return;
  }
  if (!pack) {
    evidenceInspector.innerHTML = `<div class="inspector-empty"><strong>No evidence selected</strong><p>Choose a recent check to inspect its digest, request hashes, and gateway decision.</p></div>`;
    return;
  }

  const request = pack.request || {};
  const result = pack.result || {};
  const summary = result.summary || {};
  const integrity = pack.integrity || {};
  const hashes = pack.request_hashes || {};
  const verification = pack.verification || {};
  const verifiedHashes = verification.request_hashes || {};
  const provider = request.provider || result.provider || "local";
  const model = request.model || result.model || "not recorded";
  const action = pack.gateway_action || result.action || "UNKNOWN";
  const digest = integrity.digest || "not available";
  const verdictClass = pack.integrity_valid ? "verified" : "warn";

  evidenceInspector.innerHTML = `
    <div class="inspector-status">
      <span class="integrity-chip ${verdictClass}">${pack.integrity_valid ? "Integrity verified" : "Integrity check needed"}</span>
      <code>${iconSafe(pack.check_id)}</code>
    </div>
    <div class="inspector-grid">
      <div>
        <span>Action</span>
        <strong>${iconSafe(action)}</strong>
      </div>
      <div>
        <span>Policy</span>
        <strong>${iconSafe(request.policy_profile || "default")}</strong>
      </div>
      <div>
        <span>Provider</span>
        <strong>${iconSafe(provider)}</strong>
      </div>
      <div>
        <span>Model</span>
        <strong>${iconSafe(model)}</strong>
      </div>
    </div>
    <div class="hash-block">
      <span>Pack digest</span>
      <code>${iconSafe(digest)}</code>
    </div>
    <div class="hash-list">
      ${renderHashRow("References", hashes.references_sha256, verifiedHashes.references_sha256?.valid)}
      ${renderHashRow("Candidates", hashes.candidates_sha256, verifiedHashes.candidates_sha256?.valid)}
      ${renderHashRow("Policy", hashes.policy_sha256, verifiedHashes.policy_sha256?.valid)}
    </div>
    <div class="inspector-summary">
      <p><strong>${iconSafe(summary.blocked_count ?? 0)}</strong> blocked of <strong>${iconSafe(summary.candidate_count ?? 0)}</strong> candidates.</p>
      <p>Highest risk <strong>${iconSafe(summary.highest_risk_score ?? "--")}</strong>. Emitted <code>${iconSafe(result.emitted_candidate_id || "none")}</code>.</p>
    </div>
  `;
}

function renderHashRow(label, value, valid) {
  const chipClass = valid === false ? "warn" : "verified";
  const chipLabel = valid === false ? "Mismatch" : "Verified";
  return `
    <div class="hash-row">
      <span>${iconSafe(label)}</span>
      <code>${iconSafe(value || "not available")}</code>
      <span class="integrity-chip ${chipClass}">${chipLabel}</span>
    </div>
  `;
}

async function loadPolicies() {
  const response = await apiFetch("/api/policies");
  const payload = await response.json();
  state.policies = payload.policies || [];
  policySelect.innerHTML = state.policies.map((policy) =>
    `<option value="${iconSafe(policy.id)}">${iconSafe(policy.name)}</option>`
  ).join("");
}

async function loadProviders() {
  const response = await apiFetch("/api/providers");
  const payload = await response.json();
  state.providers = payload.providers || [];
  providerSelect.innerHTML = state.providers.map((provider) =>
    `<option value="${iconSafe(provider.id)}">${iconSafe(provider.name)}</option>`
  ).join("");
}

async function refreshAuditHistory() {
  if (publicSandboxActive()) {
    state.auditHistory = [];
    return;
  }
  try {
    const response = await apiFetch("/api/audits?limit=8");
    const payload = await response.json();
    state.auditHistory = payload.audits || [];
  } catch {
    state.auditHistory = [];
  }
}

async function loadEvidencePack(checkId) {
  if (!checkId) return;
  if (publicSandboxActive()) {
    state.selectedEvidence = null;
    state.selectedEvidenceId = "";
    return;
  }
  state.evidenceLoading = true;
  state.selectedEvidenceId = checkId;
  renderHistory();
  renderEvidenceInspector();
  try {
    const response = await apiFetch(`/api/audits/${encodeURIComponent(checkId)}`);
    const payload = await response.json();
    if (payload.error) {
      throw new Error(payload.error);
    }
    state.selectedEvidence = payload;
  } catch (error) {
    if (error.message !== "unauthorized") {
      state.selectedEvidence = null;
      alert(`Evidence pack failed to load: ${error.message}`);
    }
  } finally {
    state.evidenceLoading = false;
    renderHistory();
    renderEvidenceInspector();
  }
}

async function runDemoSuite() {
  setSuiteButtonsLoading(true);
  state.suiteLoading = true;
  renderSuite();
  try {
    const suiteResponse = await apiFetch("/api/demo-suite");
    const suitePayload = await suiteResponse.json();
    const response = await apiFetch("/api/suite", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(suitePayload),
    });
    const result = await response.json();
    if (result.error) {
      throw new Error(result.detail || result.error);
    }
    state.suiteResult = result;
    await refreshAuditHistory();
    const firstEvidence = result.cases.find((item) => item.check_id);
    if (firstEvidence && !publicSandboxActive()) {
      await loadEvidencePack(firstEvidence.check_id);
    }
    renderAll();
  } catch (error) {
    if (error.message !== "unauthorized") {
      alert(`Suite failed: ${error.message}`);
    }
  } finally {
    state.suiteLoading = false;
    setSuiteButtonsLoading(false);
    renderSuite();
  }
}

function setSuiteButtonsLoading(loading) {
  const label = loading ? "Running..." : "Run Demo Suite";
  const icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>';
  for (const button of [suiteButton, topSuiteButton]) {
    if (!button) continue;
    button.disabled = loading;
    button.innerHTML = `${icon}${label}`;
  }
}

async function loadHealth() {
  const response = await fetch("/api/health");
  const payload = await response.json();
  state.authRequired = Boolean(payload.auth_required);
  state.publicDemo = Boolean(payload.public_demo);
  state.adminAuthConfigured = Boolean(payload.admin_auth_configured);
}

async function apiFetch(url, options = {}) {
  const headers = new Headers(options.headers || {});
  if (state.apiKey) {
    headers.set("Authorization", `Bearer ${state.apiKey}`);
  }
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    showAuthRequired();
    throw new Error("unauthorized");
  }
  return response;
}

function showAuthRequired() {
  const label = document.querySelector("#verdictLabel");
  const checkId = document.querySelector("#checkId");
  const headline = document.querySelector("#verdictHeadline");
  const summary = document.querySelector("#verdictSummary");
  label.textContent = "LOCKED";
  label.className = "verdict-label block";
  checkId.textContent = "API key required";
  headline.textContent = "Enter the Sentinel API key.";
  summary.textContent = "This deployment requires an API key before dashboard requests can run.";
}

function syncAuthUi() {
  const sandbox = publicSandboxActive();
  document.body.classList.toggle("public-demo", state.publicDemo);
  document.body.classList.toggle("public-sandbox", sandbox);
  sandboxBadge.hidden = !state.publicDemo;
  unlockButton.hidden = !state.authRequired;
  apiKeyInput.placeholder = state.publicDemo ? "Admin key" : "Optional locally";
  generateButton.hidden = sandbox;
  providerSelect.disabled = sandbox;
  modelInput.disabled = sandbox;
  sandboxLockCue.hidden = !sandbox;
  if (sandbox) {
    state.provider = "local_demo";
    state.model = "sentinel-demo-v1";
    providerSelect.value = state.provider;
    modelInput.value = state.model;
  }
  railStatusLabel.textContent = sandbox ? "Public sandbox" : "Local gateway online";
  document.querySelector("#proofSandbox").textContent = sandbox ? "Public sandbox" : "Admin/local mode";
}

async function bootstrapDashboard() {
  if (bootstrapping) return;
  bootstrapping = true;
  unlockButton.disabled = true;
  try {
    await Promise.all([loadPolicies(), loadProviders(), refreshAuditHistory()]);
    syncAuthUi();
    await loadDemo();
    await runCheck();
  } catch (error) {
    if (error.message !== "unauthorized") {
      alert(`Dashboard failed to load: ${error.message}`);
    }
  } finally {
    bootstrapping = false;
    unlockButton.disabled = false;
  }
}

function renderAll() {
  renderCandidates();
  renderVerdict();
  renderFindings();
  renderTrace();
  renderHistory();
  renderEvidenceInspector();
  renderSuite();
}

function clearInputs() {
  state.references = [];
  state.candidates = [
    { id: "candidate-a", label: "Candidate A", text: "" },
    { id: "candidate-b", label: "Candidate B", text: "" },
    { id: "candidate-c", label: "Candidate C", text: "" },
  ];
  state.result = null;
  syncForm();
  renderAll();
}

function exportResult() {
  if (!state.result) return;
  const blob = new Blob([JSON.stringify(state.result, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${state.result.check_id}.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function exportEvidencePack() {
  if (!state.selectedEvidence) return;
  const blob = new Blob([JSON.stringify(state.selectedEvidence, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${state.selectedEvidence.check_id}.evidence.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function exportEvidenceBundle() {
  exportBundleButton.disabled = true;
  exportBundleButton.textContent = "Exporting...";
  try {
    const response = await apiFetch("/api/audits/export?limit=25");
    if (!response.ok) {
      throw new Error(`export failed with ${response.status}`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "sentinel-evidence-bundle.zip";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch (error) {
    if (error.message !== "unauthorized") {
      alert(`Evidence bundle failed to export: ${error.message}`);
    }
  } finally {
    exportBundleButton.disabled = publicSandboxActive();
    exportBundleButton.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M7 10l5 5 5-5"/><path d="M5 21h14"/></svg>Export Bundle';
  }
}

document.querySelectorAll(".segment").forEach((button) => {
  button.addEventListener("click", () => {
    state.mode = button.dataset.mode;
    syncForm();
  });
});

for (const key of Object.keys(state.policy)) {
  document.querySelector(`#${key}`).addEventListener("change", readForm);
}

policySelect.addEventListener("change", () => {
  state.policyProfile = policySelect.value;
});
apiKeyInput.value = state.apiKey;
apiKeyInput.addEventListener("input", () => {
  state.apiKey = apiKeyInput.value.trim();
  if (state.apiKey) {
    sessionStorage.setItem("sentinel-api-key", state.apiKey);
  } else {
    sessionStorage.removeItem("sentinel-api-key");
  }
  syncAuthUi();
});
apiKeyInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && state.apiKey) {
    bootstrapDashboard();
  }
});
unlockButton.addEventListener("click", bootstrapDashboard);
providerSelect.addEventListener("change", () => {
  state.provider = providerSelect.value;
  const provider = state.providers.find((item) => item.id === state.provider);
  if (provider?.default_model) {
    state.model = provider.default_model;
    modelInput.value = provider.default_model;
  }
});
runButton.addEventListener("click", runCheck);
generateButton.addEventListener("click", runGenerateCheck);
suiteButton.addEventListener("click", runDemoSuite);
topSuiteButton.addEventListener("click", runDemoSuite);
loadDemoButton.addEventListener("click", () => {
  loadDemo().catch((error) => {
    if (error.message !== "unauthorized") {
      alert(`Demo failed to load: ${error.message}`);
    }
  });
});
clearButton.addEventListener("click", clearInputs);
exportButton.addEventListener("click", exportResult);
exportBundleButton.addEventListener("click", exportEvidenceBundle);
exportEvidenceButton.addEventListener("click", exportEvidencePack);
historyTable.addEventListener("click", (event) => {
  const button = event.target.closest("[data-evidence-id]");
  if (button) {
    loadEvidencePack(button.dataset.evidenceId);
  }
});

loadHealth()
  .then(() => {
    syncAuthUi();
    if (state.authRequired && !state.apiKey && !state.publicDemo) {
      renderAll();
      showAuthRequired();
      return null;
    }
    return bootstrapDashboard();
  });

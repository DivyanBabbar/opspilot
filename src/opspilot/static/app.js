const $ = (id) => document.getElementById(id);
const status = $("status");

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function setStatus(message, state = "ready") {
  status.textContent = message;
  status.dataset.state = state;
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(typeof data.detail === "string" ? data.detail : "The request could not be completed.");
  }
  return data;
}

async function runAction(button, pending, success, action) {
  button.disabled = true;
  setStatus(pending, "busy");
  try {
    await action();
    setStatus(success);
  } catch (error) {
    setStatus(error.message || "The action failed. Try again.", "error");
  } finally {
    button.disabled = false;
  }
}

function renderIncident(incident) {
  const plan = incident.plan;
  const actions = plan
    ? `<div class="actions">
        ${plan.status === "proposed" ? `<button class="approve" type="button" data-action="approve" data-id="${escapeHtml(incident.incident_id)}">Approve plan</button>` : ""}
        ${plan.status === "approved" ? `<button class="execute" type="button" data-action="execute" data-id="${escapeHtml(incident.incident_id)}">Execute simulation</button>` : ""}
        <span class="tag">${escapeHtml(plan.status)}</span>
      </div>`
    : "";
  const planDetails = plan
    ? `<p><b>${escapeHtml(plan.action.replaceAll("_", " "))}</b> · ${escapeHtml(plan.reason)}</p><p>${escapeHtml(plan.impact)}</p>${actions}`
    : "";

  return `<article class="card">
    <span class="tag">${escapeHtml(incident.state.replaceAll("_", " "))}</span>
    <h3>${escapeHtml(incident.service)}</h3>
    <p>${escapeHtml(incident.root_cause_lead)}</p>
    <div class="bar" role="meter" aria-label="Anomaly score" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${Math.round(incident.anomaly_score * 100)}"><i style="width:${Math.round(incident.anomaly_score * 100)}%"></i></div>
    <p>ANOMALY SCORE · ${Math.round(incident.anomaly_score * 100)}%</p>
    ${planDetails}
  </article>`;
}

async function refresh() {
  const incidents = await request("/v1/incidents");
  $("count").textContent = String(incidents.length);
  $("incidents").innerHTML = incidents.length
    ? incidents.map(renderIncident).join("")
    : '<div class="empty">No incidents yet. Load the synthetic incident to explore the workflow.</div>';
}

$("incidents").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const action = button.dataset.action;
  runAction(
    button,
    action === "approve" ? "Recording operator approval…" : "Running the simulated response…",
    action === "approve" ? "Plan approved. Review it again before running the simulation." : "Simulation complete. No infrastructure API was called.",
    async () => {
      await request(`/v1/incidents/${encodeURIComponent(button.dataset.id)}/${action}`, { method: "POST" });
      await refresh();
    },
  );
});

$("demo").addEventListener("click", (event) => {
  runAction(
    event.currentTarget,
    "Creating the synthetic 5xx incident…",
    "Demo incident loaded. Review its evidence and proposed action.",
    async () => {
      await request("/v1/demo/load", { method: "POST" });
      await refresh();
    },
  );
});

$("refresh").addEventListener("click", (event) => {
  runAction(event.currentTarget, "Refreshing the incident queue…", "Incident queue is up to date.", refresh);
});

$("submit").addEventListener("click", (event) => {
  runAction(
    event.currentTarget,
    "Scoring the service signal…",
    "Signal analyzed. Review the new incident in the queue.",
    async () => {
      await request("/v1/signals", {
        method: "POST",
        body: JSON.stringify({
          timestamp: new Date().toISOString(),
          service: $("service").value.trim(),
          metric: $("metric").value.trim(),
          value: Number($("value").value),
          baseline: Number($("baseline").value),
          severity: $("severity").value,
        }),
      });
      await refresh();
    },
  );
});

refresh().catch((error) => setStatus(error.message || "Could not load incidents.", "error"));

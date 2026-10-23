# OpsPilot — Self-Healing Infrastructure Agent

OpsPilot demonstrates an end-to-end incident response loop: ingest an observability signal, score anomalies, create a bounded remediation proposal, require operator approval, then execute a simulated action through an idempotent gate.

![CI](https://github.com/DivyanBabbar/opspilot/actions/workflows/ci.yml/badge.svg)

## What it demonstrates

- Typed signal ingestion and severity-aware anomaly scoring
- Incident state machine with evidence and proposed root-cause lead
- Remediation selection for rollback, scale-out, or restart patterns
- Explicit approval before execution
- SQLite persistence, idempotency keys, audit-ready action states
- A responsive operator dashboard and synthetic incident flow
- FastAPI/OpenAPI, Docker Compose, tests, Ruff, and CodeQL

## Quick start

```bash
git clone https://github.com/DivyanBabbar/opspilot.git
cd opspilot
python -m venv .venv
# Activate the environment, then:
pip install -e '.[dev]'
opspilot
```

Visit <http://127.0.0.1:8000> and click **Load demo incident**. The incident page shows the anomaly evidence, score, recommended action, and its state. Approve the plan, then execute the simulation. API documentation is at `/docs`.

### 2–5 minute demo

1. Click **Load demo incident** to create a synthetic 5xx spike.
2. Review the score, proposed rollback, and evidence in the incident card.
3. Approve the plan, then run the simulation and confirm its completed state.
4. Submit a custom signal from the side panel to explore the other remediation rules.

The service runs locally without provider credentials. To override the storage directory, copy `.env.example` to `.env` and edit `OPSPILOT_DATA_DIR`.

With Docker: `docker compose up --build`.

## API workflow

1. `POST /v1/signals` with a service metric, observation, and baseline.
2. Review the returned incident and proposed remediation.
3. `POST /v1/incidents/{incident_id}/approve` to approve.
4. `POST /v1/incidents/{incident_id}/execute` to run the idempotent simulator.
5. `GET /v1/incidents` to review recent incident state.

`POST /v1/demo/load` adds a synthetic 5xx spike.

## Safety and deployment boundary

The included executor **only records a simulated result**. It does not connect to Kubernetes, AWS, or any production system. An infrastructure adapter must implement least-privilege credentials, explicit action and namespace allowlists, timeouts, dry-run, rollback, audit logging, and a second approval policy before any live remediation is appropriate. The API has no authentication and should stay on localhost or a trusted development network.

## Scoring

Anomaly score combines normalized deviation from the supplied baseline with severity. A threshold determines whether to propose a plan. This transparent heuristic is intentionally easy to inspect; it is not a learned model and its score is not a probability. Production use needs metric-specific seasonality, robust baselines, deduplication, suppression windows, and service-aware thresholds.

## Configuration

`OPSPILOT_DATA_DIR` controls SQLite storage and defaults to `data`.

## Development

```bash
pip install -e '.[dev]'
ruff check .
ruff format --check .
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md). MIT licensed.

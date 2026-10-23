import pytest
from fastapi.testclient import TestClient
from opspilot import storage
from opspilot.api import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage.settings, "data_dir", str(tmp_path))
    with TestClient(app) as c:
        yield c


def test_requires_approval_and_execution_is_idempotent(client):
    incident = client.post("/v1/demo/load").json()
    iid = incident["incident_id"]
    assert client.post(f"/v1/incidents/{iid}/execute").status_code == 409
    assert client.post(f"/v1/incidents/{iid}/approve").status_code == 200
    first = client.post(f"/v1/incidents/{iid}/execute")
    assert first.status_code == 200 and first.json()["execution"] == "simulated"
    assert "No cloud" in first.json()["message"]
    assert client.post(f"/v1/incidents/{iid}/execute").status_code == 409


def test_dashboard_serves_its_branding_and_interaction_assets(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "Respond with" in page.text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/polish.css").status_code == 200


def test_signal_api_rejects_non_finite_values(client):
    response = client.post(
        "/v1/signals",
        content=(
            '{"timestamp":"2026-10-23T10:00:00Z","service":"checkout-api",'
            '"metric":"http_5xx_rate","value":NaN,"baseline":0.01}'
        ),
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 422

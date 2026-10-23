from datetime import UTC, datetime
from opspilot.engine import detect, choose_remediation
from opspilot.models import Signal


def signal(metric="cpu_utilization", value=0.99, baseline=0.2, severity="critical"):
    return Signal(
        timestamp=datetime.now(UTC),
        service="checkout",
        metric=metric,
        value=value,
        baseline=baseline,
        severity=severity,
    )


def test_detects_significant_anomaly():
    score, anomaly = detect(signal())
    assert anomaly and score > 0.55


def test_chooses_rollback_for_error_spike():
    assert choose_remediation(signal("http_5xx_rate"))[0] == "rollback"


def test_normal_signal_is_observing(client):
    response = client.post("/v1/signals", json=signal(value=0.2, severity="info").model_dump(mode="json"))
    assert response.status_code == 200 and response.json()["state"] == "observing"

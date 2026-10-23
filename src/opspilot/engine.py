from opspilot.models import Signal


def detect(signal: Signal) -> tuple[float, bool]:
    denominator = max(abs(signal.baseline), 0.01)
    deviation = abs(signal.value - signal.baseline) / denominator
    severity_weight = {"info": 0.2, "warning": 0.65, "critical": 1.0}[signal.severity]
    score = min(1.0, deviation / 2.0 * 0.75 + severity_weight * 0.25)
    return round(score, 3), score >= 0.55


def choose_remediation(signal: Signal) -> tuple[str, str]:
    metric = signal.metric.lower()
    if "error" in metric or "5xx" in metric or "crash" in metric:
        return "rollback", "Rollback is proposed because errors rose above baseline."
    if "cpu" in metric or "queue" in metric or "latency" in metric:
        return "scale_out", "Scale out is proposed to reduce saturation and queue pressure."
    return "restart", "A bounded restart is proposed for the unhealthy service."

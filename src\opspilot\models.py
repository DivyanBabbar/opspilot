from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
class Signal(BaseModel):
    timestamp: datetime
    service: str = Field(min_length=1,max_length=120)
    metric: str = Field(min_length=1,max_length=120)
    value: float
    baseline: float
    severity: Literal["info","warning","critical"] = "warning"
    message: str = Field(default="",max_length=1000)
class RemediationPlan(BaseModel):
    plan_id: str
    service: str
    action: Literal["restart","scale_out","rollback"]
    reason: str
    impact: str
    requires_approval: bool = True
    status: Literal["proposed","approved","executed","rejected"] = "proposed"
    idempotency_key: str
class Incident(BaseModel):
    incident_id: str
    service: str
    state: Literal["observing","investigating","remediation_proposed","resolved"]
    anomaly_score: float
    signals: list[Signal]
    root_cause_lead: str
    plan: RemediationPlan | None = None

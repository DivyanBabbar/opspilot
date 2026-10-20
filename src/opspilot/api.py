import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from opspilot.models import Incident, RemediationPlan, Signal
from opspilot.engine import detect, choose_remediation
from opspilot.storage import get_incident, initialize, list_incidents, save_incident, claim_action
app=FastAPI(title="OpsPilot",version="1.0.0",description="Safety-gated self-healing infrastructure workflows.")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
@app.on_event("startup")
def startup(): initialize()
@app.get("/",include_in_schema=False)
def home(): return FileResponse(Path(__file__).parent / "static" / "index.html")
@app.get("/health")
def health(): return {"status":"ok","service":"opspilot"}
@app.get("/v1/incidents")
def incidents(): return list_incidents()
@app.post("/v1/signals")
def ingest(signal:Signal):
    score,anomaly=detect(signal)
    incident_id=str(uuid.uuid4()); plan=None
    if anomaly:
        action,reason=choose_remediation(signal)
        plan=RemediationPlan(plan_id=str(uuid.uuid4()),service=signal.service,action=action,reason=reason,impact="Simulated action only; no infrastructure connector is configured.",idempotency_key=f"{incident_id}:{action}")
    incident=Incident(incident_id=incident_id,service=signal.service,state="remediation_proposed" if plan else "observing",anomaly_score=score,signals=[signal],root_cause_lead=f"{signal.metric} deviated {abs(signal.value-signal.baseline)/max(abs(signal.baseline),0.01):.1%} from its supplied baseline.",plan=plan)
    save_incident(incident); return incident
@app.get("/v1/incidents/{incident_id}")
def incident(incident_id:str):
    row=get_incident(incident_id)
    if not row: raise HTTPException(404,"Incident not found")
    return row
@app.post("/v1/incidents/{incident_id}/approve")
def approve(incident_id:str):
    row=get_incident(incident_id)
    if not row: raise HTTPException(404,"Incident not found")
    if not row.get("plan"): raise HTTPException(409,"No remediation plan is available")
    if row["plan"]["status"] != "proposed": raise HTTPException(409,"Plan is no longer awaiting approval")
    row["plan"]["status"]="approved"; save_incident(Incident.model_validate(row)); return row
@app.post("/v1/incidents/{incident_id}/execute")
def execute(incident_id:str):
    row=get_incident(incident_id)
    if not row: raise HTTPException(404,"Incident not found")
    plan=row.get("plan")
    if not plan or plan["status"]!="approved": raise HTTPException(409,"Approve the remediation plan first")
    # Deliberately simulate; connector adapters are not enabled by default.
    if not claim_action(plan["idempotency_key"],plan["plan_id"]): raise HTTPException(409,"This idempotency key was already executed")
    plan["status"]="executed"; row["state"]="resolved"; save_incident(Incident.model_validate(row)); return {"incident":row,"execution":"simulated","message":"No cloud or cluster API was called."}
@app.post("/v1/demo/load")
def demo():
    now=datetime.now(UTC)
    return ingest(Signal(timestamp=now,service="checkout-api",metric="http_5xx_rate",value=0.21,baseline=0.01,severity="critical",message="Synthetic error spike after release"))

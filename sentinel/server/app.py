from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import uuid

from sentinel.schemas.incident import TelemetryAlert, IncidentRecord, IncidentStatus, SeverityLevel
from sentinel.agent.orchestrator import SREOrchestrator

app = FastAPI(
    title="Sentinel-Kernel API",
    description="Autonomous SRE & Self-Healing Incident Agent",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

incidents_db: Dict[str, IncidentRecord] = {}
orchestrator = SREOrchestrator()

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Sentinel-Kernel Engine"}

@app.get("/api/incidents", response_model=List[IncidentRecord])
def get_incidents():
    return list(incidents_db.values())

@app.get("/api/incidents/{incident_id}", response_model=IncidentRecord)
def get_incident(incident_id: str):
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incidents_db[incident_id]

@app.post("/api/alerts/webhook", response_model=IncidentRecord)
def trigger_alert(alert: TelemetryAlert):
    incident = orchestrator.remediate(alert)
    incidents_db[incident.incident_id] = incident
    return incident

@app.post("/api/simulation/sample-incident", response_model=IncidentRecord)
def trigger_sample_incident():
    sample_alert = TelemetryAlert(
        alert_id=str(uuid.uuid4())[:8],
        service_name="payment-gateway-v2",
        error_name="StripeConnectionDeadlockError",
        message="Critical deadlock detected during asynchronous settlement transaction.",
        stack_trace='File "payment_service.py", line 42, in handle_request',
        telemetry_tags={"region": "us-east-1", "cluster": "prod-k8s-01"}
    )
    incident = orchestrator.remediate(sample_alert)
    incidents_db[incident.incident_id] = incident
    return incident

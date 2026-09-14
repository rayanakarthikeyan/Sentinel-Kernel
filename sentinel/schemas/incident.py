from pydantic import BaseModel, Field
import os
import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class SeverityLevel(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGING = "TRIAGING"
    ANALYZING_RCA = "ANALYZING_RCA"
    SANDBOX_REPRODUCING = "SANDBOX_REPRODUCING"
    SYNTHESIZING_PATCH = "SYNTHESIZING_PATCH"
    VERIFYING_TESTS = "VERIFYING_TESTS"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"

class TelemetryAlert(BaseModel):
    alert_id: str
    service_name: str
    error_name: str
    message: str
    stack_trace: Optional[str] = None
    telemetry_tags: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class CodeDiff(BaseModel):
    file_path: str
    original_code: str
    patched_code: str
    unified_diff: str

class TestExecutionResult(BaseModel):
    command: str
    passed: bool
    exit_code: int
    duration_sec: float
    output: str
    error_summary: Optional[str] = None

class IncidentRecord(BaseModel):
    incident_id: str
    title: str
    severity: SeverityLevel
    status: IncidentStatus
    alert: TelemetryAlert
    root_cause_hypothesis: Optional[str] = None
    target_file: Optional[str] = None
    reproduction_test_code: Optional[str] = None
    reproduction_result: Optional[TestExecutionResult] = None
    proposed_diff: Optional[CodeDiff] = None
    verification_result: Optional[TestExecutionResult] = None
    post_mortem_markdown: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    resolved_at: Optional[datetime.datetime] = None

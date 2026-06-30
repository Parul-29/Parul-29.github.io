from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ExperimentStatus(str, Enum):
    planned = "planned"
    running = "running"
    completed = "completed"
    aborted = "aborted"


class FailureType(str, Enum):
    service_crash = "service_crash"
    latency_injection = "latency_injection"
    network_partition = "network_partition"
    dependency_outage = "dependency_outage"
    cpu_pressure = "cpu_pressure"
    memory_pressure = "memory_pressure"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ExperimentTarget(BaseModel):
    service: str = Field(..., examples=["checkout-api"])
    environment: str = Field(default="staging")
    namespace: str | None = Field(default=None)
    replicas: int = Field(default=3, ge=1)
    criticality: RiskLevel = Field(default=RiskLevel.medium)


class SteadyStateHypothesis(BaseModel):
    availability_percent: float = Field(default=99.0, ge=0, le=100)
    p95_latency_ms: int = Field(default=500, ge=1)
    error_rate_percent: float = Field(default=1.0, ge=0, le=100)
    minimum_healthy_replicas: int = Field(default=2, ge=0)


class Guardrail(BaseModel):
    name: str
    threshold: float
    unit: str
    abort_on_breach: bool = True


class ExperimentRequest(BaseModel):
    title: str = Field(..., examples=["Checkout API latency resilience"])
    target: ExperimentTarget
    failure_type: FailureType
    duration_seconds: int = Field(default=300, ge=30, le=3600)
    blast_radius_percent: int = Field(default=25, ge=1, le=100)
    hypothesis: SteadyStateHypothesis = Field(default_factory=SteadyStateHypothesis)
    guardrails: list[Guardrail] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MetricSample(BaseModel):
    availability_percent: float = Field(ge=0, le=100)
    p95_latency_ms: int = Field(ge=0)
    error_rate_percent: float = Field(ge=0, le=100)
    healthy_replicas: int = Field(ge=0)
    detection_time_seconds: int = Field(ge=0)
    recovery_time_seconds: int = Field(ge=0)


class ExperimentFinding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    risk_level: RiskLevel
    description: str
    recommendation: str
    metric: str | None = None


class ExperimentResponse(BaseModel):
    experiment_id: str
    status: ExperimentStatus
    request: ExperimentRequest
    resilience_score: int = Field(default=0, ge=0, le=100)
    steady_state_passed: bool = False
    guardrail_breached: bool = False
    findings: list[ExperimentFinding] = Field(default_factory=list)
    observed_metrics: MetricSample | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

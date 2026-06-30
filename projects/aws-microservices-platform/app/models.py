from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Environment(str, Enum):
    dev = "dev"
    staging = "staging"
    prod = "prod"


class DeploymentStatus(str, Enum):
    planned = "planned"
    deployed = "deployed"
    failed = "failed"


class Exposure(str, Enum):
    internal = "internal"
    public = "public"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ServiceSpec(BaseModel):
    name: str = Field(..., examples=["orders-api"])
    image: str = Field(..., examples=["123456789012.dkr.ecr.us-west-2.amazonaws.com/orders-api:v1"])
    replicas: int = Field(default=2, ge=1, le=50)
    cpu_millicores: int = Field(default=250, ge=50)
    memory_mb: int = Field(default=512, ge=128)
    port: int = Field(default=8080, ge=1, le=65535)
    exposure: Exposure = Field(default=Exposure.internal)
    autoscaling_enabled: bool = True


class PlatformRequest(BaseModel):
    platform_name: str = Field(..., examples=["commerce-platform"])
    environment: Environment = Field(default=Environment.staging)
    aws_region: str = Field(default="us-west-2")
    eks_cluster: str
    vpc_id: str
    services: list[ServiceSpec] = Field(default_factory=list)
    enable_observability: bool = True
    enable_kms_encryption: bool = True
    enable_irsa: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class PlatformFinding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    risk_level: RiskLevel
    description: str
    recommendation: str
    service: str | None = None


class DeploymentPlan(BaseModel):
    namespace: str
    ecr_repositories: list[str]
    kubernetes_manifests: list[str]
    terraform_modules: list[str]
    observability_dashboards: list[str]
    iam_roles: list[str]


class PlatformResponse(BaseModel):
    deployment_id: str
    status: DeploymentStatus
    request: PlatformRequest
    plan: DeploymentPlan
    readiness_score: int = Field(ge=0, le=100)
    findings: list[PlatformFinding] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

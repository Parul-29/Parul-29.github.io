from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class FindingCategory(str, Enum):
    vulnerability = "vulnerability"
    misconfiguration = "misconfiguration"
    compliance = "compliance"


class ScanStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ActionRoute(str, Enum):
    auto_fix = "auto_fix"
    backlog = "backlog"
    human_review = "human_review"


class ScanRequest(BaseModel):
    repository: str = Field(..., examples=["Parul-29/sample-service"])
    branch: str = Field(default="main")
    commit_sha: str | None = Field(default=None)
    pull_request: int | None = Field(default=None)
    changed_files: list[str] = Field(default_factory=list)
    source_snapshot: dict[str, str] = Field(
        default_factory=dict,
        description="Optional file path to content map. Used by built-in scanners.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent: str
    category: FindingCategory
    title: str
    description: str
    severity: Severity
    file_path: str | None = None
    line: int | None = None
    evidence: str | None = None
    recommendation: str
    confidence: float = Field(ge=0, le=1, default=0.75)
    risk_score: int = Field(ge=0, le=100, default=0)
    route: ActionRoute = ActionRoute.backlog
    cwe: str | None = None
    control: str | None = None

    def dedupe_key(self) -> tuple[str, str | None, str, str]:
        return (self.category.value, self.file_path, self.title.lower(), self.evidence or "")


class AgentResult(BaseModel):
    agent: str
    findings: list[Finding] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    duration_ms: int


class ReasoningSummary(BaseModel):
    executive_summary: str
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    recommended_next_steps: list[str]


class ScanResponse(BaseModel):
    scan_id: str
    status: ScanStatus
    request: ScanRequest
    findings: list[Finding] = Field(default_factory=list)
    agent_results: list[AgentResult] = Field(default_factory=list)
    reasoning: ReasoningSummary | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    errors: list[str] = Field(default_factory=list)

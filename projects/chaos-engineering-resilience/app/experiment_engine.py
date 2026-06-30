from datetime import datetime, timezone
from uuid import uuid4

from app.models import ExperimentRequest, ExperimentResponse, ExperimentStatus, FailureType, MetricSample
from app.resilience import ResilienceAnalyzer


class ExperimentEngine:
    def __init__(self) -> None:
        self.analyzer = ResilienceAnalyzer()

    def plan(self, request: ExperimentRequest) -> ExperimentResponse:
        return ExperimentResponse(
            experiment_id=str(uuid4()),
            status=ExperimentStatus.planned,
            request=request,
        )

    def run(self, request: ExperimentRequest) -> ExperimentResponse:
        metrics = self._simulate_metrics(request)
        score, passed, findings = self.analyzer.evaluate(request, metrics)
        breached = self.analyzer.guardrail_breached(request, metrics)

        return ExperimentResponse(
            experiment_id=str(uuid4()),
            status=ExperimentStatus.aborted if breached else ExperimentStatus.completed,
            request=request,
            resilience_score=score,
            steady_state_passed=passed,
            guardrail_breached=breached,
            findings=findings,
            observed_metrics=metrics,
            completed_at=datetime.now(timezone.utc),
        )

    def _simulate_metrics(self, request: ExperimentRequest) -> MetricSample:
        impact = request.blast_radius_percent / 100
        criticality_factor = {
            "low": 0.7,
            "medium": 1.0,
            "high": 1.25,
            "critical": 1.5,
        }[request.target.criticality.value]

        failure_weight = {
            FailureType.service_crash: 1.0,
            FailureType.latency_injection: 1.25,
            FailureType.network_partition: 1.5,
            FailureType.dependency_outage: 1.4,
            FailureType.cpu_pressure: 1.1,
            FailureType.memory_pressure: 1.2,
        }[request.failure_type]

        degradation = impact * criticality_factor * failure_weight
        healthy_replicas = max(0, round(request.target.replicas * (1 - min(degradation, 0.9))))

        return MetricSample(
            availability_percent=round(max(0, 99.9 - degradation * 8), 2),
            p95_latency_ms=round(request.hypothesis.p95_latency_ms * (1 + degradation)),
            error_rate_percent=round(request.hypothesis.error_rate_percent + degradation * 6, 2),
            healthy_replicas=healthy_replicas,
            detection_time_seconds=round(20 + degradation * 90),
            recovery_time_seconds=round(45 + degradation * 240),
        )

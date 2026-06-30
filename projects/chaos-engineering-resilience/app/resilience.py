from app.models import ExperimentFinding, ExperimentRequest, MetricSample, RiskLevel


class ResilienceAnalyzer:
    def evaluate(self, request: ExperimentRequest, metrics: MetricSample) -> tuple[int, bool, list[ExperimentFinding]]:
        findings: list[ExperimentFinding] = []
        hypothesis = request.hypothesis

        if metrics.availability_percent < hypothesis.availability_percent:
            findings.append(
                ExperimentFinding(
                    title="Availability dropped below steady-state target",
                    risk_level=RiskLevel.high,
                    metric="availability_percent",
                    description=(
                        f"Observed availability was {metrics.availability_percent}% against "
                        f"a target of {hypothesis.availability_percent}%."
                    ),
                    recommendation="Add redundancy, health checks, and traffic failover before increasing the blast radius.",
                )
            )

        if metrics.p95_latency_ms > hypothesis.p95_latency_ms:
            findings.append(
                ExperimentFinding(
                    title="Latency exceeded the resilience threshold",
                    risk_level=RiskLevel.medium,
                    metric="p95_latency_ms",
                    description=(
                        f"Observed p95 latency was {metrics.p95_latency_ms} ms against "
                        f"a target of {hypothesis.p95_latency_ms} ms."
                    ),
                    recommendation="Tune timeouts, circuit breakers, retries, and dependency fallback behavior.",
                )
            )

        if metrics.error_rate_percent > hypothesis.error_rate_percent:
            findings.append(
                ExperimentFinding(
                    title="Error rate exceeded the acceptable limit",
                    risk_level=RiskLevel.high,
                    metric="error_rate_percent",
                    description=(
                        f"Observed error rate was {metrics.error_rate_percent}% against "
                        f"a target of {hypothesis.error_rate_percent}%."
                    ),
                    recommendation="Review retry storms, queue backpressure, and graceful degradation paths.",
                )
            )

        if metrics.healthy_replicas < hypothesis.minimum_healthy_replicas:
            findings.append(
                ExperimentFinding(
                    title="Healthy replica count fell below minimum",
                    risk_level=RiskLevel.critical,
                    metric="healthy_replicas",
                    description=(
                        f"Observed {metrics.healthy_replicas} healthy replicas against "
                        f"a minimum of {hypothesis.minimum_healthy_replicas}."
                    ),
                    recommendation="Increase replica spread, readiness checks, pod disruption controls, and autoscaling limits.",
                )
            )

        score = self._score(request, metrics, findings)
        return score, len(findings) == 0, findings

    def guardrail_breached(self, request: ExperimentRequest, metrics: MetricSample) -> bool:
        values = {
            "availability": metrics.availability_percent,
            "availability_percent": metrics.availability_percent,
            "p95_latency_ms": metrics.p95_latency_ms,
            "error_rate": metrics.error_rate_percent,
            "error_rate_percent": metrics.error_rate_percent,
            "healthy_replicas": metrics.healthy_replicas,
        }
        for guardrail in request.guardrails:
            current = values.get(guardrail.name)
            if current is None or not guardrail.abort_on_breach:
                continue
            if "availability" in guardrail.name or "healthy_replicas" in guardrail.name:
                if current < guardrail.threshold:
                    return True
            elif current > guardrail.threshold:
                return True
        return False

    def _score(self, request: ExperimentRequest, metrics: MetricSample, findings: list[ExperimentFinding]) -> int:
        score = 100
        score -= len([item for item in findings if item.risk_level == RiskLevel.critical]) * 35
        score -= len([item for item in findings if item.risk_level == RiskLevel.high]) * 20
        score -= len([item for item in findings if item.risk_level == RiskLevel.medium]) * 10
        score -= max(0, request.blast_radius_percent - 50) // 5
        score -= min(metrics.recovery_time_seconds // 30, 20)
        return max(0, min(100, score))

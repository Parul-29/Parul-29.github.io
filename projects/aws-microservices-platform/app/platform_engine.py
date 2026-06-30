from datetime import datetime, timezone
from uuid import uuid4

from app.models import (
    DeploymentPlan,
    DeploymentStatus,
    Exposure,
    PlatformFinding,
    PlatformRequest,
    PlatformResponse,
    RiskLevel,
)


class PlatformEngine:
    def plan(self, request: PlatformRequest) -> PlatformResponse:
        findings = self._analyze(request)
        readiness_score = self._score(request, findings)

        return PlatformResponse(
            deployment_id=str(uuid4()),
            status=DeploymentStatus.planned,
            request=request,
            plan=self._build_plan(request),
            readiness_score=readiness_score,
            findings=findings,
        )

    def deploy(self, request: PlatformRequest) -> PlatformResponse:
        response = self.plan(request)
        response.status = DeploymentStatus.deployed if response.readiness_score >= 70 else DeploymentStatus.failed
        response.completed_at = datetime.now(timezone.utc)
        return response

    def _build_plan(self, request: PlatformRequest) -> DeploymentPlan:
        namespace = f"{request.platform_name}-{request.environment.value}"
        service_names = [service.name for service in request.services]

        return DeploymentPlan(
            namespace=namespace,
            ecr_repositories=[f"{request.aws_region}/{name}" for name in service_names],
            kubernetes_manifests=[f"k8s/{namespace}/{name}-deployment.yaml" for name in service_names],
            terraform_modules=[
                "modules/vpc",
                "modules/eks",
                "modules/ecr",
                "modules/iam",
                "modules/kms",
                "modules/observability",
            ],
            observability_dashboards=[
                "grafana/service-health",
                "cloudwatch/container-insights",
                "datadog/apm-overview",
            ]
            if request.enable_observability
            else [],
            iam_roles=[f"{namespace}-{name}-irsa-role" for name in service_names] if request.enable_irsa else [],
        )

    def _analyze(self, request: PlatformRequest) -> list[PlatformFinding]:
        findings: list[PlatformFinding] = []

        if not request.services:
            findings.append(
                PlatformFinding(
                    title="No services defined",
                    risk_level=RiskLevel.high,
                    description="The platform request does not include any deployable microservices.",
                    recommendation="Add at least one service specification with image, resources, port, and scaling settings.",
                )
            )

        for service in request.services:
            if request.environment.value == "prod" and service.replicas < 2:
                findings.append(
                    PlatformFinding(
                        title="Production service lacks replica redundancy",
                        risk_level=RiskLevel.high,
                        service=service.name,
                        description=f"{service.name} has {service.replicas} replica in production.",
                        recommendation="Run at least two replicas across availability zones for production services.",
                    )
                )

            if service.exposure == Exposure.public and service.port not in (80, 443):
                findings.append(
                    PlatformFinding(
                        title="Public service exposes a non-standard port",
                        risk_level=RiskLevel.medium,
                        service=service.name,
                        description=f"{service.name} is public on port {service.port}.",
                        recommendation="Expose public traffic through an ALB or API Gateway on HTTPS and keep service ports internal.",
                    )
                )

            if not service.autoscaling_enabled:
                findings.append(
                    PlatformFinding(
                        title="Autoscaling is disabled",
                        risk_level=RiskLevel.medium,
                        service=service.name,
                        description=f"{service.name} has fixed capacity and may not absorb traffic spikes.",
                        recommendation="Enable HPA or KEDA with CPU, memory, or queue-depth metrics.",
                    )
                )

        if not request.enable_kms_encryption:
            findings.append(
                PlatformFinding(
                    title="KMS encryption is disabled",
                    risk_level=RiskLevel.high,
                    description="Platform storage and secrets are not configured for customer-managed encryption.",
                    recommendation="Enable AWS KMS for EKS secrets, EBS volumes, logs, and application data stores.",
                )
            )

        if not request.enable_irsa:
            findings.append(
                PlatformFinding(
                    title="IRSA is disabled",
                    risk_level=RiskLevel.high,
                    description="Pods may need broad node-role permissions instead of least-privilege service account roles.",
                    recommendation="Enable IAM Roles for Service Accounts and assign scoped policies per workload.",
                )
            )

        if not request.enable_observability:
            findings.append(
                PlatformFinding(
                    title="Observability is disabled",
                    risk_level=RiskLevel.medium,
                    description="The platform lacks metrics, logs, traces, and dashboard outputs.",
                    recommendation="Enable CloudWatch Container Insights, Prometheus, Grafana, and APM integration.",
                )
            )

        return findings

    def _score(self, request: PlatformRequest, findings: list[PlatformFinding]) -> int:
        score = 100
        score -= len([item for item in findings if item.risk_level == RiskLevel.critical]) * 35
        score -= len([item for item in findings if item.risk_level == RiskLevel.high]) * 20
        score -= len([item for item in findings if item.risk_level == RiskLevel.medium]) * 10
        score -= max(0, len(request.services) - 12) * 2
        return max(0, min(100, score))

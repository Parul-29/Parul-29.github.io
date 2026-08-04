import json
import re

from app.agents.base import Agent
from app.models import Finding, FindingCategory, ScanRequest, Severity


class MisconfigurationScannerAgent(Agent):
    name = "misconfiguration_scanner"

    async def scan(self, request: ScanRequest) -> list[Finding]:
        findings: list[Finding] = []
        for path, content in request.source_snapshot.items():
            lower_path = path.lower()
            if lower_path.endswith((".tf", ".tfvars")):
                findings.extend(self._scan_terraform(path, content))
            if lower_path.endswith(".json") and "policy" in lower_path:
                findings.extend(self._scan_iam_policy(path, content))
            if lower_path.endswith((".yml", ".yaml")):
                findings.extend(self._scan_workflow(path, content))
        return findings

    def _scan_terraform(self, path: str, content: str) -> list[Finding]:
        checks = [
            (
                r'acl\s*=\s*"public-read"',
                "Public S3 ACL",
                "Terraform config grants public-read access to a bucket.",
                "Use private ACLs and expose objects only through controlled CloudFront or signed URLs.",
                Severity.critical,
                "AWS.S3.1",
            ),
            (
                r"0\.0\.0\.0/0",
                "Unrestricted network ingress",
                "A security group or route permits access from the entire internet.",
                "Restrict CIDR ranges to required sources and ports.",
                Severity.high,
                "AWS.EC2.18",
            ),
            (
                r"encrypted\s*=\s*false",
                "Storage encryption disabled",
                "Infrastructure config explicitly disables encryption.",
                "Enable encryption using a managed or customer-managed KMS key.",
                Severity.high,
                "AWS.KMS.1",
            ),
        ]

        findings: list[Finding] = []
        for pattern, title, description, recommendation, severity, control in checks:
            for match in re.finditer(pattern, content):
                findings.append(
                    Finding(
                        agent=self.name,
                        category=FindingCategory.misconfiguration,
                        title=title,
                        description=description,
                        severity=severity,
                        file_path=path,
                        line=content[: match.start()].count("\n") + 1,
                        evidence=match.group(0),
                        recommendation=recommendation,
                        confidence=0.9,
                        control=control,
                    )
                )
        return findings

    def _scan_iam_policy(self, path: str, content: str) -> list[Finding]:
        findings: list[Finding] = []
        try:
            policy = json.loads(content)
        except json.JSONDecodeError:
            return findings

        statements = policy.get("Statement", [])
        if isinstance(statements, dict):
            statements = [statements]

        for statement in statements:
            if statement.get("Effect") == "Allow" and statement.get("Action") == "*" and statement.get("Resource") == "*":
                findings.append(
                    Finding(
                        agent=self.name,
                        category=FindingCategory.misconfiguration,
                        title="Overly permissive IAM policy",
                        description="IAM policy grants all actions on all resources.",
                        severity=Severity.critical,
                        file_path=path,
                        evidence='"Action": "*", "Resource": "*"',
                        recommendation="Replace wildcard permissions with least-privilege actions and scoped resources.",
                        confidence=0.95,
                        control="AWS.IAM.1",
                    )
                )
        return findings

    def _scan_workflow(self, path: str, content: str) -> list[Finding]:
        if "pull_request_target:" not in content:
            return []

        return [
            Finding(
                agent=self.name,
                category=FindingCategory.misconfiguration,
                title="Risky pull_request_target workflow",
                description="GitHub Actions pull_request_target can expose privileged tokens to untrusted code if checkout or scripts are unsafe.",
                severity=Severity.medium,
                file_path=path,
                evidence="pull_request_target:",
                recommendation="Use pull_request where possible, or harden checkout and token permissions.",
                confidence=0.72,
                control="GHA.SEC.1",
            )
        ]

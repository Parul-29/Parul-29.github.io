from app.agents.base import Agent
from app.models import Finding, FindingCategory, ScanRequest, Severity


class ComplianceCheckerAgent(Agent):
    name = "compliance_checker"

    async def scan(self, request: ScanRequest) -> list[Finding]:
        findings: list[Finding] = []
        files = set(request.changed_files) | set(request.source_snapshot)

        if not any(path.lower().endswith((".yml", ".yaml")) and ".github/workflows" in path for path in files):
            findings.append(
                Finding(
                    agent=self.name,
                    category=FindingCategory.compliance,
                    title="Missing CI workflow evidence",
                    description="No GitHub Actions workflow was provided for the scan, so pipeline security controls cannot be verified.",
                    severity=Severity.medium,
                    recommendation="Add a workflow that runs tests and security checks on pull requests.",
                    confidence=0.68,
                    control="SDLC.CI.1",
                )
            )

        if not any("codeowners" in path.lower() for path in files):
            findings.append(
                Finding(
                    agent=self.name,
                    category=FindingCategory.compliance,
                    title="Missing CODEOWNERS review control",
                    description="Repository snapshot does not include a CODEOWNERS file for ownership-based review routing.",
                    severity=Severity.low,
                    recommendation="Add CODEOWNERS to enforce review from responsible owners for sensitive paths.",
                    confidence=0.7,
                    control="SDLC.REVIEW.1",
                )
            )

        for path, content in request.source_snapshot.items():
            if path.lower().endswith((".yml", ".yaml")) and "permissions:" not in content:
                findings.append(
                    Finding(
                        agent=self.name,
                        category=FindingCategory.compliance,
                        title="GitHub Actions permissions not pinned",
                        description="Workflow does not explicitly define token permissions.",
                        severity=Severity.medium,
                        file_path=path,
                        recommendation="Set least-privilege permissions at workflow or job level.",
                        evidence="permissions block missing",
                        confidence=0.8,
                        control="GHA.PERM.1",
                    )
                )

        return findings

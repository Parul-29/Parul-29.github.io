import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from app.agents.compliance import ComplianceCheckerAgent
from app.agents.misconfiguration import MisconfigurationScannerAgent
from app.agents.reasoning import ReasoningAgent
from app.agents.vulnerability import VulnerabilityScannerAgent
from app.models import AgentResult, Finding, ScanRequest, ScanResponse, ScanStatus


class Orchestrator:
    def __init__(self) -> None:
        self.agents = [
            VulnerabilityScannerAgent(),
            MisconfigurationScannerAgent(),
            ComplianceCheckerAgent(),
        ]
        self.reasoning_agent = ReasoningAgent()

    async def run_scan(self, request: ScanRequest) -> ScanResponse:
        scan = ScanResponse(
            scan_id=str(uuid4()),
            status=ScanStatus.running,
            request=request,
        )

        agent_results = await asyncio.gather(*(agent.execute(request) for agent in self.agents))
        findings = self._dedupe_findings(agent_results)
        reasoning = await self.reasoning_agent.enrich(findings)

        scan.status = ScanStatus.completed
        scan.agent_results = agent_results
        scan.findings = sorted(findings, key=lambda item: item.risk_score, reverse=True)
        scan.reasoning = reasoning
        scan.completed_at = datetime.now(timezone.utc)
        scan.errors = [error for result in agent_results for error in result.errors]
        return scan

    def _dedupe_findings(self, agent_results: list[AgentResult]) -> list[Finding]:
        deduped: dict[tuple[str, str | None, str, str], Finding] = {}
        for result in agent_results:
            for finding in result.findings:
                key = finding.dedupe_key()
                existing = deduped.get(key)
                if not existing or finding.confidence > existing.confidence:
                    deduped[key] = finding
        return list(deduped.values())

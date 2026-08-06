import json
import httpx
import asyncio
from google import genai

from app.config import settings
from app.models import ActionRoute, Finding, ReasoningSummary, Severity


SEVERITY_BASE_SCORE = {
    Severity.low: 25,
    Severity.medium: 50,
    Severity.high: 75,
    Severity.critical: 95,
}


class ReasoningAgent:
    async def enrich(self, findings: list[Finding]) -> ReasoningSummary:
        for finding in findings:
            finding.risk_score = self._score(finding)
            finding.route = self._route(finding)

        summary = None

        if findings and settings.llm_provider == "gemini":
            summary = await self._try_gemini_summary(findings)
        elif findings and settings.llm_provider == "ollama":
            summary = await self._try_ollama_summary(findings)

        return summary or self._deterministic_summary(findings)

    def _score(self, finding: Finding) -> int:
        score = SEVERITY_BASE_SCORE[finding.severity]
        if finding.confidence < 0.7:
            score -= 10
        if finding.cwe or finding.control:
            score += 4
        return max(0, min(100, score))

    def _route(self, finding: Finding) -> ActionRoute:
        if finding.risk_score >= settings.high_risk_threshold or finding.confidence < 0.65:
            return ActionRoute.human_review
        if finding.severity == Severity.low:
            return ActionRoute.auto_fix
        return ActionRoute.backlog

    def _deterministic_summary(self, findings: list[Finding]) -> ReasoningSummary:
        counts = {severity: 0 for severity in Severity}
        for finding in findings:
            counts[finding.severity] += 1

        top_findings = sorted(findings, key=lambda item: item.risk_score, reverse=True)[:3]
        steps = [
            f"Review {finding.severity.value} finding: {finding.title}"
            for finding in top_findings
        ] or ["No findings detected. Keep security scans enabled on pull requests."]

        return ReasoningSummary(
            executive_summary=(
                f"Scan completed with {len(findings)} findings. "
                f"{counts[Severity.critical]} critical and {counts[Severity.high]} high findings require priority attention."
            ),
            total_findings=len(findings),
            critical_count=counts[Severity.critical],
            high_count=counts[Severity.high],
            medium_count=counts[Severity.medium],
            low_count=counts[Severity.low],
            recommended_next_steps=steps,
        )

    async def _try_ollama_summary(self, findings: list[Finding]) -> ReasoningSummary | None:
        payload = {
            "model": settings.ollama_model,
            "stream": False,
            "prompt": self._build_prompt(findings),
            "format": "json",
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                content = json.loads(data.get("response", "{}"))
                return ReasoningSummary.model_validate(content)
        except Exception:
            return None

    def _build_prompt(self, findings: list[Finding]) -> str:
        serialized = [
            finding.model_dump(
                mode="json",
                include={"title", "severity", "category", "risk_score", "confidence", "recommendation"},
            )
            for finding in findings
        ]
        return (
            "You are a DevSecOps reasoning agent. Return strict JSON matching this schema: "
            "{executive_summary: string, total_findings: int, critical_count: int, high_count: int, "
            "medium_count: int, low_count: int, recommended_next_steps: string[]}. "
            f"Findings: {json.dumps(serialized)}"
        )

    async def _try_gemini_summary(self, findings: list[Finding]) -> ReasoningSummary | None:
        if not settings.gemini_api_key:
            print("Gemini reasoning skipped: GEMINI_API_KEY is missing")
            return None

        try:
            client = genai.Client(api_key=settings.gemini_api_key)

            response = await asyncio.to_thread(
                client.models.generate_content,
                model=settings.gemini_model,
                contents=self._build_prompt(findings),
                config={
                    "response_format": {
                        "text": {
                            "mime_type": "application/json",
                            "schema": ReasoningSummary.model_json_schema(),
                        }
                    }
                },
            )
            return ReasoningSummary.model_validate_json(response.text)

        except Exception as exc:
            print(f"Gemini reasoning failed: {exc}")
            return None

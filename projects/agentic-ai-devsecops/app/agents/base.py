import asyncio
import time
from abc import ABC, abstractmethod

from app.config import settings
from app.models import AgentResult, ScanRequest


class Agent(ABC):
    name: str

    async def execute(self, request: ScanRequest) -> AgentResult:
        start = time.perf_counter()
        errors: list[str] = []

        for attempt in range(settings.max_agent_retries + 1):
            try:
                findings = await asyncio.wait_for(
                    self.scan(request),
                    timeout=settings.agent_timeout_seconds,
                )
                return AgentResult(
                    agent=self.name,
                    findings=findings,
                    errors=errors,
                    duration_ms=int((time.perf_counter() - start) * 1000),
                )
            except Exception as exc:  # noqa: BLE001 - agent isolation is intentional
                errors.append(f"attempt {attempt + 1}: {exc}")
                await asyncio.sleep(min(2**attempt, 4))

        return AgentResult(
            agent=self.name,
            findings=[],
            errors=errors,
            duration_ms=int((time.perf_counter() - start) * 1000),
        )

    @abstractmethod
    async def scan(self, request: ScanRequest):
        raise NotImplementedError

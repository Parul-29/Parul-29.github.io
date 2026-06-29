from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import ScanRequest, ScanResponse, ScanStatus
from app.orchestrator import Orchestrator
from app.storage import scan_store

app = FastAPI(title=settings.app_name, version="1.0.0")
orchestrator = Orchestrator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(f"{settings.api_prefix}/scans", response_model=ScanResponse)
async def create_scan(request: ScanRequest) -> ScanResponse:
    scan = await orchestrator.run_scan(request)
    scan_store.save(scan)
    return scan


@app.get(f"{settings.api_prefix}/scans/{{scan_id}}", response_model=ScanResponse)
async def get_scan(scan_id: str) -> ScanResponse:
    scan = scan_store.get(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@app.get(f"{settings.api_prefix}/review-queue", response_model=list[ScanResponse])
async def review_queue() -> list[ScanResponse]:
    return scan_store.list_review_queue()


@app.post(f"{settings.api_prefix}/github/webhook")
async def github_webhook(payload: dict[str, Any], background_tasks: BackgroundTasks) -> dict[str, str]:
    request = ScanRequest(
        repository=payload.get("repository", {}).get("full_name", "unknown/repository"),
        branch=payload.get("ref", "refs/heads/main").split("/")[-1],
        commit_sha=payload.get("after"),
        changed_files=[],
        metadata={"event": "push", "raw_keys": list(payload.keys())},
    )
    queued = ScanResponse(scan_id=f"queued-{request.commit_sha or 'manual'}", status=ScanStatus.queued, request=request)
    scan_store.save(queued)
    background_tasks.add_task(_run_background_scan, request, queued.scan_id)
    return {"status": "queued", "scan_id": queued.scan_id}


@app.post(f"{settings.api_prefix}/github/webhook/raw")
async def github_webhook_raw(request: Request) -> dict[str, Any]:
    return {"received": await request.json()}


async def _run_background_scan(request: ScanRequest, queued_scan_id: str) -> None:
    scan = await orchestrator.run_scan(request)
    scan.scan_id = queued_scan_id
    scan_store.save(scan)

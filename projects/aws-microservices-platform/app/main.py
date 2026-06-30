from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import PlatformRequest, PlatformResponse
from app.platform_engine import PlatformEngine
from app.storage import deployment_store

app = FastAPI(title=settings.app_name, version="1.0.0")
engine = PlatformEngine()

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


@app.post(f"{settings.api_prefix}/platforms/plan", response_model=PlatformResponse)
async def plan_platform(request: PlatformRequest) -> PlatformResponse:
    deployment = engine.plan(request)
    deployment_store.save(deployment)
    return deployment


@app.post(f"{settings.api_prefix}/platforms/deploy", response_model=PlatformResponse)
async def deploy_platform(request: PlatformRequest) -> PlatformResponse:
    deployment = engine.deploy(request)
    deployment_store.save(deployment)
    return deployment


@app.get(f"{settings.api_prefix}/deployments", response_model=list[PlatformResponse])
async def list_deployments() -> list[PlatformResponse]:
    return deployment_store.list()


@app.get(f"{settings.api_prefix}/deployments/{{deployment_id}}", response_model=PlatformResponse)
async def get_deployment(deployment_id: str) -> PlatformResponse:
    deployment = deployment_store.get(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment

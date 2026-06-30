from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.experiment_engine import ExperimentEngine
from app.models import ExperimentRequest, ExperimentResponse
from app.storage import experiment_store

app = FastAPI(title=settings.app_name, version="1.0.0")
engine = ExperimentEngine()

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


@app.post(f"{settings.api_prefix}/experiments/plan", response_model=ExperimentResponse)
async def plan_experiment(request: ExperimentRequest) -> ExperimentResponse:
    experiment = engine.plan(request)
    experiment_store.save(experiment)
    return experiment


@app.post(f"{settings.api_prefix}/experiments/run", response_model=ExperimentResponse)
async def run_experiment(request: ExperimentRequest) -> ExperimentResponse:
    experiment = engine.run(request)
    experiment_store.save(experiment)
    return experiment


@app.get(f"{settings.api_prefix}/experiments", response_model=list[ExperimentResponse])
async def list_experiments() -> list[ExperimentResponse]:
    return experiment_store.list()


@app.get(f"{settings.api_prefix}/experiments/{{experiment_id}}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str) -> ExperimentResponse:
    experiment = experiment_store.get(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

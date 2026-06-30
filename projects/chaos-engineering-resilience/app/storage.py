from app.models import ExperimentResponse


class ExperimentStore:
    def __init__(self) -> None:
        self._experiments: dict[str, ExperimentResponse] = {}

    def save(self, experiment: ExperimentResponse) -> None:
        self._experiments[experiment.experiment_id] = experiment

    def get(self, experiment_id: str) -> ExperimentResponse | None:
        return self._experiments.get(experiment_id)

    def list(self) -> list[ExperimentResponse]:
        return sorted(self._experiments.values(), key=lambda item: item.created_at, reverse=True)


experiment_store = ExperimentStore()

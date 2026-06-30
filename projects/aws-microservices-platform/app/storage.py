from app.models import PlatformResponse


class DeploymentStore:
    def __init__(self) -> None:
        self._deployments: dict[str, PlatformResponse] = {}

    def save(self, deployment: PlatformResponse) -> None:
        self._deployments[deployment.deployment_id] = deployment

    def get(self, deployment_id: str) -> PlatformResponse | None:
        return self._deployments.get(deployment_id)

    def list(self) -> list[PlatformResponse]:
        return sorted(self._deployments.values(), key=lambda item: item.created_at, reverse=True)


deployment_store = DeploymentStore()

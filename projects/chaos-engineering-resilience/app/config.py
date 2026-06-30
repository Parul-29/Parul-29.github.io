import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Chaos Engineering Resilience API")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    default_error_budget_percent: float = float(os.getenv("DEFAULT_ERROR_BUDGET_PERCENT", "1.0"))


settings = Settings()

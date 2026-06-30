import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "AWS Microservices Platform API")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    default_region: str = os.getenv("DEFAULT_REGION", "us-west-2")


settings = Settings()

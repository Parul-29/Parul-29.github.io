import os


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "Agentic AI DevSecOps Backend")
        self.api_prefix = os.getenv("API_PREFIX", "/api/v1")
        self.ollama_enabled = _env_bool("OLLAMA_ENABLED", False)
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.agent_timeout_seconds = float(os.getenv("AGENT_TIMEOUT_SECONDS", "20"))
        self.max_agent_retries = int(os.getenv("MAX_AGENT_RETRIES", "2"))
        self.high_risk_threshold = int(os.getenv("HIGH_RISK_THRESHOLD", "70"))
        self.critical_risk_threshold = int(os.getenv("CRITICAL_RISK_THRESHOLD", "90"))


settings = Settings()

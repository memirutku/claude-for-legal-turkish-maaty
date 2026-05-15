"""Service config — read from env."""
import os
from pathlib import Path


class Settings:
    PLUGINS_DIR: Path = Path(os.getenv("PLUGINS_DIR", "/app/plugins"))
    SERVICE_NAME: str = "Maaty Skill Template Service"
    VERSION: str = "0.1.0"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info").lower()
    # Default models per provider — used if X-AI-Model header missing
    DEFAULT_MODELS: dict[str, str] = {
        "gemini": "gemini-2.5-pro",
        "openai": "gpt-5.4",
        "anthropic": "claude-sonnet-4-6",
    }


settings = Settings()

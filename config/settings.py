"""
Application-wide settings loaded from environment variables / .env file.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)

# DeepEval's internal pydantic Settings validates AZURE_OPENAI_ENDPOINT as
# a URL and rejects empty strings.  Remove empty values for keys that
# DeepEval / pydantic-settings would choke on.
_URL_ENV_KEYS = [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_BASE",
    "OPENAI_API_BASE",
]
for _k in _URL_ENV_KEYS:
    if os.environ.get(_k, None) == "":
        del os.environ[_k]


class Settings:
    """Centralised settings singleton – reads from env vars."""

    APP_NAME: str = os.getenv("APP_NAME", "LLM Red Teaming Platform")
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "change-me")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).resolve().parent.parent / 'red_teaming.db'}",
    )

    # --- Auth ---
    AUTH_USERNAME: str = os.getenv("AUTH_USERNAME", "admin")
    AUTH_PASSWORD_HASH: str = os.getenv("AUTH_PASSWORD_HASH", "")

    # --- Provider API Keys ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_ORG_ID: str = os.getenv("OPENAI_ORG_ID", "")

    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-12-01-preview"
    )
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv(
        "AZURE_OPENAI_DEPLOYMENT_NAME", ""
    )

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_DEFAULT_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    HUGGINGFACEHUB_API_TOKEN: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")


settings = Settings()

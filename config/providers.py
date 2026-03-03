"""
LLM Provider definitions – catalogue of supported providers and their models.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class ProviderInfo:
    """Metadata for an LLM provider."""

    id: str
    display_name: str
    env_keys: List[str]
    default_models: List[str] = field(default_factory=list)
    supports_custom_model: bool = True
    base_url: str | None = None


PROVIDERS: dict[str, ProviderInfo] = {
    "openai": ProviderInfo(
        id="openai",
        display_name="OpenAI",
        env_keys=["OPENAI_API_KEY"],
        default_models=[
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini",
        ],
    ),
    "anthropic": ProviderInfo(
        id="anthropic",
        display_name="Anthropic",
        env_keys=["ANTHROPIC_API_KEY"],
        default_models=[
            "claude-sonnet-4-20250514",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ],
    ),
    "azure_openai": ProviderInfo(
        id="azure_openai",
        display_name="Azure OpenAI",
        env_keys=[
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME",
        ],
        default_models=["gpt-4o", "gpt-4", "gpt-35-turbo"],
    ),
    "google_gemini": ProviderInfo(
        id="google_gemini",
        display_name="Google Gemini",
        env_keys=["GOOGLE_API_KEY"],
        default_models=[
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ],
    ),
    "aws_bedrock": ProviderInfo(
        id="aws_bedrock",
        display_name="AWS Bedrock",
        env_keys=["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
        default_models=[
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "amazon.titan-text-premier-v1:0",
            "meta.llama3-1-70b-instruct-v1:0",
        ],
    ),
    "huggingface": ProviderInfo(
        id="huggingface",
        display_name="HuggingFace",
        env_keys=["HUGGINGFACEHUB_API_TOKEN"],
        default_models=[
            "meta-llama/Llama-3.1-70B-Instruct",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "google/gemma-2-27b-it",
        ],
    ),
    "groq": ProviderInfo(
        id="groq",
        display_name="Groq",
        env_keys=["GROQ_API_KEY"],
        default_models=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
    ),
    "deepseek": ProviderInfo(
        id="deepseek",
        display_name="DeepSeek",
        env_keys=["DEEPSEEK_API_KEY"],
        default_models=[
            "deepseek-chat",
            "deepseek-reasoner",
        ],
        base_url="https://api.deepseek.com/v1",
    ),
}


def get_configured_providers() -> dict[str, ProviderInfo]:
    """Return only providers whose API keys are set in the environment."""
    import os
    from config.settings import settings

    configured: dict[str, ProviderInfo] = {}
    
    # Build a map from both settings object AND current os.environ
    # (os.environ includes keys saved via web UI)
    env_map = {k: getattr(settings, k, "") for k in dir(settings) if k.isupper()}
    # Override with current os.environ values (includes database-saved keys)
    env_map.update({k: v for k, v in os.environ.items() if k.isupper()})

    for pid, info in PROVIDERS.items():
        if all(env_map.get(k, "") not in ("", None) for k in info.env_keys):
            configured[pid] = info
    return configured

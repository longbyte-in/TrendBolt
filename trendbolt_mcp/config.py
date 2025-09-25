"""Application configuration using pydantic-settings.

Loads configuration from environment variables and an optional .env file.
This centralizes all credentials and runtime options for the MCP server and tools.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Reddit
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str = "TrendBolt/1.0"

    # LLM (Azure OpenAI only)
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str | None = None

    # Canva Connect (access token + default brand template)
    canva_access_token: str | None = None
    canva_brand_template_id: str | None = None

    # Azure Blob Storage removed; images posted directly to LinkedIn

    # LinkedIn
    linkedin_page_id: str | None = None
    linkedin_access_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def llm_provider(self) -> str:
        if self.azure_openai_endpoint and self.azure_openai_api_key and self.azure_openai_deployment:
            return "azure_openai"
        return "none"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]



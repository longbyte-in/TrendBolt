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

    # LLM (Azure OpenAI preferred, OpenAI fallback)
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str | None = "2024-06-01"
    openai_api_key: str | None = None

    # Canva Bridge
    canva_bridge_base_url: str | None = None
    canva_bridge_signing_secret: str | None = None

    # Azure Blob Storage (default)
    azure_storage_account: str | None = None
    azure_storage_container: str | None = "posts"
    azure_storage_connection_string: str | None = None
    azure_tenant_id: str | None = None
    azure_client_id: str | None = None
    azure_client_secret: str | None = None

    # Facebook
    facebook_app_id: str | None = None
    facebook_app_secret: str | None = None
    facebook_page_id: str | None = None
    facebook_page_access_token: str | None = None

    # App options
    log_level: str = "INFO"
    subreddits: List[str] = Field(default_factory=lambda: ["technology"])  # comma-separated in .env optional
    min_score: int = 200
    template_id: str = "trendbolt_template_default"

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
        if self.openai_api_key:
            return "openai"
        return "none"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]



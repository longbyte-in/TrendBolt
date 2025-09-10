import os
from importlib import reload


def test_settings_llm_provider_openai(monkeypatch):
    # Minimal required envs to construct settings
    monkeypatch.setenv("REDDIT_CLIENT_ID", "x")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "y")
    monkeypatch.setenv("REDDIT_USER_AGENT", "TrendBolt/1.0")
    monkeypatch.setenv("CANVA_BRIDGE_BASE_URL", "https://x")
    monkeypatch.setenv("CANVA_BRIDGE_SIGNING_SECRET", "s")
    monkeypatch.setenv("FACEBOOK_APP_ID", "a")
    monkeypatch.setenv("FACEBOOK_APP_SECRET", "b")
    monkeypatch.setenv("FACEBOOK_PAGE_ID", "c")
    monkeypatch.setenv("FACEBOOK_PAGE_ACCESS_TOKEN", "d")
    monkeypatch.setenv("OPENAI_API_KEY", "openai")

    from trendbolt_mcp import config

    reload(config)
    settings = config.get_settings()
    assert settings.llm_provider == "openai"


def test_settings_llm_provider_azure(monkeypatch):
    monkeypatch.setenv("REDDIT_CLIENT_ID", "x")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "y")
    monkeypatch.setenv("REDDIT_USER_AGENT", "TrendBolt/1.0")
    monkeypatch.setenv("CANVA_BRIDGE_BASE_URL", "https://x")
    monkeypatch.setenv("CANVA_BRIDGE_SIGNING_SECRET", "s")
    monkeypatch.setenv("FACEBOOK_APP_ID", "a")
    monkeypatch.setenv("FACEBOOK_APP_SECRET", "b")
    monkeypatch.setenv("FACEBOOK_PAGE_ID", "c")
    monkeypatch.setenv("FACEBOOK_PAGE_ACCESS_TOKEN", "d")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "key")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

    from trendbolt_mcp import config

    reload(config)
    settings = config.get_settings()
    assert settings.llm_provider == "azure_openai"


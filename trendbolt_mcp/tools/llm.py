"""LLM tool for generating canvas post content using Azure OpenAI or OpenAI."""

from __future__ import annotations

from typing import Protocol

from ..config import get_settings


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:  # returns JSON string per our schema
        ...


class AzureOpenAIClient:
    def __init__(self, endpoint: str, api_key: str, deployment: str, api_version: str) -> None:
        from openai import AzureOpenAI  # type: ignore

        self._deployment = deployment
        self._client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
        )

    def generate(self, prompt: str) -> str:
        # Use Chat Completions for maximum Azure compatibility
        completion = self._client.chat.completions.create(
            model=self._deployment,
            messages=[
                {"role": "system", "content": "You are an expert viral social media content creator who specializes in creating engaging, shareable posts that drive high engagement. You understand what makes content go viral and how to craft compelling narratives that resonate with audiences."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content or ""


class OpenAIClient:
    def __init__(self, api_key: str) -> None:
        from openai import OpenAI  # type: ignore

        self._client = OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        completion = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert viral social media content creator who specializes in creating engaging, shareable posts that drive high engagement. You understand what makes content go viral and how to craft compelling narratives that resonate with audiences."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content or ""


def _build_prompt(topic: dict, brand: dict) -> str:
    title = topic.get("title", "")
    url = topic.get("url", "")
    voice = brand.get("voice", "concise, actionable")
    cta = brand.get("cta", "Follow TrendBolt")
    return (
        "You are a social media content creator. Respond with STRICT JSON ONLY, no prose, no markdown, no backticks.\n\n"
        "TOPIC: {title}\n"
        "SOURCE: {url}\n"
        "BRAND VOICE: {voice}\n"
        "CALL TO ACTION: {cta}\n\n"
        "Produce exactly this JSON (no extra keys):\n"
        "{{\n"
        "  \"title\": string (<=100 chars),\n"
        "  \"headline\": string (<=60 chars),\n"
        "  \"description\": string (<=2200 chars; most of the content),\n"
        "  \"image_available\": boolean\n"
        "}}\n\n"
        "Hard constraints:\n"
        "- Output must be valid JSON.\n"
        "- Do NOT include any explanations, instructions, or narrative.\n"
        "- Values must be concise data only."
    ).format(title=title, url=url, voice=voice, cta=cta)


def _choose_client_from_settings() -> LLMClient | None:
    s = get_settings()
    if s.llm_provider == "azure_openai":
        return AzureOpenAIClient(
            endpoint=s.azure_openai_endpoint or "",
            api_key=s.azure_openai_api_key or "",
            deployment=s.azure_openai_deployment or "",
            api_version=getattr(s, "azure_openai_api_version", "2024-06-01"),
        )
    if s.llm_provider == "openai":
        return OpenAIClient(api_key=s.openai_api_key or "")
    return None


def generate_canvas_post(topic: dict, brand: dict, client: LLMClient | None = None) -> dict:
    """Generate title/headline/description/image_available via LLM and return structured dict.

    If no client is provided, choose based on settings (Azure preferred).
    The model is instructed to return JSON; we parse defensively.
    """
    import json

    if client is None:
        client = _choose_client_from_settings()
    if client is None:
        # Fallback deterministic stub if no keys configured
        title = topic.get("title", "Update")
        return {
            "title": title,
            "headline": title,
            "description": f"Quick takeaways: {title}",
            "image_available": False,
        }

    prompt = _build_prompt(topic, brand)
    raw = client.generate(prompt)
    try:
        data = json.loads(raw)
        # minimal validation
        data.setdefault("headline", data.get("title", topic.get("title", "")))
        data.setdefault("image_available", False)
        return data
    except Exception:
        # If model returns non-JSON, fallback to a simple shaped response
        title = topic.get("title", "Update")
        return {
            "title": title,
            "headline": title,
            "description": raw.strip()[:2000] or f"Update: {title}",
            "image_available": False,
        }



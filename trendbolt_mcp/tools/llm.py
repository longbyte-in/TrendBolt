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
        "You are a viral social media content creator specializing in engaging Canva posts. "
        "Create compelling content that drives engagement and shares.\n\n"
        "TOPIC: {title}\n"
        "SOURCE: {url}\n"
        "BRAND VOICE: {voice}\n"
        "CALL TO ACTION: {cta}\n\n"
        "Generate a JSON object with these fields:\n"
        "- caption: Engaging social media caption (max 2200 chars) that hooks readers, explains the topic clearly, and encourages interaction\n"
        "- alt_text: Descriptive alt text for accessibility (max 125 chars)\n"
        "- hashtags: Array of 3-5 relevant hashtags (mix of trending and niche)\n"
        "- design_brief: Object with:\n"
        "  * headline: Eye-catching main title (max 60 chars)\n"
        "  * subtext: Compelling subtitle that adds context (max 120 chars)\n"
        "  * cta: Clear call-to-action button text (max 20 chars)\n"
        "  * color_theme: Choose 'dark_on_light' or 'light_on_dark'\n"
        "  * layout: Use 'headline_top_subtext_center_cta_bottom'\n"
        "  * image_guidance: Specific visual suggestions (icons, colors, style)\n\n"
        "Make it engaging, informative, and shareable. Avoid clickbait but make it compelling.\n"
        "Return ONLY valid JSON."
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
    """Generate caption + design brief via LLM and return structured dict.

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
            "caption": f"Big news: {title}",
            "alt_text": f"A graphic about {title}",
            "hashtags": ["#TrendBolt"],
            "design_brief": {
                "headline": title,
                "subtext": "Why it matters in 3 bullets ...",
                "cta": brand.get("cta", "Follow TrendBolt"),
                "color_theme": "dark_on_light",
                "layout": "headline_top_subtext_center_cta_bottom",
                "image_guidance": "abstract tech pattern",
            },
        }

    prompt = _build_prompt(topic, brand)
    raw = client.generate(prompt)
    try:
        data = json.loads(raw)
        # minimal validation
        data.setdefault("hashtags", [])
        data.setdefault("design_brief", {})
        return data
    except Exception:
        # If model returns non-JSON, fallback to a simple shaped response
        title = topic.get("title", "Update")
        return {
            "caption": raw.strip()[:2000] or f"Update: {title}",
            "alt_text": f"A graphic about {title}",
            "hashtags": ["#AI", "#TechTrends"],
            "design_brief": {
                "headline": title,
                "subtext": "Key takeaways...",
                "cta": brand.get("cta", "Follow TrendBolt"),
                "color_theme": "dark_on_light",
                "layout": "headline_top_subtext_center_cta_bottom",
                "image_guidance": "abstract pattern",
            },
        }



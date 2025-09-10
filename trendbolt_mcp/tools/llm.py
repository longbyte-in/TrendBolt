"""Stub for llm.generate_canvas_post tool implementation."""

from __future__ import annotations


def generate_canvas_post_stub(title: str, url: str) -> dict:
    """Temporary stub to shape the expected response contract."""
    return {
        "caption": f"Update: {title}",
        "alt_text": f"Graphic announcing: {title}",
        "hashtags": ["#TrendBolt"],
        "design_brief": {
            "headline": title,
            "subtext": "Why it matters...",
            "cta": "Follow TrendBolt",
            "color_theme": "dark_on_light",
            "layout": "headline_top_subtext_center_cta_bottom",
            "image_guidance": "abstract pattern"
        },
    }



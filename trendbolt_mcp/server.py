"""
TrendBolt MCP server bootstrap (skeleton).

This module will host the MCP server wiring and tool registration for:
- reddit.get_trending
- llm.generate_canvas_post
- canva.create_design
- facebook.publish_post

See DESIGN.md for architecture details.
"""

from __future__ import annotations

import sys

from .config import get_settings


def main() -> None:
    """Entry point for the TrendBolt MCP server (skeleton)."""
    settings = get_settings()
    print(
        "TrendBolt MCP server stub started. Tools will be implemented next.\n"
        f"LLM provider: {settings.llm_provider}\n"
        f"Storage container: {settings.azure_storage_container}"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)


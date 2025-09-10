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


def main() -> None:
    """Entry point for the TrendBolt MCP server (skeleton)."""
    print("TrendBolt MCP server stub started. Tools will be implemented next.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)


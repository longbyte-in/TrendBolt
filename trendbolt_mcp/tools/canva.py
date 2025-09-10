"""Stub for canva.create_design tool implementation.

This will call a lightweight bridge that leverages Canva Apps SDK to populate
templates and export PNGs. For now, returns a placeholder.
"""

from __future__ import annotations


def create_design_stub() -> dict:
    """Return a placeholder asset reference to unblock wiring."""
    return {
        "asset_url": "https://example.com/placeholder.png",
        "preview_url": "https://example.com/placeholder_preview.png",
        "design_id": "canva_design_stub",
    }



"""Canva bridge client for create-design + export."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Dict, Optional

import httpx

from ..config import get_settings
from ..logging import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


def _sign_payload(secret: str, body_bytes: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
    return digest


logger = get_logger(__name__)


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def create_design(
    template_id: str,
    design_brief: Dict[str, Any],
    export: Dict[str, Any] | None = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Create a design via Canva bridge and return exported asset metadata.

    The bridge is expected to expose POST /api/create_design and return
    { asset_url, preview_url, design_id }.
    """
    settings = get_settings()
    
    if not settings.canva_bridge_base_url:
        raise ValueError("Canva bridge base URL is required. Set CANVA_BRIDGE_BASE_URL in environment.")
    if not settings.canva_bridge_signing_secret:
        raise ValueError("Canva bridge signing secret is required. Set CANVA_BRIDGE_SIGNING_SECRET in environment.")
    
    url = settings.canva_bridge_base_url.rstrip("/") + "/api/create_design"
    payload = {
        "template_id": template_id or settings.template_id,
        "design_brief": design_brief,
        "export": export or {"format": "png", "width": 1080, "height": 1080},
    }
    body = json.dumps(payload).encode("utf-8")
    signature = _sign_payload(settings.canva_bridge_signing_secret, body)
    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature,
    }
    owns_client = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns_client = True
    try:
        resp = client.post(url, content=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return {
            "asset_url": data.get("asset_url"),
            "preview_url": data.get("preview_url"),
            "design_id": data.get("design_id"),
        }
    except httpx.HTTPError as e:
        raise
    finally:
        if owns_client:
            client.close()



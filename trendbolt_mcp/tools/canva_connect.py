"""Canva Connect API helpers (access token based).

Implements:
- list_brand_templates
- get_brand_template_dataset

Docs:
- List brand templates: https://www.canva.dev/docs/connect/api-reference/brand-templates/list-brand-templates/
- Get dataset: https://www.canva.dev/docs/connect/api-reference/brand-templates/get-brand-template-dataset/
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from ..config import get_settings
from ..logging import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


logger = get_logger(__name__)


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def list_brand_templates(
    query: Optional[str] = None,
    ownership: Optional[str] = None,
    sort_by: Optional[str] = None,
    dataset: Optional[str] = None,
    continuation: Optional[str] = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """List brand templates for the current user.

    Returns the raw JSON from Canva. Caller can read `items` to get template IDs.
    """
    s = get_settings()
    token = s.canva_access_token
    if not token:
        raise ValueError("Canva access token is required. Set CANVA_ACCESS_TOKEN in environment.")

    url = "https://api.canva.com/rest/v1/brand-templates"
    params: dict[str, str] = {}
    if query:
        params["query"] = query
    if ownership:
        params["ownership"] = ownership
    if sort_by:
        params["sort_by"] = sort_by
    if dataset:
        params["dataset"] = dataset
    if continuation:
        params["continuation"] = continuation

    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    try:
        resp = client.get(url, headers=_auth_headers(token), params=params)
        resp.raise_for_status()
        return resp.json()
    finally:
        if owns:
            client.close()


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def get_brand_template_dataset(
    brand_template_id: str,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Get dataset definition for a brand template."""
    s = get_settings()
    token = s.canva_access_token
    if not token:
        raise ValueError("Canva access token is required. Set CANVA_ACCESS_TOKEN in environment.")

    if not brand_template_id:
        raise ValueError("brand_template_id is required")

    url = f"https://api.canva.com/rest/v1/brand-templates/{brand_template_id}/dataset"

    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    try:
        resp = client.get(url, headers=_auth_headers(token))
        resp.raise_for_status()
        return resp.json()
    finally:
        if owns:
            client.close()


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def create_autofill_job(
    data: Dict[str, Any],
    brand_template_id: Optional[str] = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Create an autofill job using a brand template and data mapping.

    Docs: https://www.canva.dev/docs/connect/api-reference/autofill/create-autofill-job/
    """
    s = get_settings()
    token = s.canva_access_token
    if not token:
        raise ValueError("Canva access token is required. Set CANVA_ACCESS_TOKEN in environment.")

    tpl = brand_template_id or s.canva_brand_template_id
    if not tpl:
        raise ValueError("brand_template_id is required. Set CANVA_BRAND_TEMPLATE_ID or pass param.")

    url = "https://api.canva.com/rest/v1/autofills"
    payload = {
        "brand_template_id": tpl,
        "data": data,
    }

    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    try:
        resp = client.post(url, headers={**_auth_headers(token), "Content-Type": "application/json"}, json=payload)
        resp.raise_for_status()
        return resp.json()
    finally:
        if owns:
            client.close()


@retry(reraise=True, stop=stop_after_attempt(5), wait=wait_exponential(multiplier=0.5, max=8), retry=retry_if_exception_type(httpx.HTTPError))
def get_autofill_job(job_id: str, timeout_seconds: float = 30.0, client: Optional[httpx.Client] = None) -> dict:
    """Poll an autofill job by ID."""
    s = get_settings()
    token = s.canva_access_token
    if not token:
        raise ValueError("Canva access token is required. Set CANVA_ACCESS_TOKEN in environment.")

    if not job_id:
        raise ValueError("job_id is required")

    url = f"https://api.canva.com/rest/v1/autofills/{job_id}"

    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    try:
        resp = client.get(url, headers=_auth_headers(token))
        resp.raise_for_status()
        return resp.json()
    finally:
        if owns:
            client.close()


def build_autofill_data(values: Dict[str, str], field_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Build Canva autofill data structure from simple values and an optional field map.

    - values: { source_key: text_value }
    - field_map: { destination_dataset_key: source_key }
    
    Returns: { destination_dataset_key: {"type": "text", "text": value} }
    
    Note: Images are excluded - send separately later if needed.
    """
    mapping = field_map or {k: k for k in values.keys()}
    data: Dict[str, Any] = {}
    for dest_key, src_key in mapping.items():
        text_value = values.get(src_key, "")
        data[dest_key] = {"type": "text", "text": text_value}
    return data


def create_autofill_job_from_values(
    values: Dict[str, str],
    field_map: Optional[Dict[str, str]] = None,
    brand_template_id: Optional[str] = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Convenience wrapper to create an autofill job from values + field map."""
    data = build_autofill_data(values=values, field_map=field_map)
    return create_autofill_job(
        data=data,
        brand_template_id=brand_template_id,
        timeout_seconds=timeout_seconds,
        client=client,
    )



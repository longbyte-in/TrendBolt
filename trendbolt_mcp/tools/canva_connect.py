"""Canva Connect API helpers (access token based).

Implements:
- list_brand_templates
- get_brand_template_dataset

Docs:
- List brand templates: https://www.canva.dev/docs/connect/api-reference/brand-templates/list-brand-templates/
- Get dataset: https://www.canva.dev/docs/connect/api-reference/brand-templates/get-brand-template-dataset/
"""

from __future__ import annotations

import json
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
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Get dataset definition for a brand template."""
    s = get_settings()
    token = s.canva_access_token
    if not token:
        raise ValueError("Canva access token is required. Set CANVA_ACCESS_TOKEN in environment.")

    brand_template_id = s.canva_brand_template_id
    if not brand_template_id:
        raise ValueError("brand_template_id is required. Set CANVA_BRAND_TEMPLATE_ID in environment.")

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
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Create an autofill job using a brand template and data mapping.
    
    Uses CANVA_ACCESS_TOKEN and CANVA_BRAND_TEMPLATE_ID from environment.

    Docs: https://www.canva.dev/docs/connect/api-reference/autofill/create-autofill-job/
    """
    from ..logging import get_logger
    logger = get_logger(__name__)
    
    s = get_settings()
    
    # Use environment variables
    token = s.canva_access_token
    if not token:
        raise ValueError("Canva access token is required. Set CANVA_ACCESS_TOKEN in environment.")

    brand_template_id = s.canva_brand_template_id
    if not brand_template_id:
        raise ValueError("brand_template_id is required. Set CANVA_BRAND_TEMPLATE_ID in environment.")

    url = "https://api.canva.com/rest/v1/autofills"
    payload = {
        "brand_template_id": brand_template_id,
        "data": data,
    }

    # Log the request details
    logger.info(f"Creating autofill job for brand template: {brand_template_id}")
    logger.info(f"Request URL: {url}")
    logger.info(f"Request payload: {json.dumps(payload, indent=2)}")

    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    try:
        resp = client.post(url, headers={**_auth_headers(token), "Content-Type": "application/json"}, json=payload)
        
        # Log response details
        logger.info(f"Response status: {resp.status_code}")
        logger.info(f"Response headers: {dict(resp.headers)}")
        
        if resp.status_code != 200:
            logger.error(f"Request failed with status {resp.status_code}")
            logger.error(f"Response body: {resp.text}")
        
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


def build_autofill_data(
    values: Dict[str, Any], 
    field_map: Optional[Dict[str, str]] = None,
    image_fields: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Build Canva autofill data structure from simple values and field mapping.

    Args:
        values: Dictionary of field names to values (text or asset_id)
        field_map: Optional mapping from source keys to destination keys
        image_fields: Optional mapping of field names that should be treated as images
    
    Returns:
        Dictionary formatted for Canva autofill API:
        - Text: {"field_name": {"type": "text", "text": "value"}}
        - Image: {"field_name": {"type": "image", "asset_id": "asset_id"}}
    """
    mapping = field_map or {k: k for k in values.keys()}
    image_fields = image_fields or {}
    data: Dict[str, Any] = {}
    
    for dest_key, src_key in mapping.items():
        value = values.get(src_key, "")
        
        if dest_key in image_fields and value:
            # Handle as image asset
            data[dest_key] = {"type": "image", "asset_id": value}
        else:
            # Handle as text
            data[dest_key] = {"type": "text", "text": str(value)}
    
    return data


def create_autofill_job_from_values(
    values: Dict[str, Any],
    field_map: Optional[Dict[str, str]] = None,
    image_fields: Optional[Dict[str, str]] = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Convenience wrapper to create an autofill job from values + field map.
    
    Args:
        values: Dictionary of field names to values (text or asset_id)
        field_map: Optional mapping from source keys to destination keys
        image_fields: Optional mapping of field names that should be treated as images
        timeout_seconds: Request timeout
        client: Optional HTTP client
    """
    data = build_autofill_data(values=values, field_map=field_map, image_fields=image_fields)
    return create_autofill_job(
        data=data,
        timeout_seconds=timeout_seconds,
        client=client,
    )


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def create_url_asset_upload_job(
    image_url: str,
    asset_name: str,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Create an asset upload job to upload an image from URL to Canva.
    
    Docs: https://www.canva.dev/docs/connect/api-reference/assets/create-url-asset-upload-job/
    """
    from ..logging import get_logger
    logger = get_logger(__name__)
    
    s = get_settings()
    token = s.canva_access_token
    if not token:
        raise ValueError("Canva access token is required. Set CANVA_ACCESS_TOKEN in environment.")

    url = "https://api.canva.com/rest/v1/url-asset-uploads"
    
    payload = {
        "name": asset_name,
        "url": image_url
    }
    
    headers = {
        **_auth_headers(token),
        "Content-Type": "application/json"
    }

    logger.info(f"Creating URL asset upload job for: {asset_name}")
    logger.info(f"Request URL: {url}")
    logger.info(f"Image URL: {image_url}")

    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    try:
        resp = client.post(url, headers=headers, json=payload)
        
        logger.info(f"Response status: {resp.status_code}")
        if resp.status_code != 200:
            logger.error(f"Request failed with status {resp.status_code}")
            logger.error(f"Response body: {resp.text}")
        
        resp.raise_for_status()
        return resp.json()
    finally:
        if owns:
            client.close()


@retry(reraise=True, stop=stop_after_attempt(5), wait=wait_exponential(multiplier=0.5, max=8), retry=retry_if_exception_type(httpx.HTTPError))
def get_asset_upload_job(job_id: str, timeout_seconds: float = 30.0, client: Optional[httpx.Client] = None) -> dict:
    """Get the status and results of an asset upload job.
    
    Docs: https://www.canva.dev/docs/connect/api-reference/assets/get-asset-upload-job/
    """
    from ..logging import get_logger
    logger = get_logger(__name__)
    
    s = get_settings()
    token = s.canva_access_token
    if not token:
        raise ValueError("Canva access token is required. Set CANVA_ACCESS_TOKEN in environment.")

    if not job_id:
        raise ValueError("job_id is required")

    url = f"https://api.canva.com/rest/v1/asset-uploads/{job_id}"
    
    logger.info(f"Getting asset upload job status for: {job_id}")
    logger.info(f"Request URL: {url}")

    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    try:
        resp = client.get(url, headers=_auth_headers(token))
        
        logger.info(f"Response status: {resp.status_code}")
        logger.info(f"Response headers: {dict(resp.headers)}")
        
        if resp.status_code != 200:
            logger.error(f"Request failed with status {resp.status_code}")
            logger.error(f"Response body: {resp.text}")
        
        resp.raise_for_status()
        result = resp.json()
        
        logger.info(f"Job status: {result.get('job', {}).get('status', 'unknown')}")
        return result
    finally:
        if owns:
            client.close()


def upload_image_from_url(
    image_url: str,
    asset_name: str,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Upload an image from URL to Canva and return the asset ID.
    
    This function:
    1. Creates a URL asset upload job (no download needed!)
    2. Polls until upload completes
    3. Returns the asset ID
    
    Uses the more efficient URL-based upload API.
    """
    from ..logging import get_logger
    logger = get_logger(__name__)
    
    logger.info(f"Uploading image from URL: {image_url}")
    
    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    
    try:
        # Create URL asset upload job (much simpler!)
        logger.info("Creating URL asset upload job...")
        upload_result = create_url_asset_upload_job(
            image_url=image_url,
            asset_name=asset_name,
            timeout_seconds=timeout_seconds,
            client=client
        )
        
        job_id = upload_result["job"]["id"]
        logger.info(f"Upload job created: {job_id}")
        
        # Poll for completion
        import time
        max_attempts = 30  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            logger.info(f"Checking upload status (attempt {attempt}/{max_attempts})...")
            
            job_result = get_asset_upload_job(job_id, timeout_seconds=timeout_seconds, client=client)
            status = job_result["job"]["status"]
            
            if status == "success":
                asset_id = job_result["job"]["asset"]["id"]
                logger.info(f"✅ Upload successful! Asset ID: {asset_id}")
                return {
                    "success": True,
                    "asset_id": asset_id,
                    "asset": job_result["job"]["asset"]
                }
            elif status == "failed":
                error = job_result["job"].get("error", {})
                logger.error(f"❌ Upload failed: {error}")
                return {
                    "success": False,
                    "error": error,
                    "job_id": job_id
                }
            else:  # in_progress
                logger.info(f"Upload still in progress...")
                time.sleep(10)  # Wait 10 seconds before next check
        
        logger.error("❌ Upload timed out")
        return {
            "success": False,
            "error": {"code": "timeout", "message": "Upload job timed out"},
            "job_id": job_id
        }
        
    finally:
        if owns:
            client.close()



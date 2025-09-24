from __future__ import annotations
from typing import Optional, Dict, Any
import httpx
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..config import get_settings
from ..logging import get_logger

logger = get_logger(__name__)


def _auth_headers(token: str, rest: bool = False) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    if rest:
        headers.update({
            "Content-Type": "application/json",
            "LinkedIn-Version": "202509",
        })
    return headers


def _get_client(client: Optional[httpx.Client], timeout: float) -> tuple[httpx.Client, bool]:
    if client:
        return client, False
    return httpx.Client(timeout=timeout), True


@retry(reraise=True, stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=0.5, max=4),
       retry=retry_if_exception_type(httpx.HTTPError))
def create_image_post(
    image_url: str,
    text: str = "",
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> Dict[str, Any]:
    """Create an image post on LinkedIn Page using the new Images API (2025-09)."""
    s = get_settings()
    pid, token = s.linkedin_page_id, s.linkedin_access_token
    if not pid or not token:
        raise ValueError("LinkedIn page_id and access_token are required.")

    client, owns = _get_client(client, timeout_seconds)
    try:
        # Step 1: Initialize image upload using new Images API
        init_url = "https://api.linkedin.com/rest/images?action=initializeUpload"
        init_data = {
            "initializeUploadRequest": {
                "owner": f"urn:li:organization:{pid}"
            }
        }
        resp = client.post(init_url, headers=_auth_headers(token, rest=True), json=init_data)
        resp.raise_for_status()
        init_resp = resp.json()
        upload_url = init_resp["value"]["uploadUrl"]
        image_urn = init_resp["value"]["image"]

        # Step 2: Upload the image (PUT)
        img = client.get(image_url)
        img.raise_for_status()
        upload_resp = client.put(upload_url, headers={"Authorization": f"Bearer {token}"}, content=img.content)
        upload_resp.raise_for_status()

        # Wait for LinkedIn to process the image
        time.sleep(3)

        # Step 3: Create the post using new Posts API format
        post_url = "https://api.linkedin.com/rest/posts"
        post_data = {
            "author": f"urn:li:organization:{pid}",
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "content": {
                "media": {
                    "id": image_urn,
                    "altText": text[:120] or "Post from TrendBolt"
                }
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        resp = client.post(post_url, headers=_auth_headers(token, rest=True), json=post_data)
        resp.raise_for_status()
        
        # LinkedIn Posts API returns post ID in x-restli-id header for successful creation
        post_id = resp.headers.get("x-restli-id")
        
        # Try to parse JSON response if available, otherwise use header
        post_resp = {}
        if resp.text.strip():
            try:
                post_resp = resp.json()
            except ValueError:
                # Empty or invalid JSON response is normal for successful post creation
                pass
        
        # Use post ID from header or response body
        final_post_id = post_id or post_resp.get("id")

        return {
            "post_id": final_post_id,
            "image_urn": image_urn,
            "permalink_url": f"https://www.linkedin.com/feed/update/{final_post_id}" if final_post_id else None,
        }
    finally:
        if owns:
            client.close()


@retry(reraise=True, stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=0.5, max=4),
       retry=retry_if_exception_type(httpx.HTTPError))
def create_text_post(
    text: str,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> Dict[str, Any]:
    """Create a text-only post on LinkedIn Page using the new Posts API (2025-09)."""
    s = get_settings()
    pid, token = s.linkedin_page_id, s.linkedin_access_token
    if not pid or not token:
        raise ValueError("LinkedIn page_id and access_token are required.")

    client, owns = _get_client(client, timeout_seconds)
    try:
        post_url = "https://api.linkedin.com/rest/posts"
        data = {
            "author": f"urn:li:organization:{pid}",
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        resp = client.post(post_url, headers=_auth_headers(token, rest=True), json=data)
        resp.raise_for_status()
        
        # LinkedIn Posts API returns post ID in x-restli-id header for successful creation
        post_id = resp.headers.get("x-restli-id")
        
        # Try to parse JSON response if available, otherwise use header
        post_response = {}
        if resp.text.strip():
            try:
                post_response = resp.json()
            except ValueError:
                # Empty or invalid JSON response is normal for successful post creation
                pass
        
        # Use post ID from header or response body
        final_post_id = post_id or post_response.get("id")
        
        return {
            "post_id": final_post_id,
            "permalink_url": f"https://www.linkedin.com/feed/update/{final_post_id}" if final_post_id else None,
        }
    finally:
        if owns:
            client.close()


@retry(reraise=True, stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=0.5, max=4),
       retry=retry_if_exception_type(httpx.HTTPError))
def get_page_info(
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> Dict[str, Any]:
    """Fetch LinkedIn Page information using the new API (2025-09)."""
    s = get_settings()
    pid, token = s.linkedin_page_id, s.linkedin_access_token
    if not pid or not token:
        raise ValueError("LinkedIn page_id and access_token are required.")

    client, owns = _get_client(client, timeout_seconds)
    try:
        url = f"https://api.linkedin.com/v2/organizations/{pid}"
        resp = client.get(url, headers=_auth_headers(token))
        resp.raise_for_status()
        return resp.json()
    finally:
        if owns:
            client.close()

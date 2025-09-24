from __future__ import annotations
from typing import Optional, Dict, Any
import httpx
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..config import get_settings
from ..logging import get_logger

logger = get_logger(__name__)


def _auth_headers(token: str, rest: bool = False) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    if rest:
        headers.update({
            "Content-Type": "application/json",
            "LinkedIn-Version": "202501",
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
    """Create an image post on LinkedIn Page using the new Images API."""
    s = get_settings()
    pid, token = s.linkedin_page_id, s.linkedin_access_token
    if not pid or not token:
        raise ValueError("LinkedIn page_id and access_token are required.")

    client, owns = _get_client(client, timeout_seconds)
    try:
        # Step 1: Initialize image upload
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

        # Wait a bit for LinkedIn to process the image
        time.sleep(2)

        # Step 3: Create the post
        post_url = "https://api.linkedin.com/rest/posts"
        post_data = {
            "author": f"urn:li:organization:{pid}",
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED"},
            "content": {
                "media": [
                    {
                        "id": image_urn,
                        "altText": text[:120] or "Post from TrendBolt"
                    }
                ]
            },
            "lifecycleState": "PUBLISHED"
        }
        resp = client.post(post_url, headers=_auth_headers(token, rest=True), json=post_data)
        resp.raise_for_status()
        post_resp = resp.json()

        return {
            "post_id": post_resp.get("id"),
            "image_urn": image_urn,
            "permalink_url": f"https://www.linkedin.com/feed/update/{post_resp.get('id')}" if post_resp.get("id") else None,
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
    """Create a text-only post on LinkedIn Page."""
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
            "distribution": {"feedDistribution": "MAIN_FEED"},
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        resp = client.post(post_url, headers=_auth_headers(token, rest=True), json=data)
        resp.raise_for_status()
        post_response = resp.json()
        return {
            "post_id": post_response.get("id"),
            "permalink_url": f"https://www.linkedin.com/feed/update/{post_response.get('id')}" if post_response.get("id") else None,
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
    """Fetch LinkedIn Page information."""
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

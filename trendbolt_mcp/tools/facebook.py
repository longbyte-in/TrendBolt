"""Facebook Graph API publishing helper."""

from __future__ import annotations

from typing import Optional

import httpx

from ..config import get_settings
from ..logging import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


logger = get_logger(__name__)


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def publish_photo(
    caption: str,
    image_url: str,
    page_id: str | None = None,
    access_token: str | None = None,
    scheduled_publish_time: int | None = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Publish a photo to a Facebook Page using Graph API.

    Docs: https://developers.facebook.com/docs/graph-api/reference/page/photos/
    """
    s = get_settings()
    pid = page_id or s.facebook_page_id
    token = access_token or s.facebook_page_access_token
    
    if not pid:
        raise ValueError("Facebook page_id is required. Set FACEBOOK_PAGE_ID in environment or pass page_id parameter.")
    if not token:
        raise ValueError("Facebook access token is required. Set FACEBOOK_PAGE_ACCESS_TOKEN in environment or pass access_token parameter.")
    
    url = f"https://graph.facebook.com/v19.0/{pid}/photos"
    data: dict[str, str] = {"caption": caption, "url": image_url, "access_token": token}
    if scheduled_publish_time is not None:
        data["published"] = "false"
        data["scheduled_publish_time"] = str(scheduled_publish_time)
    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    try:
        resp = client.post(url, data=data)
        resp.raise_for_status()
        js = resp.json()
        # photos returns id; we can fetch permalink via feed or build URL if needed
        return {"post_id": js.get("post_id") or js.get("id"), "permalink_url": None}
    except httpx.HTTPError as e:
        raise
    finally:
        if owns:
            client.close()



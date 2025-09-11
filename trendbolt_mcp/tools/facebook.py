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


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def create_feed_post(
    message: str,
    link: str | None = None,
    published: bool = True,
    scheduled_publish_time: int | None = None,
    page_id: str | None = None,
    access_token: str | None = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Create a Page feed post.

    Docs: https://developers.facebook.com/docs/pages-api/posts/
    Required permissions: pages_manage_posts, pages_read_engagement, pages_manage_engagement
    """
    s = get_settings()
    pid = page_id or s.facebook_page_id
    token = access_token or s.facebook_page_access_token
    if not pid:
        raise ValueError("Facebook page_id is required. Set FACEBOOK_PAGE_ID or pass page_id.")
    if not token:
        raise ValueError("Facebook access token is required. Set FACEBOOK_PAGE_ACCESS_TOKEN or pass access_token.")

    url = f"https://graph.facebook.com/v23.0/{pid}/feed"
    data: dict[str, str] = {"message": message, "access_token": token}
    if link:
        data["link"] = link
    if not published:
        data["published"] = "false"
        if scheduled_publish_time is not None:
            data["scheduled_publish_time"] = str(scheduled_publish_time)

    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    try:
        resp = client.post(url, data=data)
        resp.raise_for_status()
        return resp.json()  # expects {"id": "page_post_id"}
    finally:
        if owns:
            client.close()


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
    image_url: str,
    message: str | None = None,
    caption: str | None = None,
    published: bool = True,
    page_id: str | None = None,
    access_token: str | None = None,
    scheduled_publish_time: int | None = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Publish a photo to a Facebook Page using Graph API.
    
    Uses the URL-based photo upload method as described in:
    https://developers.facebook.com/docs/graph-api/reference/page/photos/
    
    Args:
        image_url: URL of the image to upload (from Canva thumbnail)
        message: Text message to accompany the photo (optional)
        caption: Alias for message (for backward compatibility)
        published: Whether to publish immediately (default: True)
        page_id: Facebook Page ID (uses FACEBOOK_PAGE_ID from env if not provided)
        access_token: Page access token (uses FACEBOOK_PAGE_ACCESS_TOKEN from env if not provided)
        scheduled_publish_time: Unix timestamp for scheduled posts (requires published=False)
        timeout_seconds: Request timeout
        client: Optional httpx client for connection reuse
        
    Returns:
        dict: {"post_id": str, "photo_id": str, "permalink_url": str}
        
    Raises:
        ValueError: If required parameters are missing
        httpx.HTTPError: If API request fails
    """
    s = get_settings()
    pid = page_id or s.facebook_page_id
    token = access_token or s.facebook_page_access_token
    
    if not pid:
        raise ValueError("Facebook page_id is required. Set FACEBOOK_PAGE_ID in environment or pass page_id parameter.")
    if not token:
        raise ValueError("Facebook access token is required. Set FACEBOOK_PAGE_ACCESS_TOKEN in environment or pass access_token parameter.")
    
    # Use message or caption (caption is deprecated but kept for compatibility)
    text_content = message or caption or ""
    
    url = f"https://graph.facebook.com/v23.0/{pid}/photos"
    data: dict[str, str] = {
        "url": image_url,
        "access_token": token
    }
    
    # Add message/caption if provided
    if text_content:
        data["message"] = text_content
    
    # Handle publishing and scheduling
    if not published:
        data["published"] = "false"
        if scheduled_publish_time is not None:
            data["scheduled_publish_time"] = str(scheduled_publish_time)
    elif scheduled_publish_time is not None:
        # If scheduled_publish_time is provided but published=True, treat as scheduled
        data["published"] = "false"
        data["scheduled_publish_time"] = str(scheduled_publish_time)
    
    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    
    try:
        logger.info(f"Publishing photo to Facebook Page {pid} with URL: {image_url}")
        resp = client.post(url, data=data)
        resp.raise_for_status()
        js = resp.json()
        
        # Facebook returns both photo ID and post ID
        photo_id = js.get("id")
        post_id = js.get("post_id")
        
        # Build permalink URL
        permalink_url = f"https://www.facebook.com/{pid}/posts/{post_id}" if post_id else None
        
        result = {
            "post_id": post_id,
            "photo_id": photo_id,
            "permalink_url": permalink_url
        }
        
        logger.info(f"✅ Successfully published photo. Post ID: {post_id}, Photo ID: {photo_id}")
        return result
        
    except httpx.HTTPError as e:
        logger.error(f"❌ Failed to publish photo to Facebook: {e}")
        raise
    finally:
        if owns:
            client.close()


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def publish_multi_photo_post(
    message: str,
    image_urls: list[str],
    published: bool = True,
    page_id: str | None = None,
    access_token: str | None = None,
    scheduled_publish_time: int | None = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Publish a multi-photo post to Facebook Page.
    
    First uploads all photos as unpublished, then creates a feed post with attached media.
    Based on: https://developers.facebook.com/docs/graph-api/reference/page/photos/
    
    Args:
        message: Text message for the post
        image_urls: List of image URLs to upload
        published: Whether to publish immediately (default: True)
        page_id: Facebook Page ID (uses FACEBOOK_PAGE_ID from env if not provided)
        access_token: Page access token (uses FACEBOOK_PAGE_ACCESS_TOKEN from env if not provided)
        scheduled_publish_time: Unix timestamp for scheduled posts (requires published=False)
        timeout_seconds: Request timeout
        client: Optional httpx client for connection reuse
        
    Returns:
        dict: {"post_id": str, "photo_ids": list[str], "permalink_url": str}
    """
    s = get_settings()
    pid = page_id or s.facebook_page_id
    token = access_token or s.facebook_page_access_token
    
    if not pid:
        raise ValueError("Facebook page_id is required. Set FACEBOOK_PAGE_ID in environment or pass page_id parameter.")
    if not token:
        raise ValueError("Facebook access token is required. Set FACEBOOK_PAGE_ACCESS_TOKEN in environment or pass access_token parameter.")
    
    if not image_urls:
        raise ValueError("At least one image URL is required for multi-photo post.")
    
    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    
    try:
        # Step 1: Upload all photos as unpublished
        photo_ids = []
        logger.info(f"Uploading {len(image_urls)} photos to Facebook...")
        
        for i, image_url in enumerate(image_urls):
            upload_data = {
                "url": image_url,
                "published": "false",  # Upload as unpublished first
                "access_token": token
            }
            
            upload_url = f"https://graph.facebook.com/v23.0/{pid}/photos"
            resp = client.post(upload_url, data=upload_data)
            resp.raise_for_status()
            
            photo_data = resp.json()
            photo_id = photo_data.get("id")
            if photo_id:
                photo_ids.append(photo_id)
                logger.info(f"✅ Uploaded photo {i+1}/{len(image_urls)}: {photo_id}")
            else:
                logger.warning(f"⚠️ Failed to get photo ID for image {i+1}")
        
        if not photo_ids:
            raise ValueError("Failed to upload any photos")
        
        # Step 2: Create feed post with attached media
        feed_data = {
            "message": message,
            "access_token": token
        }
        
        # Add attached media
        for i, photo_id in enumerate(photo_ids):
            feed_data[f"attached_media[{i}]"] = f'{{"media_fbid":"{photo_id}"}}'
        
        # Handle publishing and scheduling
        if not published:
            feed_data["published"] = "false"
            if scheduled_publish_time is not None:
                feed_data["scheduled_publish_time"] = str(scheduled_publish_time)
        elif scheduled_publish_time is not None:
            feed_data["published"] = "false"
            feed_data["scheduled_publish_time"] = str(scheduled_publish_time)
        
        # Create the feed post
        feed_url = f"https://graph.facebook.com/v23.0/{pid}/feed"
        resp = client.post(feed_url, data=feed_data)
        resp.raise_for_status()
        
        feed_data = resp.json()
        post_id = feed_data.get("id")
        permalink_url = f"https://www.facebook.com/{pid}/posts/{post_id}" if post_id else None
        
        result = {
            "post_id": post_id,
            "photo_ids": photo_ids,
            "permalink_url": permalink_url
        }
        
        logger.info(f"✅ Successfully published multi-photo post. Post ID: {post_id}")
        return result
        
    except httpx.HTTPError as e:
        logger.error(f"❌ Failed to publish multi-photo post to Facebook: {e}")
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


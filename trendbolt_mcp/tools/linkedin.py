"""LinkedIn Advertising API publishing helper.

This implementation uses the LinkedIn Advertising API with UGC (User Generated Content) endpoints
to create and publish posts on LinkedIn Pages. Requires LinkedIn Advertising API Development Tier access.
"""

from __future__ import annotations

from typing import Optional

import httpx

from ..config import get_settings
from ..logging import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


logger = get_logger(__name__)


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def create_image_post(
    image_url: str,
    text: str,
    page_id: str | None = None,
    access_token: str | None = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Create an image post on LinkedIn Page using Advertising API UGC endpoints.
    
    This function creates a post with an image on a LinkedIn Page using the UGC API.
    Requires LinkedIn Advertising API Development Tier access and appropriate permissions.
    
    Args:
        image_url: URL of the image to post (from Canva)
        text: Text content for the post
        page_id: LinkedIn Page ID (uses LINKEDIN_PAGE_ID from env if not provided)
        access_token: LinkedIn access token (uses LINKEDIN_ACCESS_TOKEN from env if not provided)
        timeout_seconds: Request timeout
        client: Optional httpx client for connection reuse
        
    Returns:
        dict: {"post_id": str, "asset_id": str, "permalink_url": str}
        
    Raises:
        ValueError: If required parameters are missing
        httpx.HTTPError: If API request fails
    """
    s = get_settings()
    pid = page_id or s.linkedin_page_id
    token = access_token or s.linkedin_access_token
    
    if not pid:
        raise ValueError("LinkedIn page_id is required. Set LINKEDIN_PAGE_ID in environment or pass page_id parameter.")
    if not token:
        raise ValueError("LinkedIn access token is required. Set LINKEDIN_ACCESS_TOKEN in environment or pass access_token parameter.")
    
    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    
    try:
        # Step 1: Register the image URL with LinkedIn using UGC API
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        
        register_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:organization:{pid}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        logger.info(f"Registering image upload for LinkedIn Page {pid}")
        resp = client.post(register_url, headers=register_headers, json=register_data)
        resp.raise_for_status()
        
        register_response = resp.json()
        upload_url = register_response["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_id = register_response["value"]["asset"]
        
        # Step 2: Upload the image to LinkedIn
        logger.info(f"Uploading image to LinkedIn: {image_url}")
        
        # Download image from URL and upload to LinkedIn
        image_resp = client.get(image_url)
        image_resp.raise_for_status()
        
        upload_headers = {
            "Authorization": f"Bearer {token}"
        }
        
        upload_resp = client.post(upload_url, headers=upload_headers, content=image_resp.content)
        upload_resp.raise_for_status()
        
        # Step 3: Create the post with the uploaded image using Posts API
        post_url = "https://api.linkedin.com/rest/posts"
        
        post_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202304"
        }
        
        post_data = {
            "author": f"urn:li:organization:{pid}",
            "commentary": text,
            "visibility": "PUBLIC",
            "lifecycleState": "PUBLISHED",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "media": [
                {
                    "status": "READY",
                    "description": {
                        "text": text
                    },
                    "media": asset_id,
                    "title": {
                        "text": "Post from TrendBolt"
                    }
                }
            ]
        }
        
        logger.info(f"Creating LinkedIn post with image using Posts API")
        resp = client.post(post_url, headers=post_headers, json=post_data)
        resp.raise_for_status()
        
        post_response = resp.json()
        post_id = post_response.get("id")
        
        # Build permalink URL (LinkedIn doesn't provide direct permalink in response)
        permalink_url = f"https://www.linkedin.com/feed/update/{post_id}" if post_id else None
        
        result = {
            "post_id": post_id,
            "asset_id": asset_id,
            "permalink_url": permalink_url
        }
        
        logger.info(f"✅ Successfully created LinkedIn UGC post. Post ID: {post_id}")
        return result
        
    except httpx.HTTPError as e:
        logger.error(f"❌ Failed to create LinkedIn post: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        raise
    finally:
        if owns:
            client.close()


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def create_text_post(
    text: str,
    page_id: str | None = None,
    access_token: str | None = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Create a text-only post on LinkedIn Page using UGC API.
    
    Args:
        text: Text content for the post
        page_id: LinkedIn Page ID (uses LINKEDIN_PAGE_ID from env if not provided)
        access_token: LinkedIn access token (uses LINKEDIN_ACCESS_TOKEN from env if not provided)
        timeout_seconds: Request timeout
        client: Optional httpx client for connection reuse
        
    Returns:
        dict: {"post_id": str, "permalink_url": str}
    """
    s = get_settings()
    pid = page_id or s.linkedin_page_id
    token = access_token or s.linkedin_access_token
    
    if not pid:
        raise ValueError("LinkedIn page_id is required. Set LINKEDIN_PAGE_ID in environment or pass page_id parameter.")
    if not token:
        raise ValueError("LinkedIn access token is required. Set LINKEDIN_ACCESS_TOKEN in environment or pass access_token parameter.")
    
    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    
    try:
        post_url = "https://api.linkedin.com/rest/posts"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202304"
        }
        
        data = {
            "author": f"urn:li:organization:{pid}",
            "commentary": text,
            "visibility": "PUBLIC",
            "lifecycleState": "PUBLISHED",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            }
        }
        
        logger.info(f"Creating LinkedIn text post using Posts API")
        resp = client.post(post_url, headers=headers, json=data)
        resp.raise_for_status()
        
        post_response = resp.json()
        post_id = post_response.get("id")
        permalink_url = f"https://www.linkedin.com/feed/update/{post_id}" if post_id else None
        
        result = {
            "post_id": post_id,
            "permalink_url": permalink_url
        }
        
        logger.info(f"✅ Successfully created LinkedIn text post. Post ID: {post_id}")
        return result
        
    except httpx.HTTPError as e:
        logger.error(f"❌ Failed to create LinkedIn text post: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        raise
    finally:
        if owns:
            client.close()


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError))
def get_page_info(
    page_id: str | None = None,
    access_token: str | None = None,
    timeout_seconds: float = 30.0,
    client: Optional[httpx.Client] = None,
) -> dict:
    """Get LinkedIn Page information.
    
    Args:
        page_id: LinkedIn Page ID (uses LINKEDIN_PAGE_ID from env if not provided)
        access_token: LinkedIn access token (uses LINKEDIN_ACCESS_TOKEN from env if not provided)
        timeout_seconds: Request timeout
        client: Optional httpx client for connection reuse
        
    Returns:
        dict: Page information including name, vanityName, etc.
    """
    s = get_settings()
    pid = page_id or s.linkedin_page_id
    token = access_token or s.linkedin_access_token
    
    if not pid:
        raise ValueError("LinkedIn page_id is required. Set LINKEDIN_PAGE_ID in environment or pass page_id parameter.")
    if not token:
        raise ValueError("LinkedIn access token is required. Set LINKEDIN_ACCESS_TOKEN in environment or pass access_token parameter.")
    
    owns = False
    if client is None:
        client = httpx.Client(timeout=timeout_seconds)
        owns = True
    
    try:
        url = f"https://api.linkedin.com/v2/organizations/{pid}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        logger.info(f"Fetching LinkedIn Page info for {pid}")
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        
        page_info = resp.json()
        logger.info(f"✅ Successfully fetched LinkedIn Page info")
        return page_info
        
    except httpx.HTTPError as e:
        logger.error(f"❌ Failed to fetch LinkedIn Page info: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        raise
    finally:
        if owns:
            client.close()

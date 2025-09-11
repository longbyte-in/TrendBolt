"""
TrendBolt MCP Server
A Model Context Protocol server for social media automation.

Provides tools for:
- Reddit trending content discovery
- LLM-powered content generation  
- Canva design creation
- Facebook publishing

Resources:
- Trending topics from Reddit
- Generated content templates
- Design assets

Prompts:
- Content generation templates
- Design brief creation
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, 
    TextContent, 
    Resource, 
    Prompt,
    PromptMessage,
    PromptArgument
)
from .config import get_settings
from .tools.reddit import get_trending, get_post_by_id
from .tools.llm import generate_canvas_post
# from .tools.canva import create_design  # removed: legacy bridge
from .tools.canva_connect import list_brand_templates as canva_list_brand_templates
from .tools.canva_connect import (
    get_brand_template_dataset as canva_get_brand_template_dataset,
)
from .tools.canva_connect import (
    create_autofill_job_from_values as canva_create_autofill_job,
    get_autofill_job as canva_get_autofill_job,
    build_autofill_data,
    upload_image_from_url,
    create_url_asset_upload_job,
    get_asset_upload_job,
)
from .tools.facebook import publish_photo, create_feed_post



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("trendbolt")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="reddit_get_trending",
            description="Fetch trending posts from Reddit subreddits",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddits": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of subreddit names to fetch from",
                        "default": ["technology"]
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["hot", "top", "new"],
                        "description": "Sorting strategy for posts",
                        "default": "hot"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of posts to fetch",
                        "default": 10
                    },
                    "min_score": {
                        "type": "integer", 
                        "description": "Minimum score threshold for posts",
                        "default": 100
                    },
                    "time_filter": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "description": "Time filter for 'top' strategy",
                        "default": "day"
                    }
                }
            }
        ),
        Tool(
            name="llm_generate_content",
            description="Generate social media content using LLM",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "object",
                        "description": "Reddit topic object with title, url, etc."
                    },
                    "reddit_post_id": {
                        "type": "string",
                        "description": "Reddit post ID (e.g., t3_1ndjq1c) - will fetch post details"
                    },
                    "brand": {
                        "type": "object",
                        "description": "Brand configuration",
                        "default": {"cta": "Follow TrendBolt", "voice": "engaging"}
                    }
                },
                "anyOf": [
                    {"required": ["topic"]},
                    {"required": ["reddit_post_id"]}
                ]
            }
        ),
        Tool(
            name="canva_list_brand_templates",
            description="List Canva brand templates for the current user (requires access token)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "ownership": {"type": "string", "enum": ["any", "owned", "shared"]},
                    "sort_by": {"type": "string", "enum": ["relevance", "modified_descending", "modified_ascending", "title_descending", "title_ascending"]},
                    "dataset": {"type": "string", "enum": ["any", "non_empty"]},
                    "continuation": {"type": "string"}
                }
            }
        ),
        Tool(
            name="canva_get_brand_template_dataset",
            description="Get dataset definition for a Canva brand template",
            inputSchema={
                "type": "object",
                "properties": {
                    "brand_template_id": {"type": "string", "description": "Brand template ID"}
                },
                "required": ["brand_template_id"]
            }
        ),
        Tool(
            name="canva_create_autofill_job",
            description="Create an autofill job for a brand template. Automatically uploads image URLs to Canva and includes them as assets. Uses CANVA_BRAND_TEMPLATE_ID from environment if brand_template_id not provided.",
            inputSchema={
                "type": "object",
                "properties": {
                    "brand_template_id": {"type": "string", "description": "Brand template ID (optional - uses CANVA_BRAND_TEMPLATE_ID from env if not provided)"},
                    "data": {"type": "object", "description": "Autofill data mapping with simple key-value pairs. Image URLs (ending in .jpg, .png, etc.) are automatically uploaded to Canva and converted to asset IDs."}
                },
                "required": ["data"]
            }
        ),
        Tool(
            name="canva_get_autofill_job",
            description="Get autofill job status and result",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"}
                },
                "required": ["job_id"]
            }
        ),
        Tool(
            name="canva_upload_image",
            description="Upload an image from URL to Canva and get asset ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {"type": "string", "description": "URL of the image to upload"},
                    "asset_name": {"type": "string", "description": "Name for the asset in Canva"}
                },
                "required": ["image_url", "asset_name"]
            }
        ),
        Tool(
            name="canva_get_asset_upload_job",
            description="Get asset upload job status and result",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"}
                },
                "required": ["job_id"]
            }
        ),
        Tool(
            name="canva_create_url_asset_upload_job",
            description="Create an asset upload job from URL (more efficient than binary upload)",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {"type": "string", "description": "URL of the image to upload"},
                    "asset_name": {"type": "string", "description": "Name for the asset in Canva"}
                },
                "required": ["image_url", "asset_name"]
            }
        ),
        Tool(
            name="facebook_publish_post",
            description="Publish a post to Facebook",
            inputSchema={
                "type": "object",
                "properties": {
                    "caption": {
                        "type": "string",
                        "description": "Post caption text"
                    },
                    "image_url": {
                        "type": "string",
                        "description": "URL of image to post"
                    },
                    "page_id": {
                        "type": "string",
                        "description": "Facebook page ID"
                    }
                },
                "required": ["caption", "image_url", "page_id"]
            }
        ),
        Tool(
            name="facebook_create_post",
            description="Create a feed post on a Facebook Page",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "link": {"type": "string"},
                    "published": {"type": "boolean", "default": True},
                    "scheduled_publish_time": {"type": "integer"},
                    "page_id": {"type": "string"}
                },
                "required": ["message", "page_id"]
            }
        ),
        Tool(
            name="trendbolt_pipeline",
            description="Run complete TrendBolt pipeline: Reddit → LLM → Canva → Facebook",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddits": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Subreddits to fetch from",
                        "default": ["technology"]
                    },
                    "template_id": {
                        "type": "string",
                        "description": "Canva template ID",
                        "default": "trendbolt_template_default"
                    },
                    "facebook_page_id": {
                        "type": "string",
                        "description": "Facebook page ID to post to"
                    },
                    "min_score": {
                        "type": "integer",
                        "description": "Minimum Reddit post score",
                        "default": 200
                    }
                },
                "required": ["facebook_page_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "reddit_get_trending":
            result = await get_trending(
                subreddits=arguments.get("subreddits", ["technology"]),
                strategy=arguments.get("strategy", "hot"),
                limit=arguments.get("limit", 10),
                min_score=arguments.get("min_score", 100),
                time_filter=arguments.get("time_filter", "day")
            )
            
        elif name == "llm_generate_content":
            # Handle both topic object and reddit_post_id
            if "reddit_post_id" in arguments:
                # Fetch Reddit post details by ID
                reddit_post_id = arguments["reddit_post_id"]
                topic = await get_post_by_id(reddit_post_id)
                if not topic:
                    result = {"error": f"Could not fetch Reddit post {reddit_post_id}"}
                else:
                    result = generate_canvas_post(
                        topic=topic,
                        brand=arguments.get("brand", {"cta": "Follow TrendBolt"})
                    )
            else:
                topic = arguments["topic"]
                result = generate_canvas_post(
                    topic=topic,
                    brand=arguments.get("brand", {"cta": "Follow TrendBolt"})
                )
            
        elif name == "canva_list_brand_templates":
            result = canva_list_brand_templates(
                query=arguments.get("query"),
                ownership=arguments.get("ownership"),
                sort_by=arguments.get("sort_by"),
                dataset=arguments.get("dataset"),
                continuation=arguments.get("continuation"),
            )

        elif name == "canva_get_brand_template_dataset":
            result = canva_get_brand_template_dataset(
                brand_template_id=arguments["brand_template_id"]
            )
        elif name == "canva_create_autofill_job":
            # Automatically handle image uploads and include in autofill data
            raw_data = arguments["data"]
            
            # Check for image URLs and upload them automatically
            processed_data = {}
            image_fields = {}
            
            for key, value in raw_data.items():
                if isinstance(value, str) and (value.startswith('http') and any(ext in value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'])):
                    # This looks like an image URL - upload it
                    logger.info(f"Detected image URL for field '{key}': {value}")
                    try:
                        upload_result = upload_image_from_url(
                            image_url=value,
                            asset_name=f"Auto-uploaded {key}"
                        )
                        if upload_result["success"]:
                            asset_id = upload_result["asset_id"]
                            processed_data[key] = asset_id
                            image_fields[key] = key  # Mark as image field
                            logger.info(f"✅ Uploaded image for '{key}', asset ID: {asset_id}")
                        else:
                            logger.warning(f"❌ Failed to upload image for '{key}': {upload_result.get('error')}")
                            processed_data[key] = value  # Keep original URL as fallback
                    except Exception as e:
                        logger.error(f"❌ Error uploading image for '{key}': {e}")
                        processed_data[key] = value  # Keep original URL as fallback
                else:
                    # Regular text field
                    processed_data[key] = value
            
            result = canva_create_autofill_job(
                values=processed_data,
                image_fields=image_fields,
                brand_template_id=arguments.get("brand_template_id")
            )
        elif name == "canva_get_autofill_job":
            result = canva_get_autofill_job(
                job_id=arguments["job_id"]
            )
        elif name == "canva_upload_image":
            result = upload_image_from_url(
                image_url=arguments["image_url"],
                asset_name=arguments["asset_name"]
            )
        elif name == "canva_get_asset_upload_job":
            result = get_asset_upload_job(
                job_id=arguments["job_id"]
            )
        elif name == "canva_create_url_asset_upload_job":
            result = create_url_asset_upload_job(
                image_url=arguments["image_url"],
                asset_name=arguments["asset_name"]
            )
            
        elif name == "facebook_publish_post":
            result = publish_photo(
                caption=arguments["caption"],
                image_url=arguments["image_url"],
                page_id=arguments["page_id"]
            )
        elif name == "facebook_create_post":
            result = create_feed_post(
                message=arguments["message"],
                link=arguments.get("link"),
                published=arguments.get("published", True),
                scheduled_publish_time=arguments.get("scheduled_publish_time"),
                page_id=arguments["page_id"],
            )
            
        elif name == "trendbolt_pipeline":
            # Run complete pipeline
            topics = await get_trending(
                subreddits=arguments.get("subreddits", ["technology"]),
                min_score=arguments.get("min_score", 200)
            )
            
            if not topics:
                result = {"status": "no_topics", "message": "No trending topics found"}
            else:
                topic = topics[0]
                content = generate_canvas_post(
                    topic=topic,
                    brand={"cta": "Follow TrendBolt"}
                )
                # Note: Canva creation via Connect API requires separate autofill job flow.
                # Here we return content and allow caller to choose a brand template via tools.
                post = {"status": "skipped", "reason": "design_creation_moved_to_canva_connect_flow"}
                
                result = {
                    "status": "success",
                    "topic": topic,
                    "content": content,
                    "design": None,
                    "post": post
                }
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "tool": name
        }, indent=2))]


@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="trendbolt://trending-topics",
            name="Trending Topics",
            description="Current trending topics from Reddit",
            mimeType="application/json"
        ),
        Resource(
            uri="trendbolt://content-templates",
            name="Content Templates", 
            description="Pre-built content generation templates",
            mimeType="application/json"
        ),
        Resource(
            uri="trendbolt://design-assets",
            name="Design Assets",
            description="Generated design assets and exports",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content."""
    if uri == "trendbolt://trending-topics":
        topics = await get_trending(["technology"], limit=5)
        return json.dumps({"trending_topics": topics}, indent=2)
        
    elif uri == "trendbolt://content-templates":
        templates = {
            "viral_post": {
                "structure": "Hook + Context + Value + CTA",
                "voice": "engaging, informative",
                "max_length": 2200
            },
            "design_brief": {
                "headline": "Eye-catching title (max 60 chars)",
                "subtext": "Compelling subtitle (max 120 chars)", 
                "cta": "Clear action (max 20 chars)"
            }
        }
        return json.dumps(templates, indent=2)
        
    elif uri == "trendbolt://design-assets":
        return json.dumps({"message": "Design assets will appear here after generation"}, indent=2)
        
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available prompts."""
    return [
        Prompt(
            name="generate_viral_content",
            description="Generate viral social media content from a trending topic",
            arguments=[
                PromptArgument(
                    name="topic_title",
                    description="Title of the trending topic",
                    required=True
                ),
                PromptArgument(
                    name="topic_url", 
                    description="URL of the trending topic",
                    required=True
                ),
                PromptArgument(
                    name="brand_voice",
                    description="Brand voice and tone",
                    required=False
                )
            ]
        ),
        Prompt(
            name="create_design_brief",
            description="Create a design brief for Canva",
            arguments=[
                PromptArgument(
                    name="content_caption",
                    description="Social media caption content",
                    required=True
                ),
                PromptArgument(
                    name="target_audience",
                    description="Target audience for the design",
                    required=False
                )
            ]
        )
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str]) -> List[PromptMessage]:
    """Get prompt content."""
    if name == "generate_viral_content":
        topic_title = arguments["topic_title"]
        topic_url = arguments["topic_url"]
        brand_voice = arguments.get("brand_voice", "engaging and informative")
        
        return [
            PromptMessage(
                role="user",
                content=PromptMessage.TextContent(
                    type="text",
                    text=f"""Generate viral social media content for this trending topic:

Topic: {topic_title}
Source: {topic_url}
Brand Voice: {brand_voice}

Create:
1. An engaging caption (max 2200 chars) that hooks readers and encourages interaction
2. Alt text for accessibility (max 125 chars)
3. 3-5 relevant hashtags
4. A design brief with headline, subtext, and CTA

Make it compelling, informative, and shareable. Avoid clickbait but make it engaging."""
                )
            )
        ]
        
    elif name == "create_design_brief":
        caption = arguments["content_caption"]
        audience = arguments.get("target_audience", "general social media users")
        
        return [
            PromptMessage(
                role="user", 
                content=PromptMessage.TextContent(
                    type="text",
                    text=f"""Create a design brief for this social media content:

Caption: {caption}
Target Audience: {audience}

Design Brief should include:
- Eye-catching headline (max 60 chars)
- Compelling subtext (max 120 chars) 
- Clear call-to-action button text (max 20 chars)
- Color theme recommendation (dark_on_light or light_on_dark)
- Visual guidance (icons, style, layout suggestions)

Make it visually appealing and aligned with the content tone."""
                )
            )
        ]
        
    else:
        raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Run the MCP server."""
    logger.info("Starting TrendBolt MCP Server...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP server started, waiting for client connections...")
            
            # Create initialization options with server capabilities
            init_options = server.create_initialization_options()
            
            await server.run(
                read_stream,
                write_stream,
                init_options
            )
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error("MCP server error: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())
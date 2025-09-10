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
from .tools.reddit import get_trending
from .tools.llm import generate_canvas_post
from .tools.canva import create_design
from .tools.facebook import publish_photo



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
                    "brand": {
                        "type": "object",
                        "description": "Brand configuration",
                        "default": {"cta": "Follow TrendBolt", "voice": "engaging"}
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="canva_create_design",
            description="Create a design in Canva",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "Canva template ID to use"
                    },
                    "design_brief": {
                        "type": "object",
                        "description": "Design brief with headline, subtext, etc."
                    },
                    "export": {
                        "type": "object",
                        "description": "Export configuration",
                        "default": {"format": "PNG", "quality": "HIGH"}
                    }
                },
                "required": ["template_id", "design_brief"]
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
            result = generate_canvas_post(
                topic=arguments["topic"],
                brand=arguments.get("brand", {"cta": "Follow TrendBolt"})
            )
            
        elif name == "canva_create_design":
            result = create_design(
                template_id=arguments["template_id"],
                design_brief=arguments["design_brief"],
                export=arguments.get("export", {"format": "PNG", "quality": "HIGH"})
            )
            
        elif name == "facebook_publish_post":
            result = publish_photo(
                caption=arguments["caption"],
                image_url=arguments["image_url"],
                page_id=arguments["page_id"]
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
                design = create_design(
                    template_id=arguments.get("template_id", "trendbolt_template_default"),
                    design_brief=content["design_brief"]
                )
                post = publish_photo(
                    caption=content["caption"],
                    image_url=design["asset_url"],
                    page_id=arguments["facebook_page_id"]
                )
                
                result = {
                    "status": "success",
                    "topic": topic,
                    "content": content,
                    "design": design,
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
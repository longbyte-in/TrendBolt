"""
TrendBolt MCP Server
A Model Context Protocol server for social media automation.

Provides tools for:
- Reddit trending content discovery
- LLM-powered content generation  
- Canva design creation
- LinkedIn publishing

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
from .pipeline import run_once



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
                "properties": {}
            }
        ),
        Tool(
            name="canva_create_autofill_job",
            description="Create an autofill job for a brand template. Automatically uploads image URLs to Canva and includes them as assets. Uses CANVA_BRAND_TEMPLATE_ID from environment.",
            inputSchema={
                "type": "object",
                "properties": {
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
            name="linkedin_create_image_post",
            description="Create an image post on LinkedIn Page using Posts API. Requires LinkedIn Advertising API access.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "URL of the image to post (typically from Canva thumbnail)"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text content for the post (optional, defaults to empty string)"
                    }
                },
                "required": ["image_url"]
            }
        ),
        Tool(
            name="linkedin_create_text_post",
            description="Create a text-only post on LinkedIn Page using Posts API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text content for the post"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="linkedin_get_page_info",
            description="Get LinkedIn Page information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="trendbolt_pipeline",
            description="Run complete TrendBolt pipeline: Reddit → LLM → Canva → LinkedIn",
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
                    "linkedin_page_id": {
                        "type": "string",
                        "description": "LinkedIn page ID to post to"
                    },
                    "min_score": {
                        "type": "integer",
                        "description": "Minimum Reddit post score",
                        "default": 200
                    }
                },
                "required": ["linkedin_page_id"]
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
            result = canva_get_brand_template_dataset()
        elif name == "canva_create_autofill_job":
            # Automatically handle image uploads and include in autofill datagst
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
                image_fields=image_fields
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
            
        elif name == "linkedin_create_image_post":
            result = create_image_post(
                image_url=arguments["image_url"],
                text=arguments.get("text", "")
            )
        elif name == "linkedin_create_text_post":
            result = create_text_post(
                text=arguments["text"]
            )
        elif name == "linkedin_get_page_info":
            result = get_page_info()
            
        elif name == "trendbolt_pipeline":
            # Run complete pipeline using the pipeline module
            result = await run_once(
                subreddits=arguments.get("subreddits", ["technology"]),
                min_score=arguments.get("min_score", 200),
                template_id=arguments.get("template_id", "trendbolt_template_default")
            )
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
        ),
        Prompt(
            name="canva_workflow_guide",
            description="Guide for using Canva tools in TrendBolt workflow",
            arguments=[
                PromptArgument(
                    name="content_type",
                    description="Type of content to create (social media post, story, etc.)",
                    required=False
                ),
                PromptArgument(
                    name="brand_style",
                    description="Brand style preferences",
                    required=False
                )
            ]
        ),
        Prompt(
            name="canva_template_selection",
            description="Help select the best Canva template for content",
            arguments=[
                PromptArgument(
                    name="content_text",
                    description="The text content to be designed",
                    required=True
                ),
                PromptArgument(
                    name="platform",
                    description="Target platform (LinkedIn, Instagram, etc.)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="canva_autofill_data_prep",
            description="Prepare autofill data for Canva brand templates",
            arguments=[
                PromptArgument(
                    name="content_title",
                    description="Main title/headline for the design",
                    required=True
                ),
                PromptArgument(
                    name="content_description",
                    description="Description or body text",
                    required=False
                ),
                PromptArgument(
                    name="image_urls",
                    description="Comma-separated list of image URLs to include",
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
        
    elif name == "canva_workflow_guide":
        content_type = arguments.get("content_type", "social media post")
        brand_style = arguments.get("brand_style", "professional")
        
        return [
            PromptMessage(
                role="user",
                content=PromptMessage.TextContent(
                    type="text",
                    text=f"""Canva Workflow Guide for {content_type.title()}

Here's the complete workflow for creating designs with Canva in TrendBolt:

## Step 1: List Available Templates
Use `canva_list_brand_templates` to see your available brand templates:
- Query: Search for specific template types (e.g., "social media", "post", "story")
- Ownership: "owned" for your templates, "shared" for team templates
- Sort by: "relevance", "modified_descending", "title_ascending"

## Step 2: Get Template Dataset
Use `canva_get_brand_template_dataset` with a template ID to see what fields are available:
- This shows you exactly what data fields the template expects
- Look for fields like "title", "subtitle", "description", "image", etc.

## Step 3: Prepare Autofill Data
Use `canva_create_autofill_job` with your content data:
- Text fields: Direct text values
- Image URLs: Automatically uploaded to Canva and converted to asset IDs
- The system handles image uploads automatically

## Step 4: Check Job Status
Use `canva_get_autofill_job` to monitor progress:
- Check status: "pending", "processing", "success", "failed"
- Get the final design URL when complete

## Best Practices for {brand_style} Style:
- Keep headlines under 60 characters
- Use compelling, action-oriented language
- Ensure images are high-quality and relevant
- Match your brand colors and fonts

## Example Workflow:
1. List templates: `canva_list_brand_templates(query="social media")`
2. Get dataset: `canva_get_brand_template_dataset(brand_template_id="template_id")`
3. Create design: `canva_create_autofill_job(data={{"title": "Your Title", "description": "Your text"}})`
4. Check status: `canva_get_autofill_job(job_id="job_id")`

Ready to create your {content_type}? Let's start with listing your available templates!"""
                )
            )
        ]
        
    elif name == "canva_template_selection":
        content_text = arguments["content_text"]
        platform = arguments.get("platform", "LinkedIn")
        
        return [
            PromptMessage(
                role="user",
                content=PromptMessage.TextContent(
                    type="text",
                    text=f"""Template Selection Guide for {platform}

Content to design: "{content_text}"

## Template Selection Strategy:

### For {platform} Posts:
- **Square formats** (1080x1080) work best for most platforms
- **Vertical formats** (1080x1350) for stories and mobile-first content
- **Horizontal formats** (1200x630) for LinkedIn articles and headers

### Content Analysis:
Based on your text: "{content_text}"

**Recommended template types:**
- **Text-heavy content**: Look for templates with large text areas
- **Quote/inspirational**: Use quote-style templates with emphasis on typography
- **Informational**: Choose templates with clear hierarchy and bullet points
- **Visual content**: Select templates with prominent image areas

### Search Queries to Try:
1. `canva_list_brand_templates(query="social media {platform.lower()}")`
2. `canva_list_brand_templates(query="post template")`
3. `canva_list_brand_templates(query="quote design")`
4. `canva_list_brand_templates(query="infographic")`

### Template Evaluation Criteria:
- **Text capacity**: Does it have enough space for your content?
- **Visual hierarchy**: Clear headline, subtext, and body text areas
- **Brand alignment**: Matches your brand colors and style
- **Platform optimization**: Right dimensions for {platform}

### Next Steps:
1. Run `canva_list_brand_templates` with relevant queries
2. Review template previews and descriptions
3. Select 2-3 promising templates
4. Use `canva_get_brand_template_dataset` to see field requirements
5. Choose the best match for your content

Would you like me to help you search for templates now?"""
                )
            )
        ]
        
    elif name == "canva_autofill_data_prep":
        content_title = arguments["content_title"]
        content_description = arguments.get("content_description", "")
        image_urls = arguments.get("image_urls", "")
        
        return [
            PromptMessage(
                role="user",
                content=PromptMessage.TextContent(
                    type="text",
                    text=f"""Autofill Data Preparation

## Your Content:
**Title**: {content_title}
**Description**: {content_description}
**Images**: {image_urls if image_urls else "None provided"}

## Autofill Data Structure:

### Standard Fields (most templates use these):
```json
{{
    "title": "{content_title}",
    "headline": "{content_title}",
    "subtitle": "{content_description[:100]}{'...' if len(content_description) > 100 else ''}",
    "description": "{content_description}",
    "text": "{content_description}"
}}
```

### Image Fields (if images provided):
{f'''```json
{{
    "image": "{image_urls.split(',')[0].strip()}",
    "background_image": "{image_urls.split(',')[0].strip()}",
    "hero_image": "{image_urls.split(',')[0].strip()}"
}}
```''' if image_urls else "No images provided - using text-only fields"}

### Advanced Fields (for specific templates):
- **CTA fields**: "button_text", "call_to_action", "cta"
- **Brand fields**: "brand_name", "company_name", "logo"
- **Social fields**: "hashtags", "social_handle", "website"

## Template-Specific Preparation:

### Before creating autofill job:
1. **Get template dataset**: `canva_get_brand_template_dataset(brand_template_id="your_template_id")`
2. **Review required fields**: Check what fields the template expects
3. **Map your content**: Match your content to template field names
4. **Handle images**: Image URLs are automatically uploaded and converted to asset IDs

### Example Autofill Job:
```json
{{
    "data": {{
        "title": "{content_title}",
        "description": "{content_description}",
        "image": "{image_urls.split(',')[0].strip() if image_urls else ''}"
    }}
}}
```

### Pro Tips:
- **Keep titles under 60 characters** for best visual impact
- **Descriptions under 200 characters** for readability
- **Use high-quality images** (minimum 1080px width)
- **Test with different templates** to find the best fit

Ready to create your autofill job? Let me know which template you'd like to use!"""
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
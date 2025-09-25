"""
TrendBolt MCP Server - Single Tool Interface
A Model Context Protocol server for social media automation.

This version exposes only ONE tool that handles everything through natural language.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
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
from .orchestrator import TrendBoltLangChainAgent


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("trendbolt")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for external users."""
    return [
        Tool(
            name="trendbolt",
            description="Execute TrendBolt social media automation using natural language. Describe what you want to accomplish and the system will handle everything automatically.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language description of what you want to accomplish. Examples: 'Find trending AI topics and create a LinkedIn post', 'Create viral content about technology news', 'Generate professional posts from programming subreddits'"
                    },
                    "subreddits": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: specific subreddits to focus on (e.g., ['technology', 'ai', 'programming'])"
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["hot", "top", "new"],
                        "description": "Optional: Reddit search strategy (default: 'hot')"
                    },
                    "min_score": {
                        "type": "integer",
                        "description": "Optional: minimum Reddit post score threshold (default: 100)"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for external users."""
    try:
        agent = TrendBoltLangChainAgent()
        
        if name == "trendbolt":
            # Build context from query and optional parameters
            query = arguments["query"]
            subreddits = arguments.get("subreddits")
            strategy = arguments.get("strategy", "hot")
            min_score = arguments.get("min_score", 100)
            
            # Enhance query with parameters if provided
            enhanced_query = query
            if subreddits:
                enhanced_query += f" Focus on these subreddits: {', '.join(subreddits)}"
            if strategy != "hot":
                enhanced_query += f" Use '{strategy}' strategy for Reddit search"
            if min_score != 100:
                enhanced_query += f" Only consider posts with score {min_score} or higher"
            
            # Execute with the agent
            result = await agent.execute_simple_pipeline(
                query=enhanced_query,
                subreddits=subreddits
            )
            
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        error_result = {
            "error": str(e),
            "tool": name,
            "success": False
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="trendbolt://capabilities",
            name="TrendBolt Capabilities",
            description="Available automation capabilities and integrations",
            mimeType="application/json"
        ),
        Resource(
            uri="trendbolt://examples",
            name="Usage Examples",
            description="Example queries and use cases",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content."""
    if uri == "trendbolt://capabilities":
        return json.dumps({
            "integrations": {
                "reddit": "Trending content discovery from any subreddit",
                "azure_openai": "AI-powered content generation",
                "canva": "Automatic design creation and customization",
                "linkedin": "Social media publishing and management"
            },
            "capabilities": [
                "Discover trending topics from Reddit",
                "Generate engaging social media content",
                "Create professional visual designs",
                "Publish to LinkedIn with images",
                "Handle errors and retry automatically",
                "Natural language workflow control"
            ],
            "supported_platforms": ["LinkedIn"],
            "content_types": ["Posts with images", "Text-only posts"],
            "design_features": ["Brand templates", "Automatic layout", "Custom styling"]
        }, indent=2)
    
    elif uri == "trendbolt://examples":
        return json.dumps({
            "example_queries": [
                "Find trending AI topics and create a professional LinkedIn post",
                "Create viral content about the latest technology news",
                "Generate engaging posts from programming subreddits",
                "Make professional content about machine learning breakthroughs",
                "Create LinkedIn posts about startup news with visual designs",
                "Find hot topics in artificial intelligence and publish to LinkedIn"
            ],
            "parameter_examples": {
                "subreddits": ["technology", "ai", "programming", "MachineLearning", "startups"],
                "strategies": ["hot", "top", "new"],
                "min_score": "100-1000 (higher = more popular posts)"
            },
            "workflow_steps": [
                "1. Discover trending topics from specified subreddits",
                "2. Generate engaging content using AI",
                "3. Create professional visual designs",
                "4. Publish to LinkedIn with images",
                "5. Return detailed results and status"
            ]
        }, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available prompts."""
    return [
        Prompt(
            name="social_media_automation",
            description="Generate social media content from trending topics",
            arguments=[
                PromptArgument(
                    name="topic",
                    description="The trending topic to create content about",
                    required=True
                ),
                PromptArgument(
                    name="platform",
                    description="Target social media platform (e.g., LinkedIn)",
                    required=False
                ),
                PromptArgument(
                    name="tone",
                    description="Content tone (e.g., professional, casual, engaging)",
                    required=False
                )
            ]
        )
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str]) -> List[PromptMessage]:
    """Get prompt content."""
    if name == "social_media_automation":
        topic = arguments.get("topic", "technology trends")
        platform = arguments.get("platform", "LinkedIn")
        tone = arguments.get("tone", "professional")
        
        return [
            PromptMessage(
                role="user",
                content=PromptMessageTextContent(
                    type="text",
                    text=f"""Create engaging social media content about: {topic}

Platform: {platform}
Tone: {tone}

Use the trendbolt tool with this query:
"Find trending {topic} topics and create a {tone} {platform} post with visual design"

The system will automatically:
1. Discover trending content about {topic}
2. Generate {tone} copy for {platform}
3. Create professional visual designs
4. Publish to {platform} with images
5. Return detailed results and status

Example usage:
```json
{{
  "query": "Find trending {topic} topics and create a {tone} {platform} post with visual design",
  "subreddits": ["technology", "ai"],
  "strategy": "hot",
  "min_score": 200
}}
```"""
                )
            )
        ]
    
    else:
        raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Main server entry point."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

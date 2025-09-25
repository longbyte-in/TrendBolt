# MCP Server Tools

The MCP (Model Context Protocol) server provides a standardized interface for all TrendBolt tools, resources, and prompts, enabling integration with MCP-compatible clients like Claude Desktop.

## 📋 Overview

**File**: `trendbolt_mcp/server.py`  
**Type**: MCP Protocol Server  
**Port**: 8765 (default)  
**Protocol**: JSON-RPC over stdio/HTTP  

## 🛠️ Available Tools

### **Reddit Tools**

#### **`reddit_get_trending`**
Fetch trending posts from Reddit subreddits.

```json
{
  "name": "reddit_get_trending",
  "arguments": {
    "subreddits": ["technology", "programming"],
    "strategy": "hot",
    "limit": 10,
    "min_score": 100,
    "time_filter": "day"
  }
}
```

**Parameters:**
- `subreddits`: Array of subreddit names
- `strategy`: "hot", "top", or "new"
- `limit`: Maximum posts to fetch (default: 10)
- `min_score`: Minimum score threshold (default: 100)
- `time_filter`: For "top" strategy - "hour", "day", "week", "month", "year", "all"

### **Content Generation Tools**

#### **`llm_generate_content`**
Generate social media content using LLM.

```json
{
  "name": "llm_generate_content",
  "arguments": {
    "topic": {
      "title": "AI Breakthrough Announced",
      "url": "https://reddit.com/...",
      "subreddit": "technology",
      "score": 1250
    },
    "brand": {
      "cta": "Follow TrendBolt",
      "voice": "engaging and informative"
    }
  }
}
```

**Alternative with Reddit Post ID:**
```json
{
  "name": "llm_generate_content",
  "arguments": {
    "reddit_post_id": "t3_1ndjq1c",
    "brand": {
      "cta": "Learn More",
      "voice": "professional"
    }
  }
}
```

### **Canva Tools**

#### **`canva_list_brand_templates`**
List available Canva brand templates.

```json
{
  "name": "canva_list_brand_templates",
  "arguments": {
    "query": "social media",
    "ownership": "owned",
    "sort_by": "relevance"
  }
}
```

#### **`canva_create_autofill_job`**
Create an autofill job for a brand template.

```json
{
  "name": "canva_create_autofill_job",
  "arguments": {
    "data": {
      "title": "Your Title",
      "description": "Your content",
      "image": "https://example.com/image.jpg"
    }
  }
}
```

#### **`canva_get_autofill_job`**
Get autofill job status and result.

```json
{
  "name": "canva_get_autofill_job",
  "arguments": {
    "job_id": "job_12345"
  }
}
```

### **LinkedIn Tools**

#### **`linkedin_create_image_post`**
Create an image post on LinkedIn.

```json
{
  "name": "linkedin_create_image_post",
  "arguments": {
    "image_url": "https://canva.com/design/thumbnail.jpg",
    "text": "Check out this amazing content!"
  }
}
```

#### **`linkedin_create_text_post`**
Create a text-only post on LinkedIn.

```json
{
  "name": "linkedin_create_text_post",
  "arguments": {
    "text": "Your LinkedIn post content here"
  }
}
```

#### **`linkedin_get_page_info`**
Get LinkedIn page information.

```json
{
  "name": "linkedin_get_page_info",
  "arguments": {}
}
```

### **Pipeline Tools**

#### **`trendbolt_pipeline`**
Run the complete basic TrendBolt pipeline.

```json
{
  "name": "trendbolt_pipeline",
  "arguments": {
    "subreddits": ["technology"],
    "template_id": "your_canva_template_id",
    "min_score": 200
  }
}
```

#### **`langchain_workflow`**
Execute LangChain orchestrated workflow.

```json
{
  "name": "langchain_workflow",
  "arguments": {
    "subreddits": ["technology", "programming"],
    "strategy": "hot",
    "min_score": 100
  }
}
```

#### **`langchain_agent_query`**
Execute natural language workflow query.

```json
{
  "name": "langchain_agent_query",
  "arguments": {
    "query": "Find trending AI topics and create a professional LinkedIn post",
    "subreddits": ["artificial", "MachineLearning"]
  }
}
```

## 📚 Resources

### **`trendbolt://trending-topics`**
Current trending topics from Reddit.

```json
{
  "trending_topics": [
    {
      "id": "t3_abc123",
      "title": "AI Breakthrough",
      "url": "https://reddit.com/...",
      "score": 1250,
      "subreddit": "technology"
    }
  ]
}
```

### **`trendbolt://content-templates`**
Pre-built content generation templates.

```json
{
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
```

### **`trendbolt://design-assets`**
Generated design assets and exports.

## 🎯 Prompts

### **`generate_viral_content`**
Generate viral social media content from trending topics.

**Arguments:**
- `topic_title`: Title of the trending topic (required)
- `topic_url`: URL of the trending topic (required)
- `brand_voice`: Brand voice and tone (optional)

### **`create_design_brief`**
Create design briefs for Canva.

**Arguments:**
- `content_caption`: Social media caption content (required)
- `target_audience`: Target audience for the design (optional)

### **`canva_workflow_guide`**
Guide for using Canva tools in TrendBolt workflow.

**Arguments:**
- `content_type`: Type of content to create (optional)
- `brand_style`: Brand style preferences (optional)

## 🚀 Server Setup

### **Start MCP Server**

```bash
# Start server on default port
python -m trendbolt_mcp.server

# Or using CLI
trendbolt mcp --host 127.0.0.1 --port 8765
```

### **MCP Client Configuration**

#### **Claude Desktop Configuration**
```json
{
  "mcpServers": {
    "trendbolt": {
      "command": "python",
      "args": ["-m", "trendbolt_mcp.server"],
      "env": {
        "REDDIT_CLIENT_ID": "your_reddit_client_id",
        "AZURE_OPENAI_API_KEY": "your_azure_openai_key"
      }
    }
  }
}
```

#### **HTTP Client Configuration**
```json
{
  "mcpServers": {
    "trendbolt": {
      "url": "http://127.0.0.1:8765",
      "transport": "http"
    }
  }
}
```

## 🔧 Tool Implementation

### **Adding New Tools**

1. **Define Tool Schema**
```python
Tool(
    name="new_tool_name",
    description="Tool description",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
)
```

2. **Implement Tool Handler**
```python
@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]):
    if name == "new_tool_name":
        result = await your_tool_function(arguments["param1"])
        return [TextContent(type="text", text=json.dumps(result))]
```

### **Error Handling**

```python
try:
    result = await tool_function(arguments)
except Exception as e:
    logger.error(f"Tool {name} failed: {e}")
    return [TextContent(type="text", text=json.dumps({
        "error": str(e),
        "tool": name
    }))]
```

## 📊 Response Formats

### **Success Response**
```json
{
  "success": true,
  "data": {
    // Tool-specific response data
  },
  "metadata": {
    "execution_time": 1.23,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### **Error Response**
```json
{
  "error": "Error description",
  "tool": "tool_name",
  "details": {
    // Additional error details
  }
}
```

## 🔍 Monitoring and Debugging

### **Logging Configuration**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### **Tool Execution Metrics**
- Execution time tracking
- Error rate monitoring
- Usage statistics
- Performance profiling

## 🎯 Integration Examples

### **Basic Content Creation**
```python
# 1. Get trending topics
topics = await call_tool("reddit_get_trending", {
    "subreddits": ["technology"],
    "limit": 5
})

# 2. Generate content
content = await call_tool("llm_generate_content", {
    "topic": topics[0],
    "brand": {"voice": "professional"}
})

# 3. Create design
design_job = await call_tool("canva_create_autofill_job", {
    "data": content
})

# 4. Check design status
design = await call_tool("canva_get_autofill_job", {
    "job_id": design_job["job"]["id"]
})

# 5. Publish to LinkedIn
post = await call_tool("linkedin_create_image_post", {
    "image_url": design["thumbnail"]["url"],
    "text": content["description"]
})
```

### **Automated Pipeline**
```python
# Single tool call for complete pipeline
result = await call_tool("trendbolt_pipeline", {
    "subreddits": ["technology", "programming"],
    "min_score": 200
})
```

### **AI-Orchestrated Workflow**
```python
# Natural language control
result = await call_tool("langchain_agent_query", {
    "query": "Create professional content about AI trends"
})
```

## 🔗 Related Documentation

- [Basic Pipeline](./basic-pipeline.md) - Simple workflow implementation
- [LangChain Workflow](./langchain-workflow.md) - AI orchestration
- [MCP Configuration](../configuration/mcp-config.md) - Server configuration
- [API Reference](../development/api-reference.md) - Complete API documentation

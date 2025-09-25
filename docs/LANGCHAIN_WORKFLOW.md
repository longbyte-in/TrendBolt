# TrendBolt LangChain Workflow Integration

This document describes the comprehensive LangChain workflow system integrated into TrendBolt for intelligent social media automation.

## Overview

The LangChain integration provides:

- **Intelligent Workflow Orchestration**: AI-powered decision making throughout the pipeline
- **Natural Language Control**: Execute workflows using natural language descriptions
- **Dynamic Error Recovery**: Intelligent error handling and retry logic
- **State Management**: Persistent state tracking across workflow steps
- **Flexible Tool Integration**: Seamless integration with Reddit, Canva, and LinkedIn APIs

## Architecture

### Core Components

1. **TrendBoltLangChainAgent** (`trendbolt_mcp/orchestrator/langchain_agent.py`)
   - Main orchestrator using LangGraph for workflow management
   - Integrates with existing TrendBolt tools
   - Provides both structured and natural language interfaces

2. **Workflow Configuration** (`trendbolt_mcp/orchestrator/workflow_config.py`)
   - Predefined workflow templates for different content strategies
   - Content style configurations
   - Customizable workflow parameters

3. **MCP Server Integration** (`trendbolt_mcp/server.py`)
   - New MCP tools: `langchain_workflow` and `langchain_agent_query`
   - Seamless integration with existing TrendBolt MCP tools

## Usage

### 1. Basic Workflow Execution

Execute a complete TrendBolt workflow with intelligent orchestration:

```python
from trendbolt_mcp.orchestrator import TrendBoltLangChainAgent

# Initialize the agent
agent = TrendBoltLangChainAgent()

# Execute workflow
result = await agent.execute_workflow(
    subreddits=["technology", "programming"],
    strategy="hot",
    min_score=150
)

if result["success"]:
    print(f"✅ Workflow completed!")
    print(f"Topic: {result['topic']['title']}")
    print(f"LinkedIn Post: {result['linkedin_post']['post_id']}")
```

### 2. Natural Language Queries

Use natural language to describe what you want to accomplish:

```python
# Natural language workflow execution
result = await agent.execute_simple_pipeline(
    query="Find trending AI topics and create a professional LinkedIn post",
    subreddits=["artificial", "MachineLearning"]
)

print(result["response"])
```

### 3. MCP Tool Usage

Use the new MCP tools in your MCP client:

```json
// Execute structured workflow
{
  "tool": "langchain_workflow",
  "arguments": {
    "subreddits": ["technology", "programming"],
    "strategy": "hot",
    "min_score": 100
  }
}

// Execute natural language query
{
  "tool": "langchain_agent_query", 
  "arguments": {
    "query": "Find popular startup news and create engaging content"
  }
}
```

### 4. Predefined Workflow Configurations

Use predefined configurations for common scenarios:

```python
from trendbolt_mcp.orchestrator.workflow_config import get_workflow_config

# Get predefined configuration
config = get_workflow_config("tech_news")

# Execute with configuration
result = await agent.execute_workflow(
    subreddits=config.subreddits,
    strategy=config.strategy,
    min_score=config.min_score
)
```

Available configurations:
- `tech_news`: Technology news and updates
- `ai_trends`: AI and machine learning topics
- `startup_news`: Startup and business content
- `dev_tools`: Developer tools and programming resources
- `quick_viral`: Fast viral content creation

## Workflow Steps

The LangChain workflow orchestrates these steps intelligently:

1. **Content Discovery** (`discover`)
   - Fetch trending topics from Reddit
   - Apply intelligent filtering and ranking
   - Select optimal topics for content creation

2. **Content Generation** (`generate`)
   - Generate engaging social media content using LLM
   - Apply brand voice and style guidelines
   - Create compelling headlines and descriptions

3. **Design Creation** (`design`)
   - Create visual designs using Canva
   - Upload images and apply brand templates
   - Generate optimized social media graphics

4. **Content Publishing** (`publish`)
   - Publish to LinkedIn with appropriate formatting
   - Handle both text and image posts
   - Provide post tracking and analytics

## State Management

The workflow maintains comprehensive state throughout execution:

```python
class WorkflowState(TypedDict):
    messages: List[Any]              # Conversation history
    current_step: str                # Current workflow step
    reddit_topics: List[Dict]        # Discovered topics
    selected_topic: Optional[Dict]   # Selected topic for content
    generated_content: Optional[Dict] # Generated content
    canva_design: Optional[Dict]     # Created design assets
    linkedin_post: Optional[Dict]    # Published post details
    error_log: List[str]            # Error tracking
    metadata: Dict[str, Any]        # Execution metadata
```

## Error Handling

The LangChain workflow provides robust error handling:

- **Graceful Degradation**: Continue workflow even if some steps fail
- **Intelligent Retry**: Automatic retry with backoff for transient failures
- **Error Recovery**: Alternative paths when primary methods fail
- **Detailed Logging**: Comprehensive error tracking and reporting

## Configuration

### Environment Variables

The workflow uses existing TrendBolt environment variables:

```bash
# LLM Configuration
LLM_PROVIDER=openai  # or azure_openai
OPENAI_API_KEY=your_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_DEPLOYMENT=your_deployment

# Service API Keys
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
CANVA_ACCESS_TOKEN=your_canva_token
CANVA_BRAND_TEMPLATE_ID=your_template_id
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
LINKEDIN_PAGE_ID=your_page_id
```

### Content Styles

Customize content generation with different styles:

```python
from trendbolt_mcp.orchestrator.workflow_config import get_content_style

# Available styles: professional, technical, business, engaging, viral
style = get_content_style("professional")
print(style["voice"])  # "professional and authoritative"
print(style["cta"])    # "Follow for professional insights"
```

## Examples

### Example 1: Technology News Workflow

```python
import asyncio
from trendbolt_mcp.orchestrator import TrendBoltLangChainAgent

async def tech_news_workflow():
    agent = TrendBoltLangChainAgent()
    
    result = await agent.execute_workflow(
        subreddits=["technology", "programming", "artificial"],
        strategy="hot",
        min_score=200
    )
    
    if result["success"]:
        print(f"🎯 Topic: {result['topic']['title']}")
        print(f"📱 LinkedIn: {result['linkedin_post']['permalink_url']}")
    
    return result

# Run the workflow
asyncio.run(tech_news_workflow())
```

### Example 2: Natural Language Control

```python
async def natural_language_example():
    agent = TrendBoltLangChainAgent()
    
    queries = [
        "Find trending AI topics and create a professional post",
        "Look for startup news and make viral content",
        "Search programming discussions and create technical content"
    ]
    
    for query in queries:
        result = await agent.execute_simple_pipeline(query=query)
        print(f"Query: {query}")
        print(f"Response: {result['response'][:100]}...")
        print()

asyncio.run(natural_language_example())
```

### Example 3: Custom Workflow Configuration

```python
from trendbolt_mcp.orchestrator.workflow_config import create_custom_config

# Create custom configuration
custom_config = create_custom_config(
    name="DevOps Focus",
    subreddits=["devops", "kubernetes", "docker", "aws"],
    strategy="top",
    min_score=75,
    content_style="technical"
)

# Use custom configuration
result = await agent.execute_workflow(
    subreddits=custom_config.subreddits,
    strategy=custom_config.strategy,
    min_score=custom_config.min_score
)
```

## Testing

Run the test suite to verify the LangChain integration:

```bash
# Run all LangChain workflow tests
python -m pytest tests/test_langchain_workflow.py -v

# Run specific test categories
python -m pytest tests/test_langchain_workflow.py::TestWorkflowConfig -v
python -m pytest tests/test_langchain_workflow.py::TestTrendBoltLangChainAgent -v
```

## Monitoring and Debugging

### Workflow Execution Monitoring

```python
import time

start_time = time.time()
result = await agent.execute_workflow(subreddits=["technology"])
execution_time = time.time() - start_time

print(f"Execution time: {execution_time:.2f}s")
print(f"Success: {result['success']}")
print(f"Steps completed: {len([x for x in [result.get('topic'), result.get('content'), result.get('design'), result.get('linkedin_post')] if x])}/4")
```

### Error Analysis

```python
if not result["success"]:
    print("Errors encountered:")
    for error in result.get("errors", []):
        print(f"  - {error}")
        
    print(f"Final status: {result['status']}")
    print(f"Metadata: {result['metadata']}")
```

## Performance Considerations

- **Parallel Processing**: The workflow uses async/await for optimal performance
- **Intelligent Caching**: LangGraph provides built-in state caching
- **Resource Management**: Automatic cleanup of HTTP connections and resources
- **Rate Limiting**: Built-in respect for API rate limits

## Best Practices

1. **API Key Management**: Use environment variables for all API keys
2. **Error Handling**: Always check workflow results and handle errors gracefully  
3. **Content Quality**: Use appropriate min_score thresholds for quality control
4. **Brand Consistency**: Configure content styles to match your brand voice
5. **Monitoring**: Track workflow execution times and success rates
6. **Testing**: Use the test suite to verify integrations before production use

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required environment variables are set
2. **Rate Limiting**: Implement appropriate delays between API calls
3. **Content Quality**: Adjust min_score thresholds if no suitable content is found
4. **Network Issues**: The workflow includes retry logic for transient failures

### Debug Mode

Enable debug logging for detailed workflow execution information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run workflow with debug logging
result = await agent.execute_workflow(subreddits=["technology"])
```

## Integration with Existing TrendBolt

The LangChain workflow is fully compatible with existing TrendBolt functionality:

- **MCP Server**: New tools integrate seamlessly with existing MCP tools
- **Configuration**: Uses existing TrendBolt configuration system
- **APIs**: Leverages existing Reddit, Canva, and LinkedIn integrations
- **Pipeline**: Can be used alongside or instead of the original pipeline

## Future Enhancements

Planned improvements for the LangChain workflow system:

- **Multi-Platform Publishing**: Extend to Twitter, Instagram, and other platforms
- **Advanced Analytics**: Detailed performance tracking and optimization
- **Content Templates**: More sophisticated content generation templates
- **Workflow Scheduling**: Automated workflow execution on schedules
- **A/B Testing**: Built-in content variation testing capabilities

## Contributing

To contribute to the LangChain workflow system:

1. Follow the existing code structure and patterns
2. Add comprehensive tests for new functionality
3. Update documentation for any new features
4. Ensure backward compatibility with existing workflows

## Support

For questions or issues with the LangChain workflow system:

1. Check the test suite for usage examples
2. Review the error logs for debugging information
3. Consult the existing TrendBolt documentation for API details
4. Create detailed issue reports with reproduction steps

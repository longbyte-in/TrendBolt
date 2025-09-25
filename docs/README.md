# TrendBolt Documentation

This directory contains comprehensive documentation for all TrendBolt workflow implementations and integrations.

## 📚 Documentation Structure

### **Core Workflows**
- **[LangChain Workflow](./workflows/langchain-workflow.md)** - AI-powered workflow orchestration (Primary)
- **[MCP Server Tools](./workflows/mcp-tools.md)** - Model Context Protocol server tools

### **Integrations**
- **[Reddit Integration](./integrations/reddit.md)** - Reddit API integration and trending content discovery
- **[LinkedIn Integration](./integrations/linkedin.md)** - LinkedIn publishing and page management
- **[Canva Integration](./integrations/canva.md)** - Canva design creation and automation
- **[Azure OpenAI Integration](./integrations/azure-openai.md)** - LLM content generation

### **Configuration**
- **[Environment Setup](./configuration/environment-setup.md)** - Environment variables and API keys
- **[Workflow Configuration](./configuration/workflow-config.md)** - Predefined workflow templates
- **[MCP Configuration](./configuration/mcp-config.md)** - MCP server configuration

### **Development**
- **[API Reference](./development/api-reference.md)** - Complete API documentation
- **[Testing Guide](./development/testing.md)** - Testing strategies and examples
- **[Deployment Guide](./development/deployment.md)** - Production deployment instructions

### **Examples**
- **[Basic Usage](./examples/basic-usage.md)** - Simple workflow examples
- **[Advanced Workflows](./examples/advanced-workflows.md)** - Complex automation scenarios
- **[Custom Configurations](./examples/custom-configurations.md)** - Custom workflow setups

## 🚀 Quick Start

1. **Setup**: Follow [Environment Setup](./configuration/environment-setup.md)
2. **LangChain Workflow**: Use [LangChain Workflow](./workflows/langchain-workflow.md) for AI-powered automation
3. **MCP Integration**: Configure [MCP Server](./workflows/mcp-tools.md) for Claude Desktop
4. **Advanced Features**: Explore [LangChain Workflow](./workflows/langchain-workflow.md) for natural language control

## 🔧 Workflow Types

### **1. LangChain Workflow** (`trendbolt_mcp/orchestrator/langchain_agent.py`)
- AI-powered orchestration with intelligent decision making
- Natural language control and error recovery
- Enhanced Canva polling with URL validation
- State management and retry logic
- Azure OpenAI integration

### **2. MCP Server Tools** (`trendbolt_mcp/server.py`)
- Model Context Protocol integration
- Tool-based interface
- Resource and prompt management
- Client integration ready

## 📋 Available Tools

| Tool | Description | Workflow |
|------|-------------|----------|
| `reddit_get_trending` | Fetch trending Reddit posts | All |
| `llm_generate_content` | Generate social media content | All |
| `canva_create_autofill_job` | Create Canva design job | All |
| `canva_get_autofill_job` | Get Canva job status | All |
| `linkedin_create_image_post` | Publish image to LinkedIn | All |
| `linkedin_create_text_post` | Publish text to LinkedIn | All |
| `trendbolt_pipeline` | Run complete basic pipeline | Basic |
| `langchain_workflow` | Run LangChain orchestrated workflow | LangChain |
| `langchain_agent_query` | Natural language workflow control | LangChain |

## 🎯 Use Cases

### **Content Marketing Teams**
- Automated content discovery from Reddit
- AI-generated social media posts
- Brand-consistent design creation
- Multi-platform publishing

### **Social Media Managers**
- Trending topic monitoring
- Content calendar automation
- Visual content generation
- Performance tracking

### **Marketing Agencies**
- Client content automation
- Scalable content production
- Brand template management
- Multi-account publishing

## 🔗 Related Documentation

- **[Main README](../README.md)** - Project overview and quick start
- **[LinkedIn Setup](../LINKEDIN_SETUP.md)** - LinkedIn API configuration
- **[LinkedIn Integration](../LINKEDIN_INTEGRATION.md)** - Detailed LinkedIn integration
- **[LangChain Workflow](../LANGCHAIN_WORKFLOW.md)** - LangChain implementation details

## 📞 Support

For questions about specific workflows or integrations, refer to the relevant documentation files or create an issue in the project repository.

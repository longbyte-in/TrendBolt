# TrendBolt MCP Server

A Model Context Protocol (MCP) server for automated social media content creation. TrendBolt discovers trending topics on Reddit, generates engaging content using LLM, creates designs with Canva, and publishes to LinkedIn.

## 📚 Documentation

**Complete documentation is available in the [`docs/`](./docs/) folder:**

- **[Workflows](./docs/workflows/)** - All workflow implementations (Basic, LangChain, MCP)
- **[Integrations](./docs/integrations/)** - API integrations (Reddit, LinkedIn, Canva, Azure OpenAI)
- **[Configuration](./docs/configuration/)** - Environment setup and configuration guides
- **[Development](./docs/development/)** - API reference, testing, and deployment guides
- **[Examples](./docs/examples/)** - Usage examples and custom configurations

## 🚀 Workflow Implementation

TrendBolt now features a **single-tool AI-powered interface** for maximum simplicity and power:

### **Single Tool: `trendbolt`**
- **Natural language control** - Describe what you want in plain English
- **AI-powered orchestration** with intelligent decision making
- **Complete automation** - Reddit → LLM → Canva → LinkedIn
- **Flexible parameters** - Optional subreddits, strategy, and scoring
- **Error recovery** and retry logic built-in

## 🛠️ Available Tools

### **Resources**
- **`trendbolt://trending-topics`** - Current trending topics from Reddit
- **`trendbolt://content-templates`** - Pre-built content generation templates
- **`trendbolt://design-assets`** - Generated design assets and exports

### **Prompts**
- **`generate_viral_content`** - Generate viral social media content from trending topics
- **`create_design_brief`** - Create design briefs for Canva

## 📋 Prerequisites

- Python 3.11+
- Reddit API credentials
- Azure OpenAI or OpenAI API key
- Canva API credentials (optional)
- Facebook Page Access Token (optional)

## 🛠️ Installation

```bash
# Clone repository
git clone <repository-url>
cd TrendBolt

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .[dev]
```

## ⚙️ Quick Setup

1. **Environment Setup**: Follow the [Environment Setup Guide](./docs/configuration/environment-setup.md)
2. **LangChain Workflow**: Use the [LangChain Workflow](./docs/workflows/langchain-workflow.md) for AI-powered automation
3. **MCP Integration**: Configure [MCP Server](./docs/workflows/mcp-tools.md) for Claude Desktop integration
4. **Configure Integrations**: Set up [Reddit](./docs/integrations/reddit.md), [LinkedIn](./docs/integrations/linkedin.md), [Canva](./docs/integrations/canva.md), and [Azure OpenAI](./docs/integrations/azure-openai.md)

### **Essential Environment Variables**
```env
# Required
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# For design creation
CANVA_ACCESS_TOKEN=your_canva_access_token
CANVA_BRAND_TEMPLATE_ID=your_brand_template_id

# For LinkedIn publishing
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_PAGE_ID=your_linkedin_page_id
```

**📖 Complete setup instructions:** [Environment Setup Guide](./docs/configuration/environment-setup.md)

## 🚀 Usage

### **Start MCP Server**

```bash
# Start MCP server
trendbolt mcp --host 127.0.0.1 --port 8765

# Or run directly
python -m trendbolt_mcp.server
```

### **Using with MCP Clients**

Connect to the server using any MCP-compatible client (Claude Desktop, etc.):

```json
{
  "mcpServers": {
    "trendbolt": {
      "command": "trendbolt",
      "args": ["mcp", "--host", "127.0.0.1", "--port", "8765"]
    }
  }
}
```

### **Single Tool Usage**

#### **Natural Language Control**
```json
{
  "name": "trendbolt",
  "arguments": {
    "query": "Find trending AI topics and create a professional LinkedIn post"
  }
}
```

#### **With Optional Parameters**
```json
{
  "name": "trendbolt", 
  "arguments": {
    "query": "Create viral content about technology news",
    "subreddits": ["technology", "ai", "programming"],
    "strategy": "hot",
    "min_score": 200
  }
}
```

### **Example Queries**
- "Find trending AI topics and create a LinkedIn post"
- "Create viral content about the latest technology news"
- "Generate professional posts from programming subreddits"
- "Make engaging content about machine learning breakthroughs"

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Reddit API    │───▶│   LLM Engine    │───▶│   Canva API     │
│                 │    │  (Azure OpenAI)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  MCP Server     │    │  Content Gen    │    │  Design Export  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Facebook API   │    │  Azure Storage  │    │  MCP Client     │
│                 │    │                 │    │  (Claude, etc.) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
trendbolt_mcp/
├── __init__.py
├── server.py              # Main MCP server
├── cli.py                 # Command line interface
├── config.py              # Configuration management
├── pipeline.py            # End-to-end pipeline
├── integrations/
│   └── canva_connect.py   # Canva OAuth integration
├── tools/
│   ├── reddit.py          # Reddit API integration
│   ├── llm.py             # LLM content generation
│   ├── canva.py           # Canva design creation
│   └── facebook.py        # Facebook publishing
└── storage/
    └── azure_blob.py      # Azure Blob Storage
```

## 🔧 Development

### **Run Tests**
```bash
pytest tests/
```

### **Code Quality**
```bash
# Format code
black trendbolt_mcp/

# Lint code
ruff trendbolt_mcp/

# Type checking
mypy trendbolt_mcp/
```

### **Add New Tools**

1. Create tool function in `tools/` directory
2. Add tool definition to `server.py` `list_tools()`
3. Add tool handler to `call_tool()`
4. Update documentation

## 📚 API Reference

### **Reddit Tool**
- **Input**: subreddits, strategy, limit, min_score, time_filter
- **Output**: Array of trending posts with metadata

### **LLM Tool**
- **Input**: topic object, brand configuration
- **Output**: Generated content with caption, hashtags, design brief

### **Canva Tool**
- **Input**: template_id, design_brief, export settings
- **Output**: Design creation result with asset URLs

### **Facebook Tool**
- **Input**: caption, image_url, page_id
- **Output**: Post creation result with post ID

## 🚨 Error Handling

The server provides comprehensive error handling:
- **Authentication errors**: Clear messages for missing credentials
- **API errors**: Detailed error information from external APIs
- **Validation errors**: Input validation with helpful messages
- **Network errors**: Retry logic and timeout handling

## 🔒 Security

- **Environment variables**: All credentials stored securely
- **Token management**: Automatic refresh and secure storage
- **Input validation**: All inputs validated before processing
- **Error sanitization**: Sensitive information not exposed in errors

## 📈 Monitoring

- **Structured logging**: JSON-formatted logs for easy parsing
- **Error tracking**: Comprehensive error logging and reporting
- **Performance metrics**: Tool execution time tracking
- **Health checks**: Server health monitoring endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

- **Documentation**: [Link to full documentation]
- **Issues**: [GitHub Issues URL]
- **Discussions**: [GitHub Discussions URL]
- **Email**: [Support email]

---

**TrendBolt** - Turn trending topics into scroll-stopping content, instantly! 🚀
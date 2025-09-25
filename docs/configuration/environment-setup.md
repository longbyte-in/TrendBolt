# Environment Setup

Complete guide for setting up TrendBolt environment variables, API keys, and configuration files.

## 📋 Required Environment Variables

### **Reddit API**
```env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=TrendBolt/1.0 by your_username
```

**Setup:**
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create a new application (script type)
3. Copy Client ID and Secret

### **Azure OpenAI (Recommended)**
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-06-01
```

**Setup:**
1. Create Azure OpenAI resource
2. Deploy a model (GPT-4 recommended)
3. Get endpoint and API key from Azure portal

### **Canva Connect API**
```env
CANVA_ACCESS_TOKEN=your_canva_access_token
CANVA_BRAND_TEMPLATE_ID=your_brand_template_id
```

**Setup:**
1. Create [Canva Developer Account](https://developers.canva.com/)
2. Create new app and get access token
3. Create brand template and get template ID

### **LinkedIn API**
```env
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_PAGE_ID=your_linkedin_page_id
```

**Setup:**
1. Create LinkedIn Developer Application
2. Get access token with required scopes
3. Get your LinkedIn page ID

## 🔧 Configuration Files

### **.env File**
Create a `.env` file in the project root:

```env
# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=TrendBolt/1.0 by your_username

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-06-01

# Canva
CANVA_ACCESS_TOKEN=your_canva_access_token
CANVA_BRAND_TEMPLATE_ID=your_brand_template_id

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_PAGE_ID=your_linkedin_page_id

# Optional: Default settings
SUBREDDITS=technology,programming,artificial
MIN_SCORE=100
CONTENT_STRATEGY=hot
```

### **MCP Configuration**
For MCP clients like Claude Desktop, create or update your configuration:

```json
{
  "mcpServers": {
    "trendbolt": {
      "command": "python",
      "args": ["-m", "trendbolt_mcp.server"],
      "env": {
        "REDDIT_CLIENT_ID": "your_reddit_client_id",
        "REDDIT_CLIENT_SECRET": "your_reddit_client_secret",
        "REDDIT_USER_AGENT": "TrendBolt/1.0 by your_username",
        "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "your_azure_openai_key",
        "AZURE_OPENAI_DEPLOYMENT": "gpt-4o",
        "CANVA_ACCESS_TOKEN": "your_canva_access_token",
        "CANVA_BRAND_TEMPLATE_ID": "your_brand_template_id",
        "LINKEDIN_ACCESS_TOKEN": "your_linkedin_access_token",
        "LINKEDIN_PAGE_ID": "your_linkedin_page_id"
      }
    }
  }
}
```

## 🛠️ Installation Steps

### **1. Clone Repository**
```bash
git clone <repository-url>
cd TrendBolt
```

### **2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -e .
```

### **4. Create Environment File**
```bash
cp env.example .env
# Edit .env with your API keys
```

### **5. Verify Installation**
```bash
python -c "from trendbolt_mcp.config import get_settings; print('✅ Configuration loaded')"
```

## 🔍 API Key Setup Guides

### **Reddit API Setup**

1. **Create Reddit Account** (if you don't have one)
2. **Go to App Preferences**: https://www.reddit.com/prefs/apps
3. **Create New App**:
   - Name: TrendBolt
   - Type: Script
   - Description: Social media automation
   - About URL: (leave blank)
   - Redirect URI: http://localhost
4. **Copy Credentials**:
   - Client ID: Under app name
   - Client Secret: Listed as "secret"

### **Azure OpenAI Setup**

1. **Create Azure Account** and subscription
2. **Create OpenAI Resource**:
   - Go to Azure Portal
   - Search "OpenAI"
   - Create new resource
3. **Deploy Model**:
   - Go to Azure OpenAI Studio
   - Deploy GPT-4 or GPT-4o model
4. **Get Credentials**:
   - Endpoint: From resource overview
   - API Key: From Keys and Endpoint section
   - Deployment Name: From model deployments

### **Canva API Setup**

1. **Create Canva Developer Account**: https://developers.canva.com/
2. **Create New App**:
   - App name: TrendBolt
   - App type: Public app
3. **Get Access Token**:
   - Follow OAuth flow or use development token
4. **Create Brand Template**:
   - Design template in Canva
   - Make it a brand template
   - Get template ID from URL

### **LinkedIn API Setup**

1. **Create LinkedIn Developer Application**:
   - Go to LinkedIn Developer Portal
   - Create new app
   - Fill in required details
2. **Request API Access**:
   - Apply for Marketing API access
   - Get approved (may take time)
3. **Get Access Token**:
   - Use OAuth 2.0 flow
   - Required scopes: `w_member_social`, `r_organization_social`
4. **Get Page ID**:
   - Use LinkedIn API or find in page URL

## 🧪 Testing Configuration

### **Test Individual Components**

```bash
# Test Reddit API
python -c "
import asyncio
from trendbolt_mcp.tools.reddit import get_trending
result = asyncio.run(get_trending(['technology'], limit=1))
print(f'✅ Reddit: {len(result)} topics found')
"

# Test Azure OpenAI
python -c "
from trendbolt_mcp.tools.llm import generate_canvas_post
topic = {'title': 'Test Topic', 'url': 'https://test.com'}
result = generate_canvas_post(topic, {'voice': 'test'})
print(f'✅ LLM: Generated {len(result)} content fields')
"

# Test Canva API
python -c "
from trendbolt_mcp.tools.canva_connect import list_brand_templates
result = list_brand_templates()
print(f'✅ Canva: {len(result.get(\"items\", []))} templates found')
"

# Test LinkedIn API
python -c "
from trendbolt_mcp.tools.linkedin import get_page_info
result = get_page_info()
print(f'✅ LinkedIn: Page info retrieved')
"
```

### **Test Complete Pipeline**

```bash
python -c "
import asyncio
from trendbolt_mcp.pipeline import run_once
result = asyncio.run(run_once(
    subreddits=['technology'],
    min_score=50
))
print(f'✅ Pipeline: Status = {result[\"status\"]}')
"
```

## ⚠️ Common Issues

### **Reddit API Issues**
- **401 Unauthorized**: Check client ID and secret
- **403 Forbidden**: Check user agent format
- **429 Rate Limited**: Implement delays between requests

### **Azure OpenAI Issues**
- **401 Unauthorized**: Check API key and endpoint
- **404 Not Found**: Check deployment name
- **429 Rate Limited**: Check quota and billing

### **Canva API Issues**
- **401 Unauthorized**: Check access token validity
- **404 Template Not Found**: Check template ID
- **403 Forbidden**: Check app permissions

### **LinkedIn API Issues**
- **401 Unauthorized**: Check access token and scopes
- **403 Forbidden**: Check API access approval
- **400 Bad Request**: Check page ID format

## 🔒 Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use environment variables** in production
3. **Rotate API keys** regularly
4. **Limit API key permissions** to minimum required
5. **Monitor API usage** and costs
6. **Use secure storage** for production credentials

## 🔗 Related Documentation

- [MCP Configuration](./mcp-config.md) - MCP server configuration
- [Workflow Configuration](./workflow-config.md) - Workflow templates
- [LinkedIn Setup](../integrations/linkedin-setup.md) - Detailed LinkedIn setup
- [API Reference](../development/api-reference.md) - Complete API documentation

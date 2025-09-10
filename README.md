# TrendBolt
Turn trending topics into scroll-stopping content — instantly. AI-powered pipeline that discovers viral conversations on Reddit, generates on-brand copy with GPT, designs a Canva post, and publishes to Facebook.

## What it does
- Fetches trending Reddit topics
- Generates a caption + design brief via LLM (Azure OpenAI gpt-4o or OpenAI fallback)
- Creates a Facebook-fit visual (default 1080×1080) using Canva (Connect + Apps SDK bridge)
- Publishes the image and caption to a Facebook Page via Graph API

See `DESIGN.md` for the detailed architecture and API choices.

## Quickstart (end-to-end)

This section describes how an end user will run TrendBolt once the MCP server and tools are implemented.

### 1) Prerequisites
- Python 3.11+
- Accounts/credentials:
  - Reddit API app (client id/secret)
  - Azure OpenAI (gpt-4o deployment) OR OpenAI API key
  - Azure Storage account (Blob) and a container for exported images
  - Facebook Page + Meta App with a Page Access Token
  - Canva developer app: enable Connect APIs and an Apps SDK bridge for design editing/export

### 2) Environment variables
Create a `.env` file in the project root (or set these in your environment):

```env
# Reddit
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=TrendBolt/1.0 by your_handle

# LLM (choose Azure OpenAI or OpenAI fallback)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o
# OPENAI_API_KEY=...

# Canva bridge
CANVA_BRIDGE_BASE_URL=https://your-canva-bridge.example.com
CANVA_BRIDGE_SIGNING_SECRET=...

# Azure Blob Storage (default storage)
AZURE_STORAGE_ACCOUNT=youraccount
AZURE_STORAGE_CONTAINER=posts
# Option A: Connection string
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net
# Option B: AAD credentials (service principal)
# AZURE_TENANT_ID=...
# AZURE_CLIENT_ID=...
# AZURE_CLIENT_SECRET=...

# Facebook
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
FACEBOOK_PAGE_ID=...
FACEBOOK_PAGE_ACCESS_TOKEN=...
```

### 3) Install & run

Once the codebase is scaffolded, install dependencies and run either the one-shot CLI or the MCP server.

```bash
# Create venv and install (placeholder commands; final commands will be added with the code scaffold)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Option A: One-shot pipeline (fetch → generate → design → post)
trendbolt pipeline run \
  --subreddits technology,worldnews \
  --limit 20 \
  --min-score 200 \
  --template-id trendbolt_template_default \
  --facebook-page-id "$FACEBOOK_PAGE_ID"

# Option B: Start MCP server and use tools from an MCP-compatible client
trendbolt mcp serve --host 127.0.0.1 --port 8765
```

### 4) Typical flow
1. Trend selection: Pulls top/hot Reddit posts and ranks them
2. Copy generation: LLM returns caption, alt text, hashtags, and design brief
3. Design creation: Canva bridge applies the brief to a default template and exports 1080×1080 PNG to Azure Blob (SAS URL)
4. Publish: Facebook Graph API posts the image with the caption (optionally scheduled)

### 5) Scheduling
You can schedule runs with cron or any scheduler. Example daily at 9am:

```cron
0 9 * * * cd /path/to/TrendBolt && . .venv/bin/activate && trendbolt pipeline run --subreddits technology --limit 10 --min-score 200 >> trendbolt.log 2>&1
```

### 6) Permissions & reviews
- Facebook: requires `pages_manage_posts` and a Page Access Token; production apps may need App Review.
- Canva: using Connect APIs and an Apps SDK app may require Canva’s app review depending on distribution.
- Reddit: follow API terms and rate limits.

### 7) Troubleshooting
- 400/401 from Facebook: verify Page Access Token and required scopes.
- Canva export not returning: ensure the bridge is reachable and the app has permissions to export.
- Blob upload issues: check container name and SAS/credentials.
- LLM errors: confirm model/deployment name and API endpoint.

### 8) Roadmap
- Multi-platform posting (Instagram, LinkedIn, X)
- Multiple templates/aspect ratios (1:1, 4:5, 16:9) with auto-cropping
- Analytics loop to learn from engagement and improve topic selection

## TrendBolt: Reddit → LLM → Canva → Facebook Automation (MCP, Python)

### 1) Goals and scope

- **Goals**
  - Automate: fetch trending Reddit topics, generate a social-ready caption and design brief via LLM, create a Canva design, and publish to Facebook.
  - Provide a Python MCP Server exposing tools for Reddit, LLM (OpenAI), Canva, and Facebook.
  - Follow MCP Server/tool standards, Python best practices, and secure secret handling.
- **Assumptions**
  - Canva uses a default template and layout; we will use a Facebook-fit aspect ratio by default.
  - Default export: 1080×1080 PNG (square, widely supported on Facebook feed). Alternate presets can be added later.
  - LLM runs on Azure OpenAI (gpt-4o) via Azure AI Foundry when available; fallback to OpenAI.
  - Asset storage defaults to Azure Blob Storage; S3/GCS are optional alternatives.
- **Non-goals (initial)**
  - Cross-platform posting beyond Facebook.
  - Full in-editor user workflows or advanced analytics.

### 2) APIs and current capabilities

- **Reddit**: OAuth 2.0; use `asyncpraw`/`praw` to query `hot`/`top` and optionally `trending_subreddits`. Rate limits apply.
- **LLM (Azure OpenAI / OpenAI)**: Use Azure OpenAI (via Azure AI Foundry) or OpenAI Responses API to produce caption, hashtags, alt text, and a structured design brief (model: `gpt-4o` family).
- **Canva**: Public automation surfaces include Canva Connect APIs (e.g., REST "Create design") and the Apps SDK (Design Editing/Bulk Create) for programmatic content updates within the editor. We will create designs via Connect API and perform content population/export via a lightweight bridge using the Apps SDK when needed.
- **Facebook (Meta Graph API)**: Post to Page via `/PAGE_ID/photos` (image + caption) or `/PAGE_ID/feed` (text). Requires `pages_manage_posts` and a Page Access Token; supports scheduling.

References: [Canva Developers](https://www.canva.dev/), [Canva Connect APIs](https://www.canva.dev/docs/connect/), [Create design](https://www.canva.dev/docs/connect/api-reference/designs/create-design/), [OpenAI Responses](https://platform.openai.com/docs/guides/responses), [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/), [Azure Blob Storage](https://learn.microsoft.com/azure/storage/blobs/), [PRAW](https://praw.readthedocs.io/), [Meta Graph API Pages/Photos](https://developers.facebook.com/docs/graph-api/reference/page/photos/)

### 3) System architecture

- **Python MCP Server (core orchestrator)**
  - Exposes tools: `reddit.get_trending`, `llm.generate_canvas_post`, `canva.create_design`, `facebook.publish_post`.
  - Async with `httpx`; schemas via `pydantic`.
- **Canva App Bridge (Node/JS)**
  - Minimal service using Canva Apps SDK to map our design brief to a predefined template and export a PNG (1080×1080). Returns `asset_url`.
- **Storage**
  - Default: Azure Blob Storage (public SAS URL for Facebook ingestion). Alternatives: S3/GCS if preferred.
- **Scheduler**
  - Cron/CI to run the pipeline periodically with dedupe.

### 4) Data flow

1. Reddit → fetch topics (subreddit list, `hot`/`top`, filters) → ranked topics.
2. LLM → generate `{caption, alt_text, hashtags, design_brief}` for a selected topic.
3. Canva → apply `design_brief` to default template → export 1080×1080 PNG → `asset_url`.
4. Facebook → post image with `caption` (optionally schedule) → return `post_id` and permalink.

### 5) MCP tools (schemas/examples)

- `reddit.get_trending` (input → output)
  - Input:
    ```json
    {
      "subreddits": ["technology", "worldnews"],
      "strategy": "hot",
      "limit": 20,
      "time_filter": "day",
      "min_score": 200
    }
    ```
  - Output:
    ```json
    {
      "topics": [
        {
          "id": "t3_abc123",
          "title": "OpenAI releases ...",
          "url": "https://reddit.com/r/technology/...",
          "subreddit": "technology",
          "score": 4321,
          "num_comments": 512,
          "created_utc": 1725942012.0
        }
      ]
    }
    ```

- `llm.generate_canvas_post`
  - Input:
    ```json
    {
      "topic": {"title": "OpenAI releases ...", "url": "https://reddit.com/..."},
      "brand": {"voice": "concise, actionable", "style_guide": "TrendBolt defaults", "cta": "Follow for more"}
    }
    ```
  - Output:
    ```json
    {
      "caption": "Big news: ... #AI #Tech",
      "alt_text": "A bold headline about ...",
      "hashtags": ["#AI", "#TechTrends"],
      "design_brief": {
        "headline": "OpenAI releases ...",
        "subtext": "Why it matters in 3 bullets ...",
        "cta": "Follow TrendBolt",
        "color_theme": "dark_on_light",
        "layout": "headline_top_subtext_center_cta_bottom",
        "image_guidance": "abstract AI circuit pattern"
      }
    }
    ```

- `canva.create_design`
  - Input:
    ```json
    {
      "template_id": "trendbolt_template_default",
      "design_brief": {
        "headline": "...",
        "subtext": "...",
        "cta": "...",
        "color_theme": "dark_on_light",
        "layout": "headline_top_subtext_center_cta_bottom"
      },
      "export": {"format": "png", "width": 1080, "height": 1080}
    }
    ```
  - Output:
    ```json
    {
      "asset_url": "https://trendbolt.blob.core.windows.net/posts/xyz.png?sv=...",
      "preview_url": "https://trendbolt.blob.core.windows.net/posts/xyz_preview.png?sv=...",
      "design_id": "canva_design_123"
    }
    ```

- `facebook.publish_post`
  - Input:
    ```json
    {
      "page_id": "123456789",
      "caption": "Big news: ...",
      "image_url": "https://trendbolt.blob.core.windows.net/posts/xyz.png?sv=...",
      "schedule": {"publish_at_unix": 1725960000}
    }
    ```
  - Output:
    ```json
    {
      "post_id": "123456789_987654321",
      "permalink_url": "https://facebook.com/..."
    }
    ```

### 6) Project layout (server-side)

```
trendbolt_mcp/
  server.py                # MCP bootstrap and tool registration
  tools/
    reddit.py              # asyncpraw integration and ranking
    llm.py                 # OpenAI Responses client & prompts
    canva.py               # HTTP client to Canva Bridge
    facebook.py            # Graph API client (httpx)
  models/                  # Pydantic request/response schemas
  config.py                # pydantic-settings for env vars
  logging.py               # structured logging
```

### 7) Configuration and secrets

- **Environment variables** (examples):
  - `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`
  - LLM (choose one):
    - Azure OpenAI: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT` (e.g., gpt-4o)
    - OpenAI (fallback): `OPENAI_API_KEY`
  - `CANVA_BRIDGE_BASE_URL`, `CANVA_BRIDGE_SIGNING_SECRET`
  - Azure Storage (default): `AZURE_STORAGE_ACCOUNT`, `AZURE_STORAGE_CONTAINER`, and either `AZURE_STORAGE_CONNECTION_STRING` or use AAD with `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
  - `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_ACCESS_TOKEN`
- Use `.env` for local dev and a secret manager for prod. Never log secrets.

### 8) Error handling & reliability

- Retries with exponential backoff on 429/5xx; idempotency keys per topic.
- Dedupe recently posted topics; cache trending queries within a window.
- Structured logging and metrics; alert on repeated failures.

### 9) Security & compliance

- OAuth best practices; store tokens securely; rotate keys.
- Respect Reddit/Canva/Meta ToS and rate limits; App Review for Facebook; Canva App review as needed.
- Signed requests between MCP Server and Canva Bridge; TLS everywhere.

### 10) Milestones

1. MCP Server skeleton with tool stubs and config.
2. Reddit trending + LLM generation end-to-end (CLI trigger).
3. Canva Bridge MVP: apply brief to default template, export 1080×1080 PNG.
4. Facebook posting (manual first, then scheduling).
5. Hardening: retries, logging, tests; token handling.
6. App reviews and production readiness.

### 11) Open questions

- Additional aspect ratios (4:5 1080×1350, 1.91:1 1200×630) needed now or later?
- Brand assets (logo/fonts/colors) to be locked in?
- Fully automated Canva export vs. semi-automated batch approve?



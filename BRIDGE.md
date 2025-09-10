## Canva Bridge: Setup & Template Mapping

This bridge lets the Python MCP server programmatically populate a Canva template and export an asset suitable for Facebook (default 1080×1080 PNG).

### 1) Prerequisites
- Create a Canva developer app in the Canva Developer Portal.
- Enable Connect APIs and Apps SDK (Design Editing / Bulk Create as needed).
- Host a small backend (Node/Express or similar) reachable by the MCP server.

### 2) Endpoint contract
- Path: `POST /api/create_design`
- Headers:
  - `Content-Type: application/json`
  - `X-Signature: <hex(hmac_sha256(secret, body))>`
- Request body (example):
  ```json
  {
    "template_id": "trendbolt_template_default",
    "design_brief": {
      "headline": "OpenAI releases ...",
      "subtext": "Why it matters in 3 bullets ...",
      "cta": "Follow TrendBolt",
      "color_theme": "dark_on_light",
      "layout": "headline_top_subtext_center_cta_bottom"
    },
    "export": {"format": "png", "width": 1080, "height": 1080}
  }
  ```
- Response body:
  ```json
  {
    "asset_url": "https://trendbolt.blob.core.windows.net/posts/xyz.png?sv=...",
    "preview_url": "https://trendbolt.blob.core.windows.net/posts/xyz_preview.png?sv=...",
    "design_id": "canva_design_123"
  }
  ```

### 3) Template mapping
- Map fields to template elements:
  - `headline` → Text element A (bold, large)
  - `subtext` → Text element B (regular, body)
  - `cta` → Text element C (button-like style)
  - `color_theme` → Apply palette/style variables
  - `layout` → Choose a preconfigured layout variant
- Keep the template ID stable; version templates when structure changes.

### 4) Security
- Validate `X-Signature` using your shared secret.
- Enforce a small request size limit and strict JSON parsing.
- Do not log secrets or full payloads; log request IDs and outcomes.

### 5) Export & storage
- Export PNG/JPG and either return a signed URL or upload to Azure Blob, returning the SAS URL.
- Recommended: upload to Azure Blob under `posts/` with a short-lived SAS.

### 6) Example (Node/Express pseudo)
```js
app.post('/api/create_design', async (req, res) => {
  const secret = process.env.CANVA_BRIDGE_SIGNING_SECRET;
  const body = JSON.stringify(req.body || {});
  const sig = crypto.createHmac('sha256', secret).update(body).digest('hex');
  if ((req.headers['x-signature'] || '') !== sig) return res.status(401).end();

  const { template_id, design_brief, export: exp } = req.body;
  // 1) Load template
  // 2) Apply design_brief to elements
  // 3) Export to PNG (1080x1080 by default)
  // 4) Upload to storage and return URLs
  return res.json({ asset_url: 'https://.../asset.png', preview_url: 'https://.../prev.png', design_id: 'id' });
});
```

For end-to-end architecture, see `DESIGN.md`. For environment variables, see `env.example` and `README.md`.



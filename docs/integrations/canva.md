# Canva Integration

TrendBolt integrates with Canva's Connect API to automatically create branded designs from generated content using brand templates and autofill functionality.

## 📋 Overview

**File**: `trendbolt_mcp/tools/canva_connect.py`  
**API**: Canva Connect API  
**Features**: Brand templates, autofill jobs, asset uploads  

## 🔧 Setup

### **1. Canva Developer Account**
1. Create a [Canva Developer Account](https://developers.canva.com/)
2. Create a new app in the Canva Developer Portal
3. Get your Client ID and Client Secret

### **2. Environment Configuration**
```env
CANVA_ACCESS_TOKEN=your_canva_access_token
CANVA_BRAND_TEMPLATE_ID=your_brand_template_id
```

### **3. OAuth Setup (Optional)**
```env
CANVA_API_CLIENT_ID=your_canva_client_id
CANVA_API_CLIENT_SECRET=your_canva_client_secret
CANVA_REDIRECT_URI=https://your-domain.com/callback
CANVA_SCOPES=design:content:read export:read
```

## 🎨 Core Features

### **Brand Templates**
- Pre-designed templates with placeholder fields
- Consistent brand styling and layout
- Automatic content population
- Professional design output

### **Autofill Jobs**
- Asynchronous design creation
- Content mapping to template fields
- Image upload and processing
- Export generation

### **Asset Management**
- Image upload from URLs
- Asset ID management
- Binary and URL-based uploads
- Asset status tracking

## 🛠️ Available Functions

### **Template Management**

#### **`list_brand_templates()`**
List available brand templates.

```python
from trendbolt_mcp.tools.canva_connect import list_brand_templates

templates = list_brand_templates(
    query="social media",
    ownership="owned",
    sort_by="relevance"
)
```

#### **`get_brand_template_dataset()`**
Get template field definitions.

```python
from trendbolt_mcp.tools.canva_connect import get_brand_template_dataset

dataset = get_brand_template_dataset()
# Returns template field structure and requirements
```

### **Autofill Operations**

#### **`create_autofill_job_from_values()`**
Create autofill job with content mapping.

```python
from trendbolt_mcp.tools.canva_connect import create_autofill_job_from_values

# Simple text fields
job = create_autofill_job_from_values(
    values={
        "title": "Your Title",
        "description": "Your content description",
        "cta": "Learn More"
    },
    image_fields={}
)
```

#### **With Image Upload**
```python
# Automatic image upload and mapping
job = create_autofill_job_from_values(
    values={
        "title": "Your Title",
        "description": "Your content",
        "hero_image": "https://example.com/image.jpg"
    },
    image_fields={
        "hero_image": "hero_image"  # Maps URL to template field
    }
)
```

#### **`get_autofill_job()`**
Check job status and get results.

```python
from trendbolt_mcp.tools.canva_connect import get_autofill_job

status = get_autofill_job(job_id="job_12345")

if status["job"]["status"] == "success":
    design = status["job"]["result"]["design"]
    thumbnail_url = design["thumbnail"]["url"]
```

### **Asset Upload**

#### **`upload_image_from_url()`**
Upload image from URL to Canva.

```python
from trendbolt_mcp.tools.canva_connect import upload_image_from_url

result = upload_image_from_url(
    image_url="https://example.com/image.jpg",
    asset_name="My Image"
)

if result["success"]:
    asset_id = result["asset_id"]
```

#### **`create_asset_upload_job()`**
Create binary asset upload job.

```python
from trendbolt_mcp.tools.canva_connect import create_asset_upload_job

job = create_asset_upload_job(
    image_url="https://example.com/image.jpg",
    asset_name="Uploaded Image"
)
```

## 🔄 Workflow Integration

### **Basic Pipeline Integration**
```python
# In trendbolt_mcp/pipeline.py
autofill_data = {
    "title": {"type": "text", "text": content.get("title", "")},
    "headline": {"type": "text", "text": content.get("headline", "")},
    "description": {"type": "text", "text": content.get("description", "")},
}

job = create_autofill_job(
    data=autofill_data,
    brand_template_id=template_id
)
```

### **LangChain Workflow Integration**
```python
# Enhanced polling with URL validation
max_attempts = 20
poll_interval = 3

for attempt in range(max_attempts):
    await asyncio.sleep(poll_interval)
    
    status = get_autofill_job(job_id)
    if status["job"]["status"] == "success":
        design = status["job"]["result"]["design"]
        # Ensure thumbnail URL is available
        if design.get("thumbnail", {}).get("url"):
            return design
```

### **MCP Server Integration**
```python
# Automatic image upload in MCP server
processed_data = {}
for key, value in raw_data.items():
    if is_image_url(value):
        upload_result = upload_image_from_url(value, f"Auto-uploaded {key}")
        if upload_result["success"]:
            processed_data[key] = upload_result["asset_id"]
```

## 📊 Job Status Flow

```
pending → processing → success
                   ↓
                 failed
```

### **Status Handling**
```python
def handle_job_status(status_response):
    job_status = status_response["job"]["status"]
    
    if job_status == "success":
        return status_response["job"]["result"]["design"]
    elif job_status == "failed":
        error = status_response["job"].get("error", "Unknown error")
        raise Exception(f"Canva job failed: {error}")
    elif job_status in ["pending", "processing"]:
        return None  # Continue polling
    else:
        raise Exception(f"Unknown job status: {job_status}")
```

## 🎯 Template Field Mapping

### **Common Template Fields**
```python
COMMON_FIELDS = {
    "title": "Main headline text",
    "subtitle": "Secondary headline",
    "description": "Body text content",
    "cta": "Call-to-action button text",
    "image": "Hero image",
    "background_image": "Background image",
    "logo": "Brand logo",
    "brand_name": "Company name"
}
```

### **Content Mapping Strategy**
```python
def map_content_to_template(content, template_fields):
    mapping = {}
    
    # Text fields
    mapping["title"] = content.get("title", "")[:60]  # Canva title limit
    mapping["description"] = content.get("description", "")[:200]
    mapping["cta"] = content.get("cta", "Learn More")[:20]
    
    # Image fields (if available)
    if content.get("image_url"):
        mapping["image"] = content["image_url"]
    
    return mapping
```

## 🔍 Error Handling

### **Common Error Scenarios**

#### **Authentication Errors**
```python
if "unauthorized" in error_message.lower():
    raise Exception("Canva access token invalid or expired")
```

#### **Template Errors**
```python
if "template not found" in error_message.lower():
    raise Exception(f"Brand template {template_id} not found")
```

#### **Job Failures**
```python
if job_status == "failed":
    error_details = status["job"].get("error", {})
    error_type = error_details.get("type", "unknown")
    error_message = error_details.get("message", "Unknown error")
    raise Exception(f"Canva job failed ({error_type}): {error_message}")
```

### **Retry Logic**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def create_design_with_retry(data):
    return create_autofill_job_from_values(data)
```

## 📈 Performance Optimization

### **Polling Best Practices**
- **Start with 3-second intervals** for job polling
- **Increase to 20 attempts maximum** for complex designs
- **Validate thumbnail URL** before considering job complete
- **Implement exponential backoff** for failed requests

### **Image Upload Optimization**
- **Use URL uploads** when possible (faster than binary)
- **Validate image URLs** before upload
- **Cache asset IDs** to avoid duplicate uploads
- **Handle upload failures gracefully**

## 🧪 Testing

### **Unit Tests**
```python
def test_create_autofill_job():
    job = create_autofill_job_from_values(
        values={"title": "Test Title"},
        image_fields={}
    )
    assert job["success"] is True
    assert "job" in job
```

### **Integration Tests**
```python
@pytest.mark.asyncio
async def test_complete_design_workflow():
    # Create job
    job = create_autofill_job_from_values(test_data)
    job_id = job["job"]["id"]
    
    # Poll for completion
    for _ in range(10):
        status = get_autofill_job(job_id)
        if status["job"]["status"] == "success":
            assert "thumbnail" in status["job"]["result"]["design"]
            break
        await asyncio.sleep(2)
```

## 🔧 Configuration Examples

### **Brand Template Setup**
```python
# Environment configuration
CANVA_BRAND_TEMPLATE_ID = "BAF1234567890"  # Your template ID
CANVA_ACCESS_TOKEN = "your_access_token"

# Template field mapping
TEMPLATE_FIELDS = {
    "title": "headline",      # Map content.title to template.headline
    "description": "body",    # Map content.description to template.body
    "cta": "button_text"     # Map content.cta to template.button_text
}
```

### **Workflow Configuration**
```python
# Polling configuration
CANVA_POLLING = {
    "max_attempts": 20,
    "poll_interval": 3,
    "timeout_seconds": 60
}

# Image upload configuration
IMAGE_UPLOAD = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "supported_formats": [".jpg", ".jpeg", ".png", ".gif", ".webp"]
}
```

## 🔗 Related Documentation

- [Basic Pipeline](../workflows/basic-pipeline.md) - Pipeline integration
- [LangChain Workflow](../workflows/langchain-workflow.md) - AI workflow integration
- [MCP Tools](../workflows/mcp-tools.md) - MCP server tools
- [Environment Setup](../configuration/environment-setup.md) - Configuration guide

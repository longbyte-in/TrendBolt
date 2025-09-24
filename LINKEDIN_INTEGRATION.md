# LinkedIn Integration for TrendBolt

This document explains how to set up and use LinkedIn integration with TrendBolt for posting content from Canva to LinkedIn Pages using the **LinkedIn Advertising API with Development Tier** access.

## ✅ LinkedIn Advertising API Access

**You have the correct access!** The LinkedIn Advertising API with Development Tier includes:
- **Posts API** (`/rest/posts`) - For creating posts on LinkedIn Pages
- **Required permissions**: `w_organization_social`, `w_member_social`
- **Member (3-legged OAuth)** - Standard OAuth flow

## What's Included

The LinkedIn integration includes:

- **Posts API Integration** (`tools/linkedin.py`) - Uses `/rest/posts` endpoint
- **Pipeline Integration** (updated `pipeline.py`)
- **Configuration Settings** (updated `config.py`)
- **Comprehensive Tests** (`tests/test_linkedin.py`)

## Setup Instructions

### 1. Create LinkedIn App

1. Go to https://www.linkedin.com/developers/apps
2. Click "Create app"
3. Fill in app details:
   - **App name**: TrendBolt
   - **LinkedIn Page**: Select your company page
   - **Privacy policy URL**: Your privacy policy
   - **App logo**: Upload a logo
4. Submit for review

### 2. Verify Posts API Access

1. In your LinkedIn app dashboard, go to "Products"
2. Verify you have "Advertising API" with "Development Tier" access
3. Confirm you have the `/rest/posts` endpoint with `w_organization_social` and `w_member_social` permissions

### 3. Configure Environment Variables

Add these to your `.env` file:

```bash
# LinkedIn Configuration
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_PAGE_ID=your_page_id_here
LINKEDIN_ACCESS_TOKEN=your_access_token_here
```

### 4. Get Your Page ID

Your LinkedIn Page ID can be found in your LinkedIn Page admin settings or by using the `get_user_organizations()` function.

### 5. Obtain Access Token

Use the OAuth flow provided in `auth/linkedin_oauth.py`:

```python
from trendbolt_mcp.auth.linkedin_oauth import generate_auth_url, exchange_code_for_token

# Generate authorization URL
auth_url, state = generate_auth_url("http://localhost:8080/callback")
print(f"Visit: {auth_url}")

# After user authorizes, exchange code for token
token_data = exchange_code_for_token(authorization_code, "http://localhost:8080/callback")
access_token = token_data["access_token"]
```

## Usage

### Basic Post Creation

```python
from trendbolt_mcp.tools.linkedin import create_image_post, create_text_post

# Create image post
result = create_image_post(
    image_url="https://example.com/image.jpg",
    text="Check out this amazing design from Canva!"
)

# Create text-only post
result = create_text_post("Just posted a new design!")
```

### Pipeline Integration

The pipeline now automatically posts to both Facebook and LinkedIn:

```python
from trendbolt_mcp.pipeline import run_once

result = await run_once()
print(f"Facebook post: {result['facebook_post']}")
print(f"LinkedIn post: {result['linkedin_post']}")
```

## API Functions

### OAuth Functions (`auth/linkedin_oauth.py`)

- `generate_auth_url()` - Generate LinkedIn OAuth authorization URL
- `exchange_code_for_token()` - Exchange authorization code for access token
- `refresh_access_token()` - Refresh expired access token
- `get_user_profile()` - Get LinkedIn user profile
- `get_user_organizations()` - Get organizations user can manage

### Posting Functions (`tools/linkedin.py`)

- `create_image_post()` - Create post with image
- `create_text_post()` - Create text-only post
- `get_page_info()` - Get LinkedIn Page information

## Error Handling

The integration includes comprehensive error handling:

- **Missing credentials** - Clear error messages for missing config
- **API errors** - Detailed error logging with response content
- **Network timeouts** - Retry logic with exponential backoff
- **Invalid tokens** - Graceful handling of expired tokens

## Testing

Run the LinkedIn tests:

```bash
pytest tests/test_linkedin.py -v
```

## Limitations

1. **API Access**: Requires LinkedIn approval for Marketing API access
2. **Rate Limits**: LinkedIn has strict rate limits
3. **Content Restrictions**: LinkedIn has content policies that must be followed
4. **Image Upload**: Images must be uploaded through LinkedIn's asset registration process

## Alternative Approaches

If you cannot get LinkedIn Marketing API access, consider:

1. **LinkedIn Ads API** - For advertising content only
2. **Third-party platforms** - Use services like Zapier, IFTTT, or Buffer
3. **Manual posting** - Export from Canva and post manually
4. **LinkedIn's native Canva integration** - Use Canva's LinkedIn Ads app

## Troubleshooting

### Common Issues

1. **"LinkedIn Marketing API access required"**
   - You need to apply for and receive approval for Marketing API access

2. **"Invalid access token"**
   - Your token may be expired or invalid
   - Use the refresh token flow or re-authenticate

3. **"Page not found"**
   - Verify your `LINKEDIN_PAGE_ID` is correct
   - Ensure you have admin access to the page

4. **"Image upload failed"**
   - Check that the image URL is accessible
   - Verify image format is supported by LinkedIn

### Getting Help

- LinkedIn Developer Documentation: https://docs.microsoft.com/en-us/linkedin/
- LinkedIn Developer Community: https://www.linkedin.com/groups/35227/
- LinkedIn API Support: https://www.linkedin.com/help/linkedin/answer/a1343

## Security Notes

- Never commit your `.env` file with real credentials
- Use environment variables for all sensitive data
- Regularly rotate your access tokens
- Follow LinkedIn's API terms of service

---

**Note**: This integration assumes you have LinkedIn Marketing API access. If you don't have access, you'll need to apply for it through LinkedIn's developer program.

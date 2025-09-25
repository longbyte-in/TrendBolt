# LinkedIn Integration Setup Guide

## ✅ Dependencies Installed

All required Python packages have been installed in your virtual environment:
- `httpx` - HTTP client for API requests
- `tenacity` - Retry logic for API calls
- `pydantic-settings` - Configuration management

## 🔧 Setup Instructions

### Step 1: Get LinkedIn App Credentials

1. **Go to LinkedIn Developer Portal**: https://www.linkedin.com/developers/apps
2. **Create a new app** (or use existing one)
3. **Get your credentials**:
   - `Client ID` (from Auth tab)
   - `Client Secret` (from Auth tab)

### Step 2: Set Up Redirect URI

In your LinkedIn app settings:
1. Go to **Auth** tab
2. Add redirect URI: `https://oauth.pstmn.io/v1/callback`
3. Save changes

### Step 3: Get Access Token

**Note**: Since you already have your access token, you can skip the OAuth flow and go directly to Step 4.

### Step 4: Configure Environment Variables

Add to your `.env` file:
```bash
# LinkedIn App Credentials
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here

# LinkedIn Page and Token (obtained through OAuth)
LINKEDIN_PAGE_ID=your_page_id_here
LINKEDIN_ACCESS_TOKEN=your_access_token_here
```

### Step 5: Test Integration

After getting your token, test the integration:
```bash
source venv/bin/activate
python test_linkedin_posts_api.py
```

## 🎯 Quick Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Test LinkedIn integration
python test_linkedin_posts_api.py
```

## 📋 Required Environment Variables

Your `.env` file should contain:
```bash
# LinkedIn App Credentials (from LinkedIn Developer Portal)
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret

# LinkedIn Page and Token (obtained through OAuth)
LINKEDIN_PAGE_ID=your_page_id
LINKEDIN_ACCESS_TOKEN=your_access_token
```

## 🚀 Ready to Use!

Once you have all the credentials set up, your TrendBolt pipeline will automatically post to LinkedIn!

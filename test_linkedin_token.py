#!/usr/bin/env python3
"""
Alternative script to help find your LinkedIn Page ID.
This uses a different API approach that might work better.
"""

import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_me_info(access_token: str) -> dict:
    """Get basic user info to verify token works."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    
    url = "https://api.linkedin.com/v2/me"
    
    with httpx.Client() as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

def main():
    """Main function to help find LinkedIn Page ID."""
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ Error: LINKEDIN_ACCESS_TOKEN not found in environment variables.")
        print("Please add your LinkedIn access token to your .env file:")
        print("LINKEDIN_ACCESS_TOKEN=your_token_here")
        return
    
    try:
        print("🔍 Testing your LinkedIn access token...")
        
        # Test basic access
        me_info = get_me_info(access_token)
        print(f"✅ Token is valid! Connected as: {me_info.get('firstName', '')} {me_info.get('lastName', '')}")
        
        print("\n📋 To find your LinkedIn Page ID manually:")
        print("1. Go to your LinkedIn Page (the company page you want to post to)")
        print("2. Click on 'Admin tools' in the top navigation")
        print("3. Go to 'Page info' or 'Settings'")
        print("4. Look for 'Page ID' or 'Organization ID' - it will be a numeric value")
        print("\n🔗 Alternative method:")
        print("1. Go to your LinkedIn Page URL (e.g., https://www.linkedin.com/company/your-company)")
        print("2. Right-click and 'View Page Source'")
        print("3. Search for 'organizationId' in the source code")
        print("4. Look for a number like 'organizationId': 123456789")
        
        print(f"\n🎯 Once you find it, add this to your .env file:")
        print("LINKEDIN_PAGE_ID=your_page_id_here")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your access token is valid and not expired")
        print("2. Check that your LinkedIn app has the required permissions")
        print("3. Verify you're using the correct token format")

if __name__ == "__main__":
    main()

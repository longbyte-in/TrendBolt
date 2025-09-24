#!/usr/bin/env python3
"""
Script to help you find your LinkedIn Page ID.
This script will help you discover your LinkedIn Page ID using your access token.
"""

import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_user_organizations(access_token: str) -> dict:
    """Get all organizations (pages) the user has access to."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    
    # Get organizations the user is an admin of
    url = "https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee&role=ADMINISTRATOR"
    
    with httpx.Client() as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

def get_organization_details(org_id: str, access_token: str) -> dict:
    """Get detailed information about a specific organization."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    
    url = f"https://api.linkedin.com/v2/organizations/{org_id}"
    
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
        print("🔍 Searching for your LinkedIn Pages...")
        
        # Get all organizations
        orgs_response = get_user_organizations(access_token)
        
        if not orgs_response.get("elements"):
            print("❌ No organizations found. Make sure you have admin access to a LinkedIn Page.")
            return
        
        print(f"✅ Found {len(orgs_response['elements'])} organization(s) you have admin access to:\n")
        
        for i, org_acl in enumerate(orgs_response["elements"], 1):
            org_id = org_acl["organizationalTarget"].split(":")[-1]  # Extract ID from URN
            
            try:
                # Get detailed info about this organization
                org_details = get_organization_details(org_id, access_token)
                
                print(f"📄 Organization {i}:")
                print(f"   Name: {org_details.get('name', 'N/A')}")
                print(f"   Page ID: {org_id}")
                print(f"   Vanity Name: {org_details.get('vanityName', 'N/A')}")
                print(f"   Website: {org_details.get('website', 'N/A')}")
                print(f"   Industry: {org_details.get('industry', 'N/A')}")
                print(f"   LinkedIn URL: https://www.linkedin.com/company/{org_details.get('vanityName', org_id)}")
                print()
                
            except Exception as e:
                print(f"❌ Error getting details for organization {org_id}: {e}")
                print(f"   Page ID: {org_id}")
                print()
        
        print("🎯 To use with TrendBolt, add this to your .env file:")
        print("LINKEDIN_PAGE_ID=your_chosen_page_id_here")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your access token is valid")
        print("2. Ensure you have admin access to at least one LinkedIn Page")
        print("3. Check that your LinkedIn app has the required permissions")

if __name__ == "__main__":
    main()

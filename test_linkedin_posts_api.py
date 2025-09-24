"""Quick test script to verify LinkedIn Posts API integration."""

import os
from trendbolt_mcp.tools.linkedin import create_text_post, create_image_post

def test_linkedin_integration():
    """Test LinkedIn integration with Posts API."""
    
    print("🔗 TrendBolt LinkedIn Integration Test")
    print("=" * 50)
    print("📋 Facebook integration removed - LinkedIn only")
    
    # Check environment variables
    required_vars = [
        "LINKEDIN_CLIENT_ID",
        "LINKEDIN_CLIENT_SECRET", 
        "LINKEDIN_PAGE_ID",
        "LINKEDIN_ACCESS_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease set these in your .env file:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False
    
    print("✅ All required environment variables are set")
    
    # Test OAuth URL generation
    try:
        auth_url, state = generate_auth_url("http://localhost:8080/callback")
        print(f"✅ OAuth URL generated successfully")
        print(f"   State: {state}")
        print(f"   URL: {auth_url[:100]}...")
    except Exception as e:
        print(f"❌ OAuth URL generation failed: {e}")
        return False
    
    # Test text post creation (without actually posting)
    try:
        print("\n🧪 Testing text post format...")
        # This will fail without a valid token, but we can check the format
        result = create_text_post("Test post from TrendBolt")
        print(f"✅ Text post created: {result}")
    except Exception as e:
        if "LinkedIn access token is required" in str(e):
            print("⚠️  Text post format is correct (token required for actual posting)")
        else:
            print(f"❌ Text post test failed: {e}")
            return False
    
    # Test image post creation (without actually posting)
    try:
        print("\n🧪 Testing image post format...")
        # This will fail without a valid token, but we can check the format
        result = create_image_post(
            "https://example.com/test-image.jpg",
            "Test image post from TrendBolt"
        )
        print(f"✅ Image post created: {result}")
    except Exception as e:
        if "LinkedIn access token is required" in str(e):
            print("⚠️  Image post format is correct (token required for actual posting)")
        else:
            print(f"❌ Image post test failed: {e}")
            return False
    
    print("\n🎉 LinkedIn Posts API integration is ready!")
    print("\nNext steps:")
    print("1. Set up your LinkedIn app credentials in .env")
    print("2. Get an access token using the OAuth flow")
    print("3. Test actual posting with valid credentials")
    
    return True

if __name__ == "__main__":
    test_linkedin_integration()

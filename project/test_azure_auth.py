#!/usr/bin/env python3
"""
Test script for Azure JWT authentication with real Azure users.
This script helps you understand and test the complete auth flow.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

import httpx
from app.auth import AzureJWTAuth
from app.config import get_settings
from app.db import init_db
from app.models.tortoise import User


async def test_azure_auth_flow():
    """Test the complete Azure authentication flow."""
    print("🔐 Azure JWT Authentication Flow Test")
    print("=" * 50)
    
    # Initialize Tortoise ORM directly
    from tortoise import Tortoise
    settings = get_settings()
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["app.models.tortoise"]}
    )
    
    print(f"📋 Configuration:")
    print(f"   Environment: {settings.environment}")
    print(f"   Use Mock Auth: {settings.use_mock_auth}")
    print(f"   Azure Tenant ID: {settings.azure_tenant_id}")
    print(f"   Azure Client ID: {settings.azure_client_id}")
    print()
    
    # Test 1: JWKS Retrieval
    print("🔑 Step 1: Testing JWKS Retrieval")
    try:
        azure_auth = AzureJWTAuth()
        jwks_uri = azure_auth.get_jwks_uri()
        print(f"   JWKS URI: {jwks_uri}")
        
        jwks = await azure_auth.get_jwks()
        print(f"   ✅ JWKS Retrieved: {len(jwks.get('keys', []))} keys found")
        print(f"   🗝️  First key ID: {jwks['keys'][0]['kid'] if jwks.get('keys') else 'None'}")
    except Exception as e:
        print(f"   ❌ JWKS Error: {e}")
        return
    
    print()
    
    # Test 2: Show how to get a real token
    print("🎫 Step 2: How to Get a Real Azure Token")
    print("   To test with a real Azure user, you need an access token.")
    print("   Here are several ways to get one:")
    print()
    
    print("   Option A: Using Azure CLI (Recommended for testing)")
    print("   1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
    print("   2. Login: az login")
    print(f"   3. Get token: az account get-access-token --resource {settings.azure_client_id}")
    print()
    
    print("   Option B: Using PowerShell (Windows)")
    print("   1. Install Azure PowerShell module")
    print("   2. Connect-AzAccount")
    print("   3. Get-AzAccessToken")
    print()
    
    print("   Option C: Manual OAuth Flow (Browser)")
    oauth_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/authorize"
    params = {
        "client_id": settings.azure_client_id,
        "response_type": "token",
        "redirect_uri": "http://localhost:8000",  # You'll need to add this to Azure app
        "scope": f"{settings.azure_client_id}/.default",
        "response_mode": "fragment"
    }
    param_string = "&".join([f"{k}={v}" for k, v in params.items()])
    print(f"   Open: {oauth_url}?{param_string}")
    print()
    
    # Test 3: Show current users in database
    print("👥 Step 3: Current Users in Database")
    users = await User.all()
    if users:
        for user in users:
            print(f"   • {user.email} ({user.role}) - Azure OID: {user.azure_oid}")
    else:
        print("   No users found in database")
    
    print()
    print("🧪 Step 4: Testing with a Token")
    print("   Once you have a token, you can test it by:")
    print("   1. Set USE_MOCK_AUTH=false in docker-compose.yml")
    print("   2. Restart containers: docker compose restart")
    print("   3. Use the /auth/validate-token endpoint:")
    print("      curl -X POST http://localhost:8000/auth/validate-token \\")
    print("           -H 'Authorization: Bearer YOUR_TOKEN_HERE'")
    print()
    print("   Or use the test endpoints in your FastAPI app at:")
    print("   http://localhost:8000/docs")


async def validate_token_manually(token: str):
    """Manually validate a token and show the process."""
    print(f"🔍 Manual Token Validation Test")
    print("=" * 40)
    
    from tortoise import Tortoise
    from app.config import get_settings
    settings = get_settings()
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["app.models.tortoise"]}
    )
    azure_auth = AzureJWTAuth()
    
    try:
        # Step 1: Validate token
        print("Step 1: Validating token...")
        claims = await azure_auth.validate_azure_jwt(token)
        print("✅ Token is valid!")
        print(f"Claims: {json.dumps(claims, indent=2)}")
        print()
        
        # Step 2: Extract user info
        print("Step 2: Extracting user information...")
        email = claims.get("preferred_username") or claims.get("email") or claims.get("upn")
        azure_oid = claims.get("oid")
        roles = claims.get("roles", [])
        groups = claims.get("groups", [])
        
        print(f"   Email: {email}")
        print(f"   Azure OID: {azure_oid}")
        print(f"   Roles: {roles}")
        print(f"   Groups: {groups}")
        print()
        
        # Step 3: Role mapping
        print("Step 3: Role mapping...")
        user_role = azure_auth._map_azure_roles_to_app_roles(claims)
        print(f"   Mapped to application role: {user_role}")
        print()
        
        # Step 4: User creation/retrieval
        print("Step 4: User creation/retrieval...")
        user, created = await User.get_or_create(
            azure_oid=azure_oid, 
            defaults={"email": email, "role": user_role}
        )
        
        if created:
            print(f"   ✅ New user created: {user.email} ({user.role})")
        else:
            print(f"   ✅ Existing user found: {user.email} ({user.role})")
            
        return user
        
    except Exception as e:
        print(f"   ❌ Token validation failed: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If a token is provided as argument, validate it
        token = sys.argv[1]
        asyncio.run(validate_token_manually(token))
    else:
        # Otherwise, run the general test
        asyncio.run(test_azure_auth_flow())
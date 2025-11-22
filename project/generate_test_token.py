#!/usr/bin/env python3
"""
Generate a test JWT token that matches Azure format for local testing.
This creates a token with the correct claims structure that your app expects.
"""

import jwt
import json
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def create_test_azure_token():
    """Create a test JWT token that matches Azure AD format."""
    
    # Generate a test RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Create Azure-like JWT claims
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=1)
    
    claims = {
        # Standard JWT claims
        "iss": "https://login.microsoftonline.com/078c6c18-7434-4931-81cd-7b9603fda5a2/v2.0",
        "aud": "70050862-5a60-4865-b3b5-4bbf913e4ca9",
        "exp": int(exp.timestamp()),
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        
        # Azure AD specific claims
        "sub": "test-user-12345",
        "oid": "test-object-id-67890",  # Azure Object ID
        "tid": "078c6c18-7434-4931-81cd-7b9603fda5a2",  # Tenant ID
        "ver": "2.0",
        
        # User information
        "preferred_username": "testuser@yourdomain.com",
        "email": "testuser@yourdomain.com",
        "upn": "testuser@yourdomain.com",
        "name": "Test User",
        "given_name": "Test",
        "family_name": "User",
        
        # Role/Permission claims (you can modify these)
        "roles": ["admin"],  # Change to ["writer"] or ["reader"] to test different roles
        "groups": ["fastapi-admins"],  # Azure AD groups
        
        # Additional Azure claims
        "appid": "70050862-5a60-4865-b3b5-4bbf913e4ca9",
        "appidacr": "1",
        "idp": "https://sts.windows.net/078c6c18-7434-4931-81cd-7b9603fda5a2/",
        "rh": "test-refresh-hint",
        "scp": "access_as_user",
        "unique_name": "testuser@yourdomain.com"
    }
    
    # Create JWT with test key
    token = jwt.encode(
        claims,
        private_pem,
        algorithm="RS256",
        headers={"kid": "test-key-id-123"}
    )
    
    return token, claims

if __name__ == "__main__":
    print("🎫 Generating Test Azure JWT Token")
    print("=" * 50)
    
    token, claims = create_test_azure_token()
    
    print("📋 Token Claims:")
    print(json.dumps(claims, indent=2, default=str))
    print()
    
    print("🎫 Generated JWT Token:")
    print(token)
    print()
    
    print("🧪 Test Commands:")
    print("1. Test token validation:")
    print(f"   curl -X POST 'http://localhost:8004/auth/validate-token' -H 'Authorization: Bearer {token}'")
    print()
    
    print("2. Test user authentication:")
    print(f"   curl -H 'Authorization: Bearer {token}' http://localhost:8004/auth/test/me")
    print()
    
    print("3. Test admin access:")
    print(f"   curl -H 'Authorization: Bearer {token}' http://localhost:8004/auth/test/test-authorization/admin")
    print()
    
    print("📝 Note:")
    print("   This token won't validate against real Azure JWKS (different keys).")
    print("   But it shows the exact format your app expects from Azure AD.")
    print("   Modify the 'roles' array in the script to test different user roles.")
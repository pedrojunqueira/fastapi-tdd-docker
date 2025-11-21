"""
Test utilities for Azure JWT authentication.
Provides tools for creating mock Azure JWT tokens for testing.
"""

import base64
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@dataclass
class AzureTokenConfig:
    """Configuration for creating Azure JWT tokens."""
    email: str
    roles: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)
    tenant_id: str = "test-tenant-id"
    client_id: str = "test-client-id"
    expires_in_minutes: int = 60
    additional_claims: dict[str, Any] = field(default_factory=dict)


class MockAzureJWT:
    """Create mock Azure JWT tokens for testing."""

    def __init__(self):
        # Generate a test RSA key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

        # Serialize keys
        self.private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Key ID for JWKS
        self.kid = "test-key-id-123"

    def create_jwks(self) -> dict[str, Any]:
        """Create a mock JWKS response."""
        # Convert public key to JWK format
        public_numbers = self.public_key.public_numbers()

        # Convert to base64url format
        def int_to_base64url(value: int) -> str:
            byte_length = (value.bit_length() + 7) // 8
            value_bytes = value.to_bytes(byte_length, "big")
            return base64.urlsafe_b64encode(value_bytes).decode("ascii").rstrip("=")

        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": self.kid,
                    "x5t": "test-x5t",
                    "n": int_to_base64url(public_numbers.n),
                    "e": int_to_base64url(public_numbers.e),
                    "x5c": [],
                    "issuer": "https://login.microsoftonline.com/test-tenant/v2.0"
                }
            ]
        }

    def create_azure_jwt(self, config: AzureTokenConfig) -> str:
        """Create a mock Azure JWT token."""
        now = datetime.utcnow()
        exp = now + timedelta(minutes=config.expires_in_minutes)
        
        # Standard Azure JWT claims
        claims = {
            "iss": f"https://login.microsoftonline.com/{config.tenant_id}/v2.0",
            "aud": config.client_id,
            "exp": int(exp.timestamp()),
            "iat": int(now.timestamp()),
            "nbf": int(now.timestamp()),
            "sub": f"test-user-{hash(config.email)}",
            "oid": f"test-object-id-{hash(config.email)}",
            "tid": config.tenant_id,
            "ver": "2.0",
            "preferred_username": config.email,
            "email": config.email,
            "upn": config.email,
            "name": f"Test User {config.email}",
            "given_name": "Test",
            "family_name": f"User {config.email}",
        }
        
        # Add roles if provided
        if config.roles:
            claims["roles"] = config.roles
            
        # Add groups if provided
        if config.groups:
            claims["groups"] = config.groups
            
        # Add any additional claims
        if config.additional_claims:
            claims.update(config.additional_claims)
        
        # Create JWT with test key
        token = jwt.encode(
            claims,
            self.private_pem,
            algorithm="RS256",
            headers={"kid": self.kid}
        )
        
        return token
    
    def create_expired_token(self, email: str) -> str:
        """Create an expired Azure JWT token for testing."""
        config = AzureTokenConfig(email=email, expires_in_minutes=-60)
        return self.create_azure_jwt(config)
    
    def create_invalid_signature_token(self, email: str) -> str:
        """Create a token with invalid signature for testing."""
        # Create token with different key
        different_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        different_pem = different_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        now = datetime.utcnow()
        exp = now + timedelta(hours=1)
        
        claims = {
            "iss": "https://login.microsoftonline.com/test-tenant-id/v2.0",
            "aud": "test-client-id",
            "exp": int(exp.timestamp()),
            "iat": int(now.timestamp()),
            "preferred_username": email,
            "email": email,
            "oid": f"test-object-id-{hash(email)}",
        }
        
        return jwt.encode(
            claims,
            different_pem,
            algorithm="RS256",
            headers={"kid": self.kid}
        )


# Global test JWT instance
mock_azure_jwt = MockAzureJWT()


def create_test_azure_token(
    email: str,
    role: str = "reader",
    expires_in_minutes: int = 60
) -> str:
    """Convenience function to create test Azure JWT tokens."""
    roles = [role] if role else []
    config = AzureTokenConfig(
        email=email,
        roles=roles,
        expires_in_minutes=expires_in_minutes
    )
    return mock_azure_jwt.create_azure_jwt(config)


def create_test_azure_token_with_groups(
    email: str,
    groups: list[str],
    expires_in_minutes: int = 60
) -> str:
    """Create test Azure JWT token with group membership."""
    config = AzureTokenConfig(
        email=email,
        groups=groups,
        expires_in_minutes=expires_in_minutes
    )
    return mock_azure_jwt.create_azure_jwt(config)

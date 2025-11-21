"""Tests for Azure JWT authentication integration."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone

from app.auth import AzureJWTAuth
from app.config import Settings
from tests.utils.azure_jwt_mock import MockAzureJWT, AzureTokenConfig


@pytest.fixture
def mock_azure_jwt():
    """Create a MockAzureJWT instance for testing."""
    return MockAzureJWT()


@pytest.fixture
def azure_auth():
    """Create an AzureJWTAuth instance for testing."""
    # Mock the settings for testing
    auth = AzureJWTAuth()
    auth.settings.azure_tenant_id = "test-tenant-id"
    auth.settings.azure_client_id = "test-client-id"
    return auth


@pytest.fixture
def valid_token_config():
    """Create a valid token configuration."""
    return AzureTokenConfig(
        email="test@example.com",
        roles=["User", "Admin"],
        groups=["group1", "group2"],
        additional_claims={"name": "Test User", "sub": "user123"}
    )


class TestAzureJWTAuth:
    """Test Azure JWT authentication functionality."""

    @pytest.mark.asyncio
    async def test_validate_azure_jwt_success(self, azure_auth, mock_azure_jwt, valid_token_config):
        """Test successful JWT validation."""
        # Generate a valid token
        token = mock_azure_jwt.create_token(valid_token_config)
        
        # Mock the JWKS response
        with patch.object(azure_auth, 'get_jwks', return_value=mock_azure_jwt.get_jwks_response()):
            claims = await azure_auth.validate_azure_jwt(token)
            
            assert claims["sub"] == "user123"
            assert claims["name"] == "Test User"
            assert claims["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_validate_azure_jwt_expired(self, azure_auth, mock_azure_jwt):
        """Test validating an expired token."""
        # Create an expired token
        expired_config = AzureTokenConfig(
            sub="user123",
            name="Test User",
            email="test@example.com",
            exp=int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp())
        )
        token = mock_azure_jwt.create_token(expired_config)
        
        with patch.object(azure_auth, 'get_jwks', return_value=mock_azure_jwt.get_jwks_response()):
            with pytest.raises(HTTPException) as exc_info:
                await azure_auth.validate_azure_jwt(token)
            
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_validate_azure_jwt_invalid_signature(self, azure_auth, mock_azure_jwt, valid_token_config):
        """Test validating a token with invalid signature."""
        # Create a token with one key pair
        token = mock_azure_jwt.create_token(valid_token_config)
        
        # Create a different MockAzureJWT instance (different keys)
        different_mock = MockAzureJWT()
        
        # Use different JWKS (wrong keys)
        with patch.object(azure_auth, 'get_jwks', return_value=different_mock.get_jwks_response()):
            with pytest.raises(HTTPException) as exc_info:
                await azure_auth.validate_azure_jwt(token)
            
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_validate_azure_jwt_malformed(self, azure_auth):
        """Test validating a malformed token."""
        malformed_token = "not.a.valid.jwt.token"
        
        with pytest.raises(HTTPException) as exc_info:
            await azure_auth.validate_azure_jwt(malformed_token)
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_jwks_caching(self, azure_auth, mock_azure_jwt):
        """Test JWKS response caching with TTL."""
        jwks_response = mock_azure_jwt.get_jwks_response()
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = jwks_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # First call should make HTTP request
            result1 = await azure_auth.get_jwks()
            assert mock_get.call_count == 1
            assert result1 == jwks_response
            
            # Second call should use cache
            result2 = await azure_auth.get_jwks()
            assert mock_get.call_count == 1  # No additional HTTP call
            assert result2 == jwks_response

    @pytest.mark.asyncio
    async def test_jwks_cache_expiry(self, azure_auth, mock_azure_jwt):
        """Test JWKS cache expiration."""
        jwks_response = mock_azure_jwt.get_jwks_response()
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = jwks_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Make first call
            await azure_auth.get_jwks()
            assert mock_get.call_count == 1
            
            # Simulate cache expiry by setting past timestamp
            azure_auth._jwks_cache_expiry = datetime.now(timezone.utc) - timedelta(hours=25)
            
            # Second call should make new HTTP request
            await azure_auth.get_jwks()
            assert mock_get.call_count == 2

    @pytest.mark.asyncio
    async def test_jwks_network_error(self, azure_auth):
        """Test handling of network errors when fetching JWKS."""
        with patch('httpx.AsyncClient.get', side_effect=Exception("Network error")):
            with pytest.raises(HTTPException) as exc_info:
                await azure_auth.get_jwks()
            
            assert exc_info.value.status_code == 503
            assert "Unable to fetch Azure JWKS" in str(exc_info.value.detail)

    def test_role_mapping_app_roles(self, azure_auth):
        """Test role mapping with Azure app roles."""
        from app.auth import UserRole
        token_data = {
            "roles": ["admin", "administrator"]
        }
        
        mapped_role = azure_auth._map_azure_roles_to_app_roles(token_data)
        assert mapped_role == UserRole.ADMIN

    def test_role_mapping_groups(self, azure_auth):
        """Test role mapping with Azure AD groups."""
        from app.auth import UserRole
        token_data = {
            "groups": ["fastapi-admins", "system-administrators"]
        }
        
        mapped_role = azure_auth._map_azure_roles_to_app_roles(token_data)
        assert mapped_role == UserRole.ADMIN

    def test_role_mapping_default(self, azure_auth):
        """Test role mapping with no matching roles or groups."""
        from app.auth import UserRole
        token_data = {}
        
        mapped_role = azure_auth._map_azure_roles_to_app_roles(token_data)
        assert mapped_role == UserRole.READER

    @pytest.mark.asyncio
    async def test_get_user_from_azure_jwt(self, azure_auth, mock_azure_jwt, valid_token_config):
        """Test User object creation from Azure JWT."""
        token = mock_azure_jwt.create_token(valid_token_config)
        
        with patch.object(azure_auth, 'get_jwks', return_value=mock_azure_jwt.get_jwks_response()):
            user = await azure_auth.get_user_from_azure_jwt(token)
            
            assert user.azure_oid == "user123"
            assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_concurrent_jwks_requests(self, azure_auth, mock_azure_jwt):
        """Test that concurrent JWKS requests are handled properly."""
        import asyncio
        
        jwks_response = mock_azure_jwt.get_jwks_response()
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = jwks_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Make multiple concurrent requests
            tasks = [azure_auth.get_jwks() for _ in range(5)]
            results = await asyncio.gather(*tasks)
            
            # All should return the same result
            assert all(result == jwks_response for result in results)
            # Should only make one HTTP request due to caching
            assert mock_get.call_count == 1
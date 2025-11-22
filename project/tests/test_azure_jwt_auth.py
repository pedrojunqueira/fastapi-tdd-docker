"""Tests for Azure JWT authentication integration."""

import pytest

from app.auth import AzureJWTAuth


@pytest.fixture
def azure_auth():
    """Create an AzureJWTAuth instance for testing."""
    # Mock the settings for testing
    auth = AzureJWTAuth()
    auth.settings.azure_tenant_id = "test-tenant-id"
    auth.settings.azure_client_id = "test-client-id"
    return auth


class TestAzureJWTAuth:
    """Test Azure JWT authentication functionality."""

    @pytest.mark.asyncio
    async def test_validate_azure_jwt_malformed(self, azure_auth):
        """Test validating a malformed token."""
        from fastapi import HTTPException

        malformed_token = "not.a.valid.jwt.token"  # noqa: S105

        with pytest.raises(HTTPException) as exc_info:
            await azure_auth.validate_azure_jwt(malformed_token)

        assert exc_info.value.status_code == 401

    def test_role_mapping_app_roles(self, azure_auth):
        """Test role mapping with Azure app roles."""
        from app.auth import UserRole

        token_data = {"roles": ["admin", "administrator"]}

        mapped_role = azure_auth._map_azure_roles_to_app_roles(token_data)
        assert mapped_role == UserRole.ADMIN

    def test_role_mapping_groups(self, azure_auth):
        """Test role mapping with Azure AD groups."""
        from app.auth import UserRole

        token_data = {"groups": ["fastapi-admins", "system-administrators"]}

        mapped_role = azure_auth._map_azure_roles_to_app_roles(token_data)
        assert mapped_role == UserRole.ADMIN

    def test_role_mapping_default(self, azure_auth):
        """Test role mapping with no matching roles or groups."""
        from app.auth import UserRole

        token_data = {}

        mapped_role = azure_auth._map_azure_roles_to_app_roles(token_data)
        assert mapped_role == UserRole.READER

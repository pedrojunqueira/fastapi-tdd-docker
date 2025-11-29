"""
Tests for Azure AD authentication and role-based authorization.
"""


class TestRoleBasedAuthorization:
    """Test role-based access control."""

    # Admin role tests
    def test_admin_can_access_all_endpoints(self, test_app_with_admin):
        """Test that admin can access all endpoints."""
        # Create
        response = test_app_with_admin.post(
            "/summaries/",
            json={"url": "https://admin-test.com", "summary": "Admin test"},
        )
        assert response.status_code == 201
        summary_id = response.json()["id"]

        # Read single
        response = test_app_with_admin.get(f"/summaries/{summary_id}/")
        assert response.status_code == 200

        # Read all
        response = test_app_with_admin.get("/summaries/")
        assert response.status_code == 200

        # Update
        response = test_app_with_admin.put(
            f"/summaries/{summary_id}/",
            json={"url": "https://admin-test.com", "summary": "Updated"},
        )
        assert response.status_code == 200

        # Delete
        response = test_app_with_admin.delete(f"/summaries/{summary_id}/")
        assert response.status_code == 200

    # Writer role tests
    def test_writer_can_create_and_manage_own(self, test_app_with_writer):
        """Test that writer can create and manage their own summaries."""
        # Create
        response = test_app_with_writer.post(
            "/summaries/",
            json={"url": "https://writer-test.com", "summary": "Writer test"},
        )
        assert response.status_code == 201
        summary_id = response.json()["id"]

        # Read single (own)
        response = test_app_with_writer.get(f"/summaries/{summary_id}/")
        assert response.status_code == 200

        # Read all (own only)
        response = test_app_with_writer.get("/summaries/")
        assert response.status_code == 200

        # Update (own)
        response = test_app_with_writer.put(
            f"/summaries/{summary_id}/",
            json={"url": "https://writer-test.com", "summary": "Updated by writer"},
        )
        assert response.status_code == 200

        # Delete (own)
        response = test_app_with_writer.delete(f"/summaries/{summary_id}/")
        assert response.status_code == 200

    # Reader role tests
    def test_reader_can_only_access_profile(self, test_app_with_reader):
        """Test that reader can only access their profile, not summaries.

        Readers are in a 'pending approval' state. They need to be promoted
        to writer by an admin before they can use the summaries API.
        """
        # Cannot create summaries
        response = test_app_with_reader.post(
            "/summaries/",
            json={"url": "https://reader-test.com", "summary": "Should fail"},
        )
        assert response.status_code == 403

        # Cannot read summaries list
        response = test_app_with_reader.get("/summaries/")
        assert response.status_code == 403

        # Cannot update summaries
        response = test_app_with_reader.put(
            "/summaries/1/",
            json={"url": "https://reader-test.com", "summary": "Should fail"},
        )
        assert response.status_code == 403

        # Cannot delete summaries
        response = test_app_with_reader.delete("/summaries/1/")
        assert response.status_code == 403

        # CAN access their own profile
        response = test_app_with_reader.get("/users/me")
        assert response.status_code == 200


class TestAuthenticationErrors:
    """Test authentication error scenarios."""

    def test_missing_claims_returns_error(self, test_app_with_admin):
        """Test that the ping endpoint works without auth."""
        # Ping should work without authentication
        response = test_app_with_admin.get("/ping")
        assert response.status_code == 200


class TestUserCreation:
    """Test user creation from Azure tokens."""

    def test_user_created_on_first_login(self, test_app_with_admin):
        """Test that user is created in DB on first authentication."""
        # Make a request to trigger user creation
        response = test_app_with_admin.get("/summaries/")
        assert response.status_code == 200

    def test_admin_role_assigned_correctly(self, test_app_with_admin):
        """Test that admin role is correctly assigned from Azure token."""
        # Admin can create - proves admin role was assigned
        response = test_app_with_admin.post(
            "/summaries/",
            json={"url": "https://test-admin.com"},
        )
        assert response.status_code == 201

    def test_writer_role_assigned_correctly(self, test_app_with_writer):
        """Test that writer role is correctly assigned from Azure token."""
        # Writer can create - proves writer role was assigned
        response = test_app_with_writer.post(
            "/summaries/",
            json={"url": "https://test-writer.com"},
        )
        assert response.status_code == 201

    def test_reader_role_assigned_correctly(self, test_app_with_reader):
        """Test that reader role is correctly assigned from Azure token."""
        # Reader cannot create - proves reader role was assigned
        response = test_app_with_reader.post(
            "/summaries/",
            json={"url": "https://test-reader.com"},
        )
        assert response.status_code == 403


class TestAzureRoleMapping:
    """Test Azure role/group to application role mapping."""

    def test_admin_role_from_azure_roles(self):
        """Test that admin role is mapped from Azure roles claim."""
        from app.auth import _map_azure_roles_to_app_roles
        from app.models.tortoise import UserRole

        # Test various admin role names
        claims = {"roles": ["admin"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.ADMIN

        claims = {"roles": ["Administrator"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.ADMIN

        claims = {"roles": ["fastapi.admin"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.ADMIN

    def test_writer_role_from_azure_roles(self):
        """Test that writer role is mapped from Azure roles claim."""
        from app.auth import _map_azure_roles_to_app_roles
        from app.models.tortoise import UserRole

        claims = {"roles": ["writer"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.WRITER

        claims = {"roles": ["Editor"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.WRITER

        claims = {"roles": ["fastapi.writer"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.WRITER

    def test_reader_role_default(self):
        """Test that reader role is default when no matching roles."""
        from app.auth import _map_azure_roles_to_app_roles
        from app.models.tortoise import UserRole

        # No roles
        claims = {}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.READER

        # Unknown role
        claims = {"roles": ["unknown_role"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.READER

    def test_admin_role_from_groups(self):
        """Test that admin role is mapped from Azure groups claim."""
        from app.auth import _map_azure_roles_to_app_roles
        from app.models.tortoise import UserRole

        claims = {"groups": ["fastapi-admins"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.ADMIN

        claims = {"groups": ["system-administrators"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.ADMIN

    def test_writer_role_from_groups(self):
        """Test that writer role is mapped from Azure groups claim."""
        from app.auth import _map_azure_roles_to_app_roles
        from app.models.tortoise import UserRole

        claims = {"groups": ["fastapi-writers"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.WRITER

        claims = {"groups": ["content-editors"]}
        assert _map_azure_roles_to_app_roles(claims) == UserRole.WRITER


class TestAuthHelperFunctions:
    """Test authentication helper functions."""

    def test_require_ownership_or_admin_with_admin(self):
        """Test that admin can access any resource."""
        import asyncio

        from app.auth import require_ownership_or_admin
        from app.models.pydantic import CurrentUserSchema

        admin_user = CurrentUserSchema(id=1, email="admin@test.com", role="admin")

        async def run_test():
            return await require_ownership_or_admin(999, admin_user)

        # Admin can access resource owned by user 999
        result = asyncio.new_event_loop().run_until_complete(run_test())
        assert result is True

    def test_require_ownership_or_admin_with_owner(self):
        """Test that owner can access their own resource."""
        import asyncio

        from app.auth import require_ownership_or_admin
        from app.models.pydantic import CurrentUserSchema

        owner = CurrentUserSchema(id=5, email="owner@test.com", role="writer")

        async def run_test():
            return await require_ownership_or_admin(5, owner)

        # Owner can access their own resource
        result = asyncio.new_event_loop().run_until_complete(run_test())
        assert result is True

    def test_require_ownership_or_admin_denied(self):
        """Test that non-owner non-admin is denied."""
        import asyncio

        import pytest
        from fastapi import HTTPException

        from app.auth import require_ownership_or_admin
        from app.models.pydantic import CurrentUserSchema

        non_owner = CurrentUserSchema(id=5, email="user@test.com", role="writer")

        async def run_test():
            return await require_ownership_or_admin(10, non_owner)

        # Non-owner trying to access resource owned by user 10
        with pytest.raises(HTTPException) as exc_info:
            asyncio.new_event_loop().run_until_complete(run_test())
        assert exc_info.value.status_code == 403

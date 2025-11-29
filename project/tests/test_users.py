"""
Tests for user management API endpoints.

Note: These tests use mocked authentication. The fixtures mock either:
- get_azure_user: For Azure token claims (used by registration)
- get_current_user_from_azure: For authenticated user (used by protected endpoints)
"""


class TestUserRegistration:
    """Test user self-registration."""

    def test_new_user_can_register(self, test_app_with_unregistered_user):
        """Test that a new Azure AD user can register themselves.

        Note: First user becomes admin, subsequent users become readers.
        Since tests share a database, the role depends on test order.
        """
        response = test_app_with_unregistered_user.post("/users/register")
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] in [
            "admin",
            "reader",
        ]  # First user gets admin, others get reader
        assert "id" in data
        assert "created_at" in data

    def test_user_cannot_register_twice(self, test_app_with_unregistered_user):
        """Test that an already registered user cannot register again."""
        # First registration should succeed
        response1 = test_app_with_unregistered_user.post("/users/register")
        assert response1.status_code == 201

        # Second registration should fail
        response2 = test_app_with_unregistered_user.post("/users/register")
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"]


class TestUserProfile:
    """Test user profile endpoint."""

    def test_registered_user_can_get_profile(self, test_app_with_unregistered_user):
        """Test that a registered user can get their profile."""
        # First register the user
        reg_response = test_app_with_unregistered_user.post("/users/register")
        assert reg_response.status_code == 201

        # Now get profile
        response = test_app_with_unregistered_user.get("/users/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "reader"

    def test_unregistered_user_gets_404(self, test_app_with_unregistered_user):
        """Test that an unregistered user gets 404 for profile."""
        response = test_app_with_unregistered_user.get("/users/me")
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"].lower()


class TestAdminUserManagement:
    """Test admin-only user management endpoints."""

    def test_admin_can_list_users(self, test_app_with_admin):
        """Test that admin can list all users."""
        response = test_app_with_admin.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)

    def test_admin_can_get_user_by_id(self, test_app_with_admin):
        """Test that admin can get a specific user."""
        # First list users to get an ID
        list_response = test_app_with_admin.get("/users/")
        users = list_response.json()["users"]
        if users:
            user_id = users[0]["id"]
            response = test_app_with_admin.get(f"/users/{user_id}")
            assert response.status_code == 200
            assert response.json()["id"] == user_id

    def test_admin_can_update_user_role(self, test_app_with_admin):
        """Test that admin can update a user's role."""
        # First list users
        list_response = test_app_with_admin.get("/users/")
        users = list_response.json()["users"]

        if users:
            # Update first user's role
            target_user = users[0]
            new_role = "writer" if target_user["role"] != "writer" else "reader"
            response = test_app_with_admin.put(
                f"/users/{target_user['id']}",
                json={"role": new_role},
            )
            assert response.status_code == 200
            assert response.json()["role"] == new_role

    def test_admin_cannot_delete_self(self, test_app_with_admin):
        """Test that admin cannot delete themselves."""
        # The mocked admin has user_id=1, try to delete that
        response = test_app_with_admin.delete("/users/1")
        assert response.status_code == 400
        assert "Cannot delete yourself" in response.json()["detail"]

    def test_admin_get_nonexistent_user(self, test_app_with_admin):
        """Test 404 when getting non-existent user."""
        response = test_app_with_admin.get("/users/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_admin_update_with_invalid_role(self, test_app_with_admin):
        """Test that invalid role returns 400."""
        list_response = test_app_with_admin.get("/users/")
        users = list_response.json()["users"]
        if users:
            response = test_app_with_admin.put(
                f"/users/{users[0]['id']}",
                json={"role": "superadmin"},  # Invalid role
            )
            assert response.status_code == 400
            assert "Invalid role" in response.json()["detail"]


class TestNonAdminAccess:
    """Test that non-admin users cannot access admin endpoints."""

    def test_reader_cannot_list_users(self, test_app_with_reader):
        """Test that reader cannot list users."""
        response = test_app_with_reader.get("/users/")
        assert response.status_code == 403

    def test_writer_cannot_list_users(self, test_app_with_writer):
        """Test that writer cannot list users."""
        response = test_app_with_writer.get("/users/")
        assert response.status_code == 403

    def test_reader_cannot_update_users(self, test_app_with_reader):
        """Test that reader cannot update users."""
        response = test_app_with_reader.put("/users/1", json={"role": "admin"})
        assert response.status_code == 403

    def test_reader_cannot_delete_users(self, test_app_with_reader):
        """Test that reader cannot delete users."""
        response = test_app_with_reader.delete("/users/1")
        assert response.status_code == 403

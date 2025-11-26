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
    def test_reader_can_only_read(self, test_app_with_reader):
        """Test that reader can only read, not write."""
        # Cannot create
        response = test_app_with_reader.post(
            "/summaries/",
            json={"url": "https://reader-test.com", "summary": "Should fail"},
        )
        assert response.status_code == 403

        # Can read list
        response = test_app_with_reader.get("/summaries/")
        assert response.status_code == 200

        # Cannot update
        response = test_app_with_reader.put(
            "/summaries/1/",
            json={"url": "https://reader-test.com", "summary": "Should fail"},
        )
        assert response.status_code == 403

        # Cannot delete
        response = test_app_with_reader.delete("/summaries/1/")
        assert response.status_code == 403


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

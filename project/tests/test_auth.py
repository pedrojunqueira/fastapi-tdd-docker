"""
Tests for authentication and authorization functionality.
"""

import uuid


class TestMockAuthentication:
    """Test the mock authentication system."""

    def test_create_summary_as_admin(self, test_app_with_db):
        """Test that admin can create summaries."""
        headers = {"Authorization": "Bearer mock:admin@example.com:admin"}

        response = test_app_with_db.post(
            "/summaries/",
            headers=headers,
            json={"url": "https://example.com", "summary": "Admin created summary"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["url"] == "https://example.com/"
        assert data["summary"] == "Admin created summary"
        assert data["user_id"] is not None

    def test_create_summary_as_writer(self, test_app_with_db):
        """Test that writer can create summaries."""
        headers = {"Authorization": "Bearer mock:writer@example.com:writer"}

        response = test_app_with_db.post(
            "/summaries/",
            headers=headers,
            json={"url": "https://example.com", "summary": "Writer created summary"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["summary"] == "Writer created summary"

    def test_create_summary_as_reader_forbidden(self, test_app_with_db):
        """Test that reader cannot create summaries."""
        headers = {"Authorization": "Bearer mock:reader@example.com:reader"}

        response = test_app_with_db.post(
            "/summaries/",
            headers=headers,
            json={"url": "https://example.com", "summary": "Should fail"},
        )

        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_create_summary_without_auth_fails(self, test_app_with_db):
        """Test that unauthenticated requests fail."""
        response = test_app_with_db.post(
            "/summaries/", json={"url": "https://example.com", "summary": "Should fail"}
        )

        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_invalid_token_fails(self, test_app_with_db):
        """Test that invalid tokens fail."""
        headers = {"Authorization": "Bearer invalid-token"}

        response = test_app_with_db.post(
            "/summaries/", headers=headers, json={"url": "https://example.com"}
        )

        assert response.status_code == 401
        assert "Invalid authentication credentials" in response.json()["detail"]


class TestRoleBasedAccess:
    """Test role-based access control."""

    def test_writer_can_only_see_own_summaries(self, test_app_with_db):
        """Test that writers can only see their own summaries."""
        unique_id = str(uuid.uuid4())[:8]

        # Create summary as writer1 with unique email
        headers1 = {
            "Authorization": f"Bearer mock:writer1-{unique_id}@example.com:writer"
        }
        response1 = test_app_with_db.post(
            "/summaries/",
            headers=headers1,
            json={"url": "https://writer1.com", "summary": "Writer 1 summary"},
        )
        assert response1.status_code == 201
        summary1_id = response1.json()["id"]

        # Create summary as writer2 with unique email
        headers2 = {
            "Authorization": f"Bearer mock:writer2-{unique_id}@example.com:writer"
        }
        response2 = test_app_with_db.post(
            "/summaries/",
            headers=headers2,
            json={"url": "https://writer2.com", "summary": "Writer 2 summary"},
        )
        assert response2.status_code == 201

        # Writer1 should only see their own summary in list
        response = test_app_with_db.get("/summaries/", headers=headers1)
        assert response.status_code == 200
        summaries = response.json()
        assert len(summaries) == 1
        assert summaries[0]["url"] == "https://writer1.com/"

        # Writer1 should not be able to access writer2's summary directly
        response = test_app_with_db.get(
            f"/summaries/{response2.json()['id']}/", headers=headers1
        )
        assert response.status_code == 404

        # Writer1 should be able to access their own summary
        response = test_app_with_db.get(f"/summaries/{summary1_id}/", headers=headers1)
        assert response.status_code == 200

    def test_admin_can_see_all_summaries(self, test_app_with_db):
        """Test that admin can see all summaries."""
        # Create summary as writer
        writer_headers = {"Authorization": "Bearer mock:writer@example.com:writer"}
        response1 = test_app_with_db.post(
            "/summaries/",
            headers=writer_headers,
            json={"url": "https://writer.com", "summary": "Writer summary"},
        )
        assert response1.status_code == 201

        # Create summary as admin
        admin_headers = {"Authorization": "Bearer mock:admin@example.com:admin"}
        response2 = test_app_with_db.post(
            "/summaries/",
            headers=admin_headers,
            json={"url": "https://admin.com", "summary": "Admin summary"},
        )
        assert response2.status_code == 201

        # Admin should see all summaries
        response = test_app_with_db.get("/summaries/", headers=admin_headers)
        assert response.status_code == 200
        summaries = response.json()
        assert len(summaries) >= 2  # At least the two we created

        # Admin should be able to access any summary
        response = test_app_with_db.get(
            f"/summaries/{response1.json()['id']}/", headers=admin_headers
        )
        assert response.status_code == 200

    def test_writer_cannot_delete_others_summary(self, test_app_with_db):
        """Test that writers cannot delete other users' summaries."""
        # Create summary as writer1
        headers1 = {"Authorization": "Bearer mock:writer1@example.com:writer"}
        response1 = test_app_with_db.post(
            "/summaries/",
            headers=headers1,
            json={"url": "https://writer1.com", "summary": "Writer 1 summary"},
        )
        assert response1.status_code == 201
        summary_id = response1.json()["id"]

        # Try to delete as different writer
        headers2 = {"Authorization": "Bearer mock:writer2@example.com:writer"}
        response = test_app_with_db.delete(
            f"/summaries/{summary_id}/", headers=headers2
        )
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_admin_can_delete_any_summary(self, test_app_with_db):
        """Test that admin can delete any summary."""
        # Create summary as writer
        writer_headers = {"Authorization": "Bearer mock:writer@example.com:writer"}
        response1 = test_app_with_db.post(
            "/summaries/",
            headers=writer_headers,
            json={"url": "https://writer.com", "summary": "Writer summary"},
        )
        assert response1.status_code == 201
        summary_id = response1.json()["id"]

        # Delete as admin
        admin_headers = {"Authorization": "Bearer mock:admin@example.com:admin"}
        response = test_app_with_db.delete(
            f"/summaries/{summary_id}/", headers=admin_headers
        )
        assert response.status_code == 200

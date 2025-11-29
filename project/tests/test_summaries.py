"""
Tests for summaries API endpoints with Azure AD authentication.
"""


class TestSummariesWithWriter:
    """Test summary CRUD operations with writer role."""

    def test_create_summary(self, test_app_with_writer):
        """Test that writer can create summaries."""
        response = test_app_with_writer.post(
            "/summaries/",
            json={"url": "https://foo.bar"},
        )
        assert response.status_code == 201
        assert response.json()["url"] == "https://foo.bar/"

    def test_create_summary_with_custom_summary(self, test_app_with_writer):
        """Test creating a summary with a custom summary provided."""
        response = test_app_with_writer.post(
            "/summaries/",
            json={
                "url": "https://example.com/article",
                "summary": "Custom article summary",
            },
        )
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["url"] == "https://example.com/article"
        assert response_data["summary"] == "Custom article summary"

    def test_create_summaries_invalid_json(self, test_app_with_writer):
        """Test validation for missing required fields."""
        response = test_app_with_writer.post("/summaries/", json={})
        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"] == ["body", "url"]

    def test_read_summary(self, test_app_with_writer):
        """Test writer can read their own summary."""
        response = test_app_with_writer.post(
            "/summaries/",
            json={"url": "https://foo.bar"},
        )
        summary_id = response.json()["id"]

        response = test_app_with_writer.get(f"/summaries/{summary_id}/")
        assert response.status_code == 200

        response_dict = response.json()
        assert response_dict["id"] == summary_id
        assert response_dict["url"] == "https://foo.bar/"

    def test_remove_summary(self, test_app_with_writer):
        """Test writer can delete their own summary."""
        response = test_app_with_writer.post(
            "/summaries/",
            json={"url": "https://foo.bar"},
        )
        summary_id = response.json()["id"]

        response = test_app_with_writer.delete(f"/summaries/{summary_id}/")
        assert response.status_code == 200
        assert response.json()["url"] == "https://foo.bar/"

    def test_update_summary(self, test_app_with_writer):
        """Test writer can update their own summary."""
        response = test_app_with_writer.post(
            "/summaries/",
            json={"url": "https://foo.bar"},
        )
        summary_id = response.json()["id"]

        response = test_app_with_writer.put(
            f"/summaries/{summary_id}/",
            json={"url": "https://foo.bar", "summary": "updated!"},
        )
        assert response.status_code == 200

        response_dict = response.json()
        assert response_dict["id"] == summary_id
        assert response_dict["url"] == "https://foo.bar/"
        assert response_dict["summary"] == "updated!"

    def test_update_summary_incorrect_id(self, test_app_with_writer):
        """Test 404 when updating non-existent summary."""
        response = test_app_with_writer.put(
            "/summaries/99999/",
            json={"url": "https://foo.bar/", "summary": "updated!"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Summary not found"


class TestSummariesWithAdmin:
    """Test summary operations with admin role."""

    def test_admin_can_create_summary(self, test_app_with_admin):
        """Test that admin can create summaries."""
        response = test_app_with_admin.post(
            "/summaries/",
            json={"url": "https://example.com", "summary": "Admin summary"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["url"] == "https://example.com/"
        assert data["summary"] == "Admin summary"

    def test_read_summary_incorrect_id(self, test_app_with_admin):
        """Test 404 for non-existent summary."""
        response = test_app_with_admin.get("/summaries/99999/")
        assert response.status_code == 404
        assert response.json()["detail"] == "Summary not found"

    def test_read_all_summaries(self, test_app_with_admin):
        """Test admin can read all summaries."""
        response = test_app_with_admin.post(
            "/summaries/",
            json={"url": "https://foo.bar"},
        )
        summary_id = response.json()["id"]

        response = test_app_with_admin.get("/summaries/")
        assert response.status_code == 200

        response_list = response.json()
        assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1

    def test_remove_summary_incorrect_id(self, test_app_with_admin):
        """Test 404 when deleting non-existent summary."""
        response = test_app_with_admin.delete("/summaries/99999/")
        assert response.status_code == 404
        assert response.json()["detail"] == "Summary not found"


class TestSummariesWithReader:
    """Test that reader role has no access to summaries.

    Readers are essentially in a 'pending approval' state.
    They can only access /users/me until promoted to writer by an admin.
    """

    def test_reader_cannot_create_summary(self, test_app_with_reader):
        """Test that reader cannot create summaries."""
        response = test_app_with_reader.post(
            "/summaries/",
            json={"url": "https://example.com", "summary": "Should fail"},
        )
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_reader_cannot_read_summaries_list(self, test_app_with_reader):
        """Test that reader cannot read summaries list."""
        response = test_app_with_reader.get("/summaries/")
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_reader_cannot_read_single_summary(self, test_app_with_reader):
        """Test that reader cannot read a single summary."""
        response = test_app_with_reader.get("/summaries/1/")
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_reader_cannot_delete_summary(self, test_app_with_reader):
        """Test that reader cannot delete summaries."""
        response = test_app_with_reader.delete("/summaries/1/")
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_reader_cannot_update_summary(self, test_app_with_reader):
        """Test that reader cannot update summaries."""
        response = test_app_with_reader.put(
            "/summaries/1/",
            json={"url": "https://foo.bar/", "summary": "updated!"},
        )
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

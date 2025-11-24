"""
Updated tests for authentication using dependency overrides.
"""

import os

import pytest
from starlette.testclient import TestClient
from tortoise.contrib.fastapi import register_tortoise

from app.auth import get_current_user_from_azure
from app.config import Settings, get_settings
from app.main import create_application
from app.models.pydantic import CurrentUserSchema
from app.models.tortoise import User, UserRole


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


def create_mock_user_dependency(email: str, role: str):
    """Create a mock user dependency for testing."""

    async def _mock_user():
        role_enum = UserRole(role)
        oid = f"test-oid-{email}"
        user, _created = await User.get_or_create(
            azure_oid=oid, defaults={"email": email, "role": role_enum}
        )
        return CurrentUserSchema(id=user.id, email=user.email, role=user.role.value)

    return _mock_user


class TestAuthentication:
    """Test authentication with different roles."""

    @pytest.fixture
    def app_with_admin(self):
        """App configured with admin user."""
        from app.main import azure_scheme

        # Mock Azure config loading
        async def mock_load_config():
            pass

        azure_scheme.openid_config.load_config = mock_load_config

        app = create_application()
        app.dependency_overrides[get_settings] = get_settings_override
        app.dependency_overrides[get_current_user_from_azure] = (
            create_mock_user_dependency("admin@test.com", "admin")
        )
        register_tortoise(
            app,
            db_url=os.environ.get("DATABASE_TEST_URL"),
            modules={"models": ["app.models.tortoise"]},
            generate_schemas=True,
            add_exception_handlers=True,
        )
        with TestClient(app) as client:
            yield client

    @pytest.fixture
    def app_with_writer(self):
        """App configured with writer user."""
        from app.main import azure_scheme

        # Mock Azure config loading
        async def mock_load_config():
            pass

        azure_scheme.openid_config.load_config = mock_load_config

        app = create_application()
        app.dependency_overrides[get_settings] = get_settings_override
        app.dependency_overrides[get_current_user_from_azure] = (
            create_mock_user_dependency("writer@test.com", "writer")
        )
        register_tortoise(
            app,
            db_url=os.environ.get("DATABASE_TEST_URL"),
            modules={"models": ["app.models.tortoise"]},
            generate_schemas=True,
            add_exception_handlers=True,
        )
        with TestClient(app) as client:
            yield client

    @pytest.fixture
    def app_with_reader(self):
        """App configured with reader user."""
        from app.main import azure_scheme

        # Mock Azure config loading
        async def mock_load_config():
            pass

        azure_scheme.openid_config.load_config = mock_load_config

        app = create_application()
        app.dependency_overrides[get_settings] = get_settings_override
        app.dependency_overrides[get_current_user_from_azure] = (
            create_mock_user_dependency("reader@test.com", "reader")
        )
        register_tortoise(
            app,
            db_url=os.environ.get("DATABASE_TEST_URL"),
            modules={"models": ["app.models.tortoise"]},
            generate_schemas=True,
            add_exception_handlers=True,
        )
        with TestClient(app) as client:
            yield client

    def test_admin_can_create_summary(self, app_with_admin):
        """Test that admin can create summaries."""
        response = app_with_admin.post(
            "/summaries/",
            json={"url": "https://example.com", "summary": "Admin summary"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["url"] == "https://example.com/"
        assert data["summary"] == "Admin summary"

    def test_writer_can_create_summary(self, app_with_writer):
        """Test that writer can create summaries."""
        response = app_with_writer.post(
            "/summaries/",
            json={"url": "https://example.com", "summary": "Writer summary"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["summary"] == "Writer summary"

    def test_reader_cannot_create_summary(self, app_with_reader):
        """Test that reader cannot create summaries."""
        response = app_with_reader.post(
            "/summaries/",
            json={"url": "https://example.com", "summary": "Should fail"},
        )
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

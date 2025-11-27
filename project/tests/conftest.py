import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.testclient import TestClient
from tortoise.contrib.fastapi import register_tortoise

from app.auth import get_azure_user
from app.config import Settings, get_settings
from app.main import create_application


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


def create_mock_azure_user(email: str, role: str, oid: str | None = None):
    """Create a mock Azure user object that mimics what azure_scheme returns."""
    mock_user = MagicMock()
    mock_user.claims = {
        "preferred_username": email,
        "email": email,
        "oid": oid or f"test-oid-{email}",
        "roles": [role],  # Azure App Roles
    }
    return mock_user


def create_mock_azure_user_dependency(email: str, role: str, oid: str | None = None):
    """Create a mock dependency that returns a mock Azure user."""
    mock_user = create_mock_azure_user(email, role, oid)

    async def _mock_azure_user():
        return mock_user

    return _mock_azure_user


def mock_azure_scheme_config():
    """Mock the Azure scheme's OpenID config loading to prevent network calls."""
    from app.azure import azure_scheme

    # Mock the load_config method to do nothing
    azure_scheme.openid_config.load_config = AsyncMock()


@pytest.fixture(scope="module")
def test_app():
    # set up
    mock_azure_scheme_config()
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:
        # testing
        yield test_client

    # tear down


@pytest.fixture(scope="module")
def test_app_with_db():
    # set up
    mock_azure_scheme_config()
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_TEST_URL"),
        modules={"models": ["app.models.tortoise"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    with TestClient(app) as test_client:
        # testing
        yield test_client

    # tear down


@pytest.fixture
def test_app_with_admin():
    """Test app with admin user authentication."""
    mock_azure_scheme_config()
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_azure_user] = create_mock_azure_user_dependency(
        "admin@test.com", "admin"
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
def test_app_with_writer():
    """Test app with writer user authentication."""
    mock_azure_scheme_config()
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_azure_user] = create_mock_azure_user_dependency(
        "writer@test.com", "writer"
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
def test_app_with_reader():
    """Test app with reader user authentication."""
    mock_azure_scheme_config()
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_azure_user] = create_mock_azure_user_dependency(
        "reader@test.com", "reader"
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

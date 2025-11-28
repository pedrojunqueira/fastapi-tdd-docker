import os
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.testclient import TestClient
from tortoise.contrib.fastapi import register_tortoise

from app.auth import get_azure_user, get_current_user_from_azure
from app.azure import azure_scheme
from app.config import Settings, get_settings
from app.main import create_application
from app.models.pydantic import CurrentUserSchema
from app.models.tortoise import User, UserRole


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


def create_mock_current_user_dependency(user_id: int, email: str, role: str):
    """Create a mock dependency that returns a CurrentUserSchema directly.
    This bypasses database lookup entirely for tests."""

    async def _mock_current_user():
        return CurrentUserSchema(id=user_id, email=email, role=role)

    return _mock_current_user


def mock_azure_scheme_config():
    """Mock the Azure scheme's OpenID config loading to prevent network calls."""
    # Mock the load_config method to do nothing
    azure_scheme.openid_config.load_config = AsyncMock()


async def ensure_user_exists(email: str, role: str, oid: str | None = None) -> User:
    """Ensure a user exists in the database for testing."""
    azure_oid = oid or f"test-oid-{email}"
    role_enum = UserRole(role)
    user, _ = await User.get_or_create(
        azure_oid=azure_oid,
        defaults={"email": email, "role": role_enum},
    )
    # Update role if different
    if user.role != role_enum:
        user.role = role_enum
        await user.save()
    return user


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
    """Test app with admin user authentication.
    Mocks the current user directly to bypass database lookup."""
    mock_azure_scheme_config()
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    # Mock get_current_user_from_azure to return admin user directly
    app.dependency_overrides[get_current_user_from_azure] = (
        create_mock_current_user_dependency(1, "admin@test.com", "admin")
    )
    # Also mock get_azure_user for endpoints that use it directly (like registration)
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
    """Test app with writer user authentication.
    Mocks the current user directly to bypass database lookup."""
    mock_azure_scheme_config()
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_current_user_from_azure] = (
        create_mock_current_user_dependency(2, "writer@test.com", "writer")
    )
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
    """Test app with reader user authentication.
    Mocks the current user directly to bypass database lookup."""
    mock_azure_scheme_config()
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_current_user_from_azure] = (
        create_mock_current_user_dependency(3, "reader@test.com", "reader")
    )
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


@pytest.fixture
def test_app_with_unregistered_user():
    """Test app with an unregistered Azure AD user.
    Only mocks the Azure token, not the current user lookup.
    Use this for testing registration flow."""
    mock_azure_scheme_config()
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    # Use a unique OID that won't exist in the database
    unique_oid = f"unregistered-{uuid.uuid4()}"
    app.dependency_overrides[get_azure_user] = create_mock_azure_user_dependency(
        "newuser@test.com", "reader", oid=unique_oid
    )
    # DON'T mock get_current_user_from_azure - let it do the DB lookup
    # This allows testing the registration flow properly
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_TEST_URL"),
        modules={"models": ["app.models.tortoise"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    with TestClient(app) as client:
        yield client

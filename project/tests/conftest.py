import os
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.testclient import TestClient
from tortoise import Tortoise
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


async def ensure_user_exists_async(
    email: str, role: str, oid: str | None = None
) -> User:
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


async def setup_test_db_and_user(email: str, role: str, user_id: int):
    """Initialize Tortoise and create a test user, return the user."""
    db_url = os.environ.get("DATABASE_TEST_URL")
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["app.models.tortoise"]},
    )
    await Tortoise.generate_schemas()

    # Create the test user with a specific ID if possible
    oid = f"test-oid-{email}"
    user = await User.filter(azure_oid=oid).first()
    if not user:
        user = await User.create(
            azure_oid=oid,
            email=email,
            role=UserRole(role),
        )
    return user


async def cleanup_test_db():
    """Close Tortoise connections."""
    await Tortoise.close_connections()


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
    Creates a real user in the DB and mocks authentication to return that user."""
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

    with TestClient(app) as client:
        # Create the admin user via API registration endpoint first
        # Override to allow registration
        app.dependency_overrides[get_azure_user] = create_mock_azure_user_dependency(
            "admin@test.com", "admin", "test-oid-admin"
        )
        # Register the user
        response = client.post("/users/register")
        if response.status_code == 201:
            user_data = response.json()
            user_id = user_data["id"]
        elif response.status_code == 400:
            # User already exists, get their info via /users/me
            # We need to set up auth first
            app.dependency_overrides[get_current_user_from_azure] = (
                create_mock_current_user_dependency(1, "admin@test.com", "admin")
            )
            # Try to find the user - for now use ID 1 as fallback
            user_id = 1
        else:
            user_id = 1

        # Now override the dependency with the real user ID
        app.dependency_overrides[get_current_user_from_azure] = (
            create_mock_current_user_dependency(user_id, "admin@test.com", "admin")
        )
        yield client


@pytest.fixture
def test_app_with_writer():
    """Test app with writer user authentication.
    Creates a real user in the DB and mocks authentication to return that user."""
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

    with TestClient(app) as client:
        # Create the writer user via API registration endpoint
        app.dependency_overrides[get_azure_user] = create_mock_azure_user_dependency(
            "writer@test.com", "writer", "test-oid-writer"
        )
        response = client.post("/users/register")
        if response.status_code == 201:
            user_data = response.json()
            user_id = user_data["id"]
        else:
            user_id = 2  # Fallback

        # Now override the dependency with the real user ID
        app.dependency_overrides[get_current_user_from_azure] = (
            create_mock_current_user_dependency(user_id, "writer@test.com", "writer")
        )
        yield client


@pytest.fixture
def test_app_with_reader():
    """Test app with reader user authentication.
    Creates a real user in the DB and mocks authentication to return that user."""
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

    with TestClient(app) as client:
        # Create the reader user via API registration endpoint
        app.dependency_overrides[get_azure_user] = create_mock_azure_user_dependency(
            "reader@test.com", "reader", "test-oid-reader"
        )
        response = client.post("/users/register")
        if response.status_code == 201:
            user_data = response.json()
            user_id = user_data["id"]
        else:
            user_id = 3  # Fallback

        # Now override the dependency with the real user ID
        app.dependency_overrides[get_current_user_from_azure] = (
            create_mock_current_user_dependency(user_id, "reader@test.com", "reader")
        )
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

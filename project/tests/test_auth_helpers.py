"""
Helper functions for testing Azure AD authentication.
"""

from unittest.mock import MagicMock

from app.auth import get_azure_user


def create_mock_azure_user(email: str, role: str, oid: str | None = None):
    """
    Create a mock Azure user object that mimics what azure_scheme returns.

    Args:
        email: User email address
        role: Azure app role (admin, writer, reader)
        oid: Azure Object ID (auto-generated if not provided)

    Returns:
        MagicMock object with claims attribute
    """
    mock_user = MagicMock()
    mock_user.claims = {
        "preferred_username": email,
        "email": email,
        "oid": oid or f"test-oid-{email}",
        "roles": [role],  # Azure App Roles
    }
    return mock_user


def setup_test_user(app, email: str, role: str):
    """
    Setup authentication override for tests with a specific user.

    Args:
        app: FastAPI application instance
        email: User email address
        role: User role (admin, writer, reader)

    Returns:
        Modified app with dependency override
    """
    mock_user = create_mock_azure_user(email, role)

    async def mock_azure_user():
        return mock_user

    app.dependency_overrides[get_azure_user] = mock_azure_user
    return app

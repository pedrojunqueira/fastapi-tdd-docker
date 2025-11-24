"""
Simplified test configuration with dependency override for testing.
"""

from app.auth import get_current_user_from_azure
from app.models.pydantic import CurrentUserSchema
from app.models.tortoise import User, UserRole


def setup_test_user(app, email: str, role: str):
    """Setup authentication override for tests with a specific user."""

    async def mock_user():
        role_enum = UserRole(role)
        oid = f"test-oid-{email}"
        user, _created = await User.get_or_create(
            azure_oid=oid, defaults={"email": email, "role": role_enum}
        )
        return CurrentUserSchema(id=user.id, email=user.email, role=user.role.value)

    app.dependency_overrides[get_current_user_from_azure] = mock_user
    return app

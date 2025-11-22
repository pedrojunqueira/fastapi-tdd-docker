"""
Extended authentication testing endpoints for Azure JWT authentication.
These endpoints help you test the complete authentication flow with real Azure users.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth import get_current_user
from app.config import get_settings
from app.models.pydantic import CurrentUserSchema
from app.models.tortoise import User, UserRole

# Create router for extended auth testing
router = APIRouter(prefix="/auth/test", tags=["authentication-testing"])


class UserCreationResponse(BaseModel):
    """Response model for user creation testing."""

    user_id: int
    email: str
    role: str
    azure_oid: str | None
    created: bool
    message: str


class AuthTestResponse(BaseModel):
    """Response model for authentication testing."""

    authenticated: bool
    user: dict[str, Any]
    token_type: str
    permissions: dict[str, bool]


@router.get("/me", response_model=AuthTestResponse)
async def get_my_auth_info(current_user: CurrentUserSchema = Depends(get_current_user)):
    """
    Test endpoint: Get detailed information about the current authenticated user.
    This shows exactly what your app knows about the authenticated user.
    """
    settings = get_settings()

    # Get the full user record from database
    user_record = await User.get(id=current_user.id)

    # Test various permissions
    permissions = {
        "can_read": True,  # All authenticated users can read
        "can_write": current_user.role in ["writer", "admin"],
        "can_admin": current_user.role == "admin",
        "can_delete": current_user.role == "admin",
    }

    return AuthTestResponse(
        authenticated=True,
        user={
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "azure_oid": user_record.azure_oid,
            "created_at": user_record.created_at.isoformat()
            if user_record.created_at
            else None,
            "last_login": user_record.last_login.isoformat()
            if user_record.last_login
            else None,
        },
        token_type="mock" if settings.use_mock_auth else "azure_jwt",
        permissions=permissions,
    )


@router.post("/promote-to-admin")
async def promote_user_to_admin(
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """
    Test endpoint: Promote current user to admin (for testing purposes only).
    This is useful for testing authorization without configuring Azure roles.
    """
    settings = get_settings()

    # Only allow in development
    if settings.environment == "prod":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not available in production",
        )

    user_record = await User.get(id=current_user.id)
    user_record.role = UserRole.ADMIN
    await user_record.save()

    return {
        "message": f"User {current_user.email} promoted to admin",
        "new_role": "admin",
        "note": "You may need to get a new token for this change to take effect",
    }


@router.post("/change-role/{role}")
async def change_user_role(
    role: str,
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """
    Test endpoint: Change user role (for testing purposes only).
    Allows testing different authorization levels.
    """
    settings = get_settings()

    # Only allow in development
    if settings.environment == "prod":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not available in production",
        )

    # Validate role
    try:
        new_role = UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}",
        ) from None

    user_record = await User.get(id=current_user.id)
    old_role = user_record.role
    user_record.role = new_role
    await user_record.save()

    return {
        "message": f"User {current_user.email} role changed from {old_role} to {new_role}",
        "old_role": old_role.value,
        "new_role": new_role.value,
        "note": "You may need to get a new token for this change to take effect in Azure mode",
    }


@router.get("/users")
async def list_all_users(current_user: CurrentUserSchema = Depends(get_current_user)):
    """
    Test endpoint: List all users in the system.
    Only admins can access this endpoint.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can list users",
        )

    users = await User.all()
    return {
        "total_users": len(users),
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "azure_oid": user.azure_oid,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            for user in users
        ],
    }


@router.get("/test-authorization/{level}")
async def test_authorization_level(
    level: str, current_user: CurrentUserSchema = Depends(get_current_user)
):
    """
    Test endpoint: Test different authorization levels.

    Available levels:
    - reader: All authenticated users
    - writer: Writers and admins only
    - admin: Admins only
    """
    access_levels = {
        "reader": ["reader", "writer", "admin"],
        "writer": ["writer", "admin"],
        "admin": ["admin"],
    }

    if level not in access_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid level. Choose from: {list(access_levels.keys())}",
        )

    allowed_roles = access_levels[level]

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. This endpoint requires one of: {allowed_roles}. You have: {current_user.role}",
        )

    return {
        "message": f"✅ Access granted to {level} level endpoint",
        "your_role": current_user.role,
        "required_roles": allowed_roles,
        "endpoint": f"/auth/test/test-authorization/{level}",
    }

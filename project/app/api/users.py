"""
User management API endpoints.

Provides:
- Self-registration for authenticated Azure AD users
- Admin-only user management (list, view, update, delete)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.auth import (
    AzureUserClaims,
    get_admin_user,
    get_azure_claims_for_registration,
    register_user,
)
from app.models.pydantic import (
    CurrentUserSchema,
    UserListResponseSchema,
    UserResponseSchema,
    UserUpdateSchema,
)
from app.models.tortoise import User, UserRole

router = APIRouter()


@router.post("/register", response_model=UserResponseSchema, status_code=201)
async def register_new_user(
    claims: Annotated[AzureUserClaims, Depends(get_azure_claims_for_registration)],
) -> UserResponseSchema:
    """
    Register a new user in the application.

    - Requires Azure AD authentication (tenant users only)
    - New users are assigned the 'reader' role by default
    - Users can only register once
    """
    user = await register_user(claims)
    return UserResponseSchema(
        id=user.id,
        email=user.email,
        role=user.role.value,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.get("/", response_model=UserListResponseSchema)
async def list_users(
    _admin: Annotated[CurrentUserSchema, Depends(get_admin_user)],
) -> UserListResponseSchema:
    """
    List all registered users.

    - Admin only
    """
    users = await User.all()
    return UserListResponseSchema(
        users=[
            UserResponseSchema(
                id=user.id,
                email=user.email,
                role=user.role.value,
                created_at=user.created_at,
                last_login=user.last_login,
            )
            for user in users
        ],
        total=len(users),
    )


@router.get("/me", response_model=UserResponseSchema)
async def get_current_user_profile(
    claims: Annotated[AzureUserClaims, Depends(get_azure_claims_for_registration)],
) -> UserResponseSchema:
    """
    Get the current user's profile.

    - Any authenticated user (registered or not)
    - Returns user info if registered, 404 if not
    """
    user = await User.filter(azure_oid=claims.azure_oid).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not registered. Please register first at /users/register",
        )
    return UserResponseSchema(
        id=user.id,
        email=user.email,
        role=user.role.value,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(
    user_id: int,
    _admin: Annotated[CurrentUserSchema, Depends(get_admin_user)],
) -> UserResponseSchema:
    """
    Get a specific user by ID.

    - Admin only
    """
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponseSchema(
        id=user.id,
        email=user.email,
        role=user.role.value,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.put("/{user_id}", response_model=UserResponseSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdateSchema,
    _admin: Annotated[CurrentUserSchema, Depends(get_admin_user)],
) -> UserResponseSchema:
    """
    Update a user's role.

    - Admin only
    - Only role can be updated
    """
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update role
    try:
        user.role = UserRole(user_update.role)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(r.value for r in UserRole)}",
        ) from e

    await user.save()

    return UserResponseSchema(
        id=user.id,
        email=user.email,
        role=user.role.value,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    admin: Annotated[CurrentUserSchema, Depends(get_admin_user)],
) -> None:
    """
    Delete a user.

    - Admin only
    - Cannot delete yourself
    """
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await user.delete()

"""
Simplified authentication using fastapi-azure-auth library.
"""

import logging
from typing import Annotated

from fastapi import HTTPException, Security

from app.azure import azure_scheme
from app.models.pydantic import CurrentUserSchema
from app.models.tortoise import User, UserRole

logger = logging.getLogger(__name__)


async def get_current_user_from_azure(
    azure_user: Annotated[object, Security(azure_scheme)],
) -> CurrentUserSchema:
    """
    Get current user from Azure authentication.
    The azure_user parameter will be injected by azure_scheme via Security dependency.
    """
    if azure_user is None:
        # This should not happen in production, only if scheme not properly configured
        raise HTTPException(
            status_code=500, detail="Authentication scheme not configured"
        )  # Extract claims from Azure token
    claims = azure_user.claims

    email = claims.get("preferred_username") or claims.get("email") or claims.get("upn")
    if not email:
        raise HTTPException(status_code=401, detail="No email found in token")

    azure_oid = claims.get("oid")
    if not azure_oid:
        raise HTTPException(status_code=401, detail="No Azure Object ID found in token")

    # Map Azure roles to application roles
    user_role = _map_azure_roles_to_app_roles(claims)

    # Create or update user in database
    user, created = await User.get_or_create(
        azure_oid=azure_oid, defaults={"email": email, "role": user_role}
    )

    # Always update email and role from Azure token (role might have changed)
    if not created:
        needs_save = False
        if user.email != email:
            user.email = email
            needs_save = True
        if user.role != user_role:
            logger.info(f"Updating user role from {user.role} to {user_role}")
            user.role = user_role
            needs_save = True
        if needs_save:
            await user.save()

    logger.info(f"User authenticated: {email} (role: {user_role.value})")

    return CurrentUserSchema(id=user.id, email=user.email, role=user_role.value)


def _map_azure_roles_to_app_roles(claims: dict) -> UserRole:
    """Map Azure roles/groups to application roles."""
    roles = claims.get("roles", [])
    groups = claims.get("groups", [])

    logger.debug(f"Azure token roles: {roles}, groups: {groups}")

    # Define role mappings
    admin_roles = ["admin", "administrator", "fastapi.admin"]
    writer_roles = ["writer", "editor", "fastapi.writer"]

    admin_groups = ["fastapi-admins", "system-administrators"]
    writer_groups = ["fastapi-writers", "content-editors"]

    # Check for admin role
    if any(role.lower() in admin_roles for role in roles) or any(
        group in admin_groups for group in groups
    ):
        logger.info("User assigned admin role")
        return UserRole.ADMIN

    # Check for writer role
    if any(role.lower() in writer_roles for role in roles) or any(
        group in writer_groups for group in groups
    ):
        logger.info("User assigned writer role")
        return UserRole.WRITER

    # Default to reader
    logger.info("User assigned default reader role")
    return UserRole.READER


def require_roles(*allowed_roles: str):
    """
    Decorator to require specific roles for endpoint access.

    Usage:
        @require_roles("admin", "writer")
        async def create_summary(user: CurrentUserSchema = Depends(get_current_user_from_azure)):
            pass
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = None
            for _key, value in kwargs.items():
                if isinstance(value, CurrentUserSchema):
                    user = value
                    break

            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def require_ownership_or_admin(
    resource_user_id: int, current_user: CurrentUserSchema
) -> bool:
    """
    Check if user owns the resource or is an admin.

    Args:
        resource_user_id: The user_id of the resource owner
        current_user: The current authenticated user

    Returns:
        bool: True if user has access, raises HTTPException otherwise
    """
    if current_user.role == "admin" or current_user.id == resource_user_id:
        return True

    raise HTTPException(
        status_code=403, detail="Access denied. You can only access your own resources."
    )


# Role-based dependency functions for cleaner endpoint definitions


async def get_admin_user(
    current_user: Annotated[CurrentUserSchema, Security(azure_scheme)],
) -> CurrentUserSchema:
    """Dependency that requires admin role."""
    user = await get_current_user_from_azure(current_user)
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin role required.",
        )
    return user


async def get_writer_or_admin_user(
    current_user: Annotated[CurrentUserSchema, Security(azure_scheme)],
) -> CurrentUserSchema:
    """Dependency that requires writer or admin role."""
    user = await get_current_user_from_azure(current_user)
    if user.role not in ["writer", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Writer or Admin role required.",
        )
    return user


async def get_authenticated_user(
    current_user: Annotated[CurrentUserSchema, Security(azure_scheme)],
) -> CurrentUserSchema:
    """Dependency that requires any authenticated user (reader, writer, or admin)."""
    return await get_current_user_from_azure(current_user)

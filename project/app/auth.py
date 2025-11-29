"""
Authentication and authorization using fastapi-azure-auth library.

This module provides:
- Azure AD authentication via fastapi-azure-auth
- Role-based authorization (admin, writer, reader)
- User registration (self-service for tenant users)
- Testable dependency injection pattern

Users must be registered in the application before they can access protected endpoints.
Registration is open to any authenticated Azure AD user from the tenant.
"""

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Security

from app.azure import azure_scheme
from app.models.pydantic import CurrentUserSchema
from app.models.tortoise import User, UserRole

logger = logging.getLogger(__name__)


class AzureUserClaims:
    """Parsed Azure user claims from JWT token."""

    def __init__(self, claims: dict):
        self.email = (
            claims.get("preferred_username") or claims.get("email") or claims.get("upn")
        )
        self.azure_oid = claims.get("oid")
        self.name = claims.get("name")
        self.roles = claims.get("roles", [])
        self.groups = claims.get("groups", [])

    def is_valid(self) -> bool:
        """Check if required claims are present."""
        return bool(self.email and self.azure_oid)


async def get_azure_user(
    azure_user: Annotated[object, Security(azure_scheme)],
) -> object:
    """
    Get the raw Azure user from the token.
    This is a separate dependency to allow easy mocking in tests.
    """
    return azure_user


def parse_azure_claims(azure_user: object) -> AzureUserClaims:
    """Parse Azure user claims from the token."""
    if azure_user is None:
        raise HTTPException(
            status_code=500, detail="Authentication scheme not configured"
        )
    return AzureUserClaims(azure_user.claims)


async def get_current_user_from_azure(
    azure_user: Annotated[object, Depends(get_azure_user)],
) -> CurrentUserSchema:
    """
    Get current user from Azure authentication.
    User must already be registered in the application.
    """
    claims = parse_azure_claims(azure_user)

    if not claims.is_valid():
        raise HTTPException(
            status_code=401, detail="Invalid token: missing required claims"
        )

    # Look up user by Azure OID - must already exist
    user = await User.filter(azure_oid=claims.azure_oid).first()

    if not user:
        raise HTTPException(
            status_code=403,
            detail="User not registered. Please register first at /users/register",
        )

    # Update last login and email if changed
    needs_save = False
    if user.email != claims.email:
        user.email = claims.email
        needs_save = True
    user.last_login = datetime.now(UTC)
    needs_save = True

    if needs_save:
        await user.save()

    logger.info(f"User authenticated: {claims.email} (role: {user.role.value})")

    return CurrentUserSchema(id=user.id, email=user.email, role=user.role.value)


async def get_azure_claims_for_registration(
    azure_user: Annotated[object, Depends(get_azure_user)],
) -> AzureUserClaims:
    """
    Get Azure claims for user registration.
    Does not require user to be registered yet.
    """
    claims = parse_azure_claims(azure_user)

    if not claims.is_valid():
        raise HTTPException(
            status_code=401, detail="Invalid token: missing required claims"
        )

    return claims


async def register_user(claims: AzureUserClaims) -> User:
    """
    Register a new user from Azure claims.

    - The FIRST user to register becomes an admin (to bootstrap the system)
    - All subsequent users get the 'reader' role by default
    """
    # Check if user already exists
    existing_user = await User.filter(azure_oid=claims.azure_oid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")

    # Check if this is the first user - they become admin
    user_count = await User.all().count()
    if user_count == 0:
        role = UserRole.ADMIN
        logger.info(
            f"First user registration - assigning admin role to: {claims.email}"
        )
    else:
        role = UserRole.READER

    # Create new user
    user = await User.create(
        azure_oid=claims.azure_oid,
        email=claims.email,
        role=role,
        last_login=datetime.now(UTC),
    )

    logger.info(f"New user registered: {claims.email} with role: {role.value}")
    return user


def _map_azure_roles_to_app_roles(claims: dict) -> UserRole:
    """
    Map Azure roles/groups to application roles.
    NOTE: This is kept for reference but not used in current flow.
    Roles are managed within the application by admins, not from Azure.
    """
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
        return UserRole.ADMIN

    # Check for writer role
    if any(role.lower() in writer_roles for role in roles) or any(
        group in writer_groups for group in groups
    ):
        return UserRole.WRITER

    # Default to reader
    return UserRole.READER


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
    current_user: Annotated[CurrentUserSchema, Depends(get_current_user_from_azure)],
) -> CurrentUserSchema:
    """Dependency that requires admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin role required.",
        )
    return current_user


async def get_writer_or_admin_user(
    current_user: Annotated[CurrentUserSchema, Depends(get_current_user_from_azure)],
) -> CurrentUserSchema:
    """Dependency that requires writer or admin role."""
    if current_user.role not in ["writer", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Writer or Admin role required.",
        )
    return current_user


async def get_authenticated_user(
    current_user: Annotated[CurrentUserSchema, Depends(get_current_user_from_azure)],
) -> CurrentUserSchema:
    """Dependency that requires any authenticated user (reader, writer, or admin)."""
    return current_user

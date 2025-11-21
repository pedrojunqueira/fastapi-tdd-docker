"""
Authentication and authorization module.
Supports both mock authentication (development) and Azure JWT (production).
"""

import logging
from datetime import datetime, timedelta
from typing import Annotated, Any

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.models.pydantic import CurrentUserSchema
from app.models.tortoise import User, UserRole

# Setup logging
logger = logging.getLogger(__name__)

# JWT algorithm import for Azure token validation
try:
    from jwt.algorithms import RSAAlgorithm
except ImportError:
    RSAAlgorithm = None

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


class AzureJWTAuth:
    """Azure JWT authentication for production with enhanced caching and error handling."""

    def __init__(self):
        self.settings = get_settings()
        self._jwks_cache = None
        self._jwks_cache_expiry = None
        self._cache_ttl = timedelta(hours=24)  # JWKS cache for 24 hours

    def get_jwks_uri(self) -> str:
        """Get JWKS URI for Azure tenant."""
        if not self.settings.azure_tenant_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Azure tenant ID not configured"
            )
        return f"https://login.microsoftonline.com/{self.settings.azure_tenant_id}/discovery/v2.0/keys"

    async def get_jwks(self) -> dict[str, Any]:
        """Fetch JWKS from Azure with TTL-based caching."""
        now = datetime.utcnow()
        
        # Check if cache is valid
        if (self._jwks_cache is not None and 
            self._jwks_cache_expiry is not None and 
            now < self._jwks_cache_expiry):
            logger.debug("Using cached JWKS")
            return self._jwks_cache
            
        logger.info("Fetching JWKS from Azure")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.get_jwks_uri())
                response.raise_for_status()
                self._jwks_cache = response.json()
                self._jwks_cache_expiry = now + self._cache_ttl
                logger.info("JWKS cache updated successfully")
                return self._jwks_cache
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to fetch Azure JWKS"
            ) from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Azure JWKS endpoint returned error: {e.response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Azure authentication service unavailable"
            ) from e

    def get_public_key(self, token_header: dict[str, Any], jwks: dict[str, Any]) -> str:
        """Extract public key from JWKS for token validation."""
        kid = token_header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing 'kid' in header",
            )

        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # Convert JWKS key to PEM format
                if RSAAlgorithm is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="JWT RSA algorithm support not available",
                    )
                return RSAAlgorithm.from_jwk(key)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key",
        )

    async def validate_azure_jwt(self, token: str) -> dict[str, Any]:
        """Validate Azure JWT token and return claims."""
        try:
            # Decode header without verification to get kid
            unverified_header = jwt.get_unverified_header(token)

            # Get JWKS and find the right key
            jwks = await self.get_jwks()
            public_key = self.get_public_key(unverified_header, jwks)

            # Verify and decode the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[self.settings.jwt_algorithm],
                audience=self.settings.jwt_audience,
                issuer=f"https://login.microsoftonline.com/{self.settings.azure_tenant_id}/v2.0",
            )

            return payload

        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
            ) from e
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e!s}"
            ) from e

    async def get_user_from_azure_jwt(self, token: str) -> User:
        """Create or get user from Azure JWT claims."""
        claims = await self.validate_azure_jwt(token)

        # Extract user information from JWT claims
        email = (
            claims.get("preferred_username") or claims.get("email") or claims.get("upn")
        )
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No email found in token",
            )

        azure_oid = claims.get("oid")  # Azure Object ID
        if not azure_oid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No Azure Object ID found in token",
            )

        # Map Azure roles to our application roles
        user_role = self._map_azure_roles_to_app_roles(claims)

        # Create or update user in database
        user, created = await User.get_or_create(
            azure_oid=azure_oid, defaults={"email": email, "role": user_role}
        )

        # Update email if it changed
        if not created and user.email != email:
            user.email = email
            await user.save()

        return user

    def _map_azure_roles_to_app_roles(self, claims: dict[str, Any]) -> UserRole:
        """Map Azure roles/groups to application roles with enhanced logic."""
        # Check for roles in token (app roles assigned in Azure)
        roles = claims.get("roles", [])
        # Check for groups (security groups in Azure AD)
        groups = claims.get("groups", [])
        
        logger.debug(f"Azure roles: {roles}, groups: {groups}")
        
        # Priority order: Admin > Writer > Reader
        # App Roles (highest priority)
        if any(role.lower() in ["admin", "administrator", "fastapi.admin"] for role in roles):
            logger.info(f"User assigned admin role via app roles: {roles}")
            return UserRole.ADMIN
        if any(role.lower() in ["writer", "editor", "fastapi.writer"] for role in roles):
            logger.info(f"User assigned writer role via app roles: {roles}")
            return UserRole.WRITER
        if any(role.lower() in ["reader", "viewer", "fastapi.reader"] for role in roles):
            logger.info(f"User assigned reader role via app roles: {roles}")
            return UserRole.READER
            
        # Group-based mapping (can be configured based on your Azure AD setup)
        # You can replace these group IDs with your actual Azure AD group IDs
        admin_groups = [
            "fastapi-admins",
            "system-administrators", 
            # Add your Azure AD group IDs here
        ]
        writer_groups = [
            "fastapi-writers",
            "content-editors",
            # Add your Azure AD group IDs here
        ]
        reader_groups = [
            "fastapi-readers",
            "content-viewers",
            # Add your Azure AD group IDs here
        ]
        
        # Check group membership
        if any(group in admin_groups for group in groups):
            logger.info(f"User assigned admin role via group membership: {groups}")
            return UserRole.ADMIN
        if any(group in writer_groups for group in groups):
            logger.info(f"User assigned writer role via group membership: {groups}")
            return UserRole.WRITER
        if any(group in reader_groups for group in groups):
            logger.info(f"User assigned reader role via group membership: {groups}")
            return UserRole.READER
            
        # Default role for authenticated users
        logger.info("User assigned default reader role")
        return UserRole.READER


class MockAuth:
    """Mock authentication for development and testing."""

    @staticmethod
    async def create_test_user(email: str, role: UserRole = UserRole.READER) -> User:
        """Create or get a test user for development/testing."""
        user, _ = await User.get_or_create(email=email, defaults={"role": role})
        return user

    @staticmethod
    async def get_user_from_mock_token(token: str) -> User | None:
        """Extract user from mock token format: 'mock:email:role'"""
        if not token.startswith("mock:"):
            return None

        try:
            _, email, role = token.split(":")
            role_enum = UserRole(role)
            return await MockAuth.create_test_user(email, role_enum)
        except (ValueError, IndexError):
            return None


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> CurrentUserSchema:
    """
    Get the current authenticated user.
    Supports both mock authentication (development) and Azure JWT (production).
    """
    settings = get_settings()

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Choose authentication method based on configuration
    if settings.use_mock_auth:
        # Mock authentication for development
        user = await MockAuth.get_user_from_mock_token(credentials.credentials)
    else:
        # Azure JWT authentication for production
        azure_auth = AzureJWTAuth()
        user = await azure_auth.get_user_from_azure_jwt(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUserSchema(id=user.id, email=user.email, role=user.role.value)


def require_roles(*allowed_roles: str):
    """
    Decorator factory to require specific roles for endpoint access.

    Usage:
        @require_roles("admin", "writer")
        async def create_summary(user: CurrentUserSchema = Depends(get_current_user)):
            pass
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs (injected by FastAPI dependency)
            user = None
            for _key, value in kwargs.items():
                if isinstance(value, CurrentUserSchema):
                    user = value
                    break

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
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
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied. You can only access your own resources.",
    )

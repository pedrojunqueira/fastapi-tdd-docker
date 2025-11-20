"""
Authentication and authorization module.
Initially uses mock authentication, will be replaced with Azure JWT later.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.pydantic import CurrentUserSchema
from app.models.tortoise import User, UserRole

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


class MockAuth:
    """Mock authentication for development and testing.
    Will be replaced with Azure JWT validation later."""
    
    @staticmethod
    async def create_test_user(email: str, role: UserRole = UserRole.READER) -> User:
        """Create or get a test user for development/testing."""
        user, _ = await User.get_or_create(
            email=email,
            defaults={"role": role}
        )
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
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
) -> CurrentUserSchema:
    """
    Get the current authenticated user.
    Currently uses mock authentication, will be replaced with Azure JWT.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock authentication - will be replaced with Azure JWT validation
    user = await MockAuth.get_user_from_mock_token(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return CurrentUserSchema(
        id=user.id,
        email=user.email,
        role=user.role.value
    )


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
            for key, value in kwargs.items():
                if isinstance(value, CurrentUserSchema):
                    user = value
                    break
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def require_ownership_or_admin(
    resource_user_id: int,
    current_user: CurrentUserSchema
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
        detail="Access denied. You can only access your own resources."
    )

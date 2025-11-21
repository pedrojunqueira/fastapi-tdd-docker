"""Create Azure JWT validation endpoint for debugging and health checks."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.auth import AzureJWTAuth, get_settings

# Create router for Azure JWT validation endpoints
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


class TokenValidationResponse(BaseModel):
    """Response model for token validation."""
    valid: bool
    user_id: str | None = None
    email: str | None = None
    roles: list[str] = []
    claims: dict[str, Any] = {}
    error: str | None = None


class JWKSResponse(BaseModel):
    """Response model for JWKS endpoint."""
    keys: list[dict[str, Any]]
    cached: bool
    cache_expires: str | None = None


@router.get("/jwks", response_model=JWKSResponse)
async def get_jwks():
    """Get current JWKS (JSON Web Key Set) from Azure."""
    settings = get_settings()

    # Only allow in development or if explicitly enabled
    if not settings.use_mock_auth and not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not available in production"
        )

    azure_auth = AzureJWTAuth()
    try:
        jwks_data = await azure_auth.get_jwks()

        return JWKSResponse(
            keys=jwks_data.get("keys", []),
            cached=azure_auth._jwks_cache is not None,
            cache_expires=azure_auth._jwks_cache_expiry.isoformat() if azure_auth._jwks_cache_expiry else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching JWKS: {e!s}"
        ) from e


@router.post("/validate-token", response_model=TokenValidationResponse)
async def validate_azure_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Validate an Azure JWT token and return user information."""
    settings = get_settings()

    # Only allow in development or if explicitly enabled
    if not settings.use_mock_auth and not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not available in production"
        )

    azure_auth = AzureJWTAuth()

    try:
        # Validate the token
        claims = await azure_auth.validate_azure_jwt(credentials.credentials)

        return TokenValidationResponse(
            valid=True,
            user_id=claims.get("sub"),
            email=claims.get("email"),
            roles=claims.get("roles", []) + claims.get("groups", []),
            claims=claims
        )

    except HTTPException as e:
        return TokenValidationResponse(
            valid=False,
            error=f"HTTP {e.status_code}: {e.detail}"
        )
    except Exception as e:
        return TokenValidationResponse(
            valid=False,
            error=f"Validation error: {e!s}"
        )


@router.get("/health")
async def auth_health_check():
    """Health check for authentication system."""
    settings = get_settings()
    
    health_info = {
        "status": "healthy",
        "auth_mode": "mock" if settings.use_mock_auth else "azure_jwt",
        "azure_configured": bool(settings.azure_tenant_id and settings.azure_client_id),
        "timestamp": "2024-11-21T00:00:00Z"
    }
    
    # Test Azure JWT configuration if not in mock mode
    if not settings.use_mock_auth:
        try:
            azure_auth = AzureJWTAuth()
            jwks_uri = azure_auth.get_jwks_uri()
            health_info["jwks_uri"] = jwks_uri
            health_info["azure_tenant"] = settings.azure_tenant_id
        except Exception as e:
            health_info["status"] = "degraded"
            health_info["azure_error"] = str(e)
    
    return health_info

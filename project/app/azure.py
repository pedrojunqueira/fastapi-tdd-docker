"""Azure authentication scheme initialization."""

from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer

from app.config import get_settings

settings = get_settings()

# Initialize Azure authentication scheme
azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.app_client_id,
    tenant_id=settings.tenant_id,
    scopes=settings.scopes,
    allow_guest_users=False,  # Only allow users from this tenant
)

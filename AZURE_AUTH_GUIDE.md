# Azure Authentication with fastapi-azure-auth

This project now uses the [fastapi-azure-auth](https://intility.github.io/fastapi-azure-auth/) library for simplified Azure Entra ID authentication.

## Overview

The authentication system has been simplified significantly by using the fastapi-azure-auth package, which handles:

- JWT token validation
- OpenID Connect configuration
- Azure public key fetching and caching
- Swagger UI integration with OAuth2

## Azure Configuration Required

You need TWO app registrations in Azure Entra ID:

### 1. Backend API App Registration

1. Go to Azure Portal → Azure Active Directory → App registrations
2. Create new registration (e.g., "fastapi-tdd-auth")
3. **Supported account types**: Single tenant
4. Press Register
5. Note the **Application (Client) ID** and **Directory (tenant) ID**
6. Go to **Manifest** → Change `requestedAccessTokenVersion` from `null` to `2`
7. Go to **Expose an API** → Add scope:
   - Scope name: `user_impersonation`
   - Who can consent: Admins and users
   - Display names and descriptions as needed

### 2. OpenAPI Documentation App Registration

1. Create another app registration (e.g., "fastapi-tdd-auth - OpenAPI")
2. **Supported account types**: Single tenant
3. **Redirect URI**:
   - Type: Single-Page Application (SPA)
   - URL: `http://localhost:8004/oauth2-redirect`
4. Press Register
5. Note the **Application (Client) ID**
6. Go to **Manifest** → Change `requestedAccessTokenVersion` from `null` to `2`
7. Go to **API Permissions** → Add permission → My APIs → Select your backend API
8. Select the `user_impersonation` scope
9. Click "Add permissions"

### 3. Add Production Redirect URL (After Azure Deployment)

Once your app is deployed to Azure Container Apps, you need to add the production redirect URL:

1. Go to Azure Portal → Azure Active Directory → App registrations
2. Select your **OpenAPI Documentation App** (e.g., "fastapi-tdd-auth - OpenAPI")
3. Go to **Authentication** → **Single-page application** redirect URIs
4. Click **Add URI** and add your production URL:
   ```
   https://<your-container-app-name>.<environment>.<region>.azurecontainerapps.io/oauth2-redirect
   ```
   Example:
   ```
   https://ca-web-vspce2id5t2ik.graytree-6719a4b0.australiaeast.azurecontainerapps.io/oauth2-redirect
   ```
5. Click **Save**

> **Note**: You can find your Container App URL by running:
>
> ```bash
> az containerapp show --name <app-name> --resource-group <rg> --query "properties.configuration.ingress.fqdn" -o tsv
> ```

## Environment Configuration

Update your `.env` or `docker-compose.yml` with:

```bash
TENANT_ID=your-tenant-id
APP_CLIENT_ID=your-backend-app-client-id
OPENAPI_CLIENT_ID=your-openapi-client-id
BACKEND_CORS_ORIGINS=["http://localhost:8004"]
SCOPE_DESCRIPTION=user_impersonation
```

## Code Structure

### Main Components

- **app/config.py**: Settings with Azure configuration and computed fields for scopes
- **app/main.py**: FastAPI application with Azure authentication scheme initialization
- **app/auth.py**: User mapping from Azure JWT to application users
- **app/api/summaries.py**: Protected endpoints using `get_current_user_from_azure` dependency

### Authentication Flow

1. User authenticates via Swagger UI OAuth2 flow
2. Azure returns JWT token with user claims
3. `fastapi-azure-auth` validates token signature and claims
4. `get_current_user_from_azure` extracts user info and maps roles
5. User is created/updated in database with Azure OID as unique identifier
6. Request proceeds with authenticated user context

### Role Mapping

Azure roles/groups are mapped to application roles:

- **Admin**: `admin`, `administrator`, `fastapi.admin` roles OR `fastapi-admins`, `system-administrators` groups
- **Writer**: `writer`, `editor`, `fastapi.writer` roles OR `fastapi-writers`, `content-editors` groups
- **Reader**: Default role for any authenticated user

## Testing

Tests use dependency override to inject mock users:

```python
from app.auth import get_current_user_from_azure
from app.models.pydantic import CurrentUserSchema
from app.models.tortoise import User, UserRole

def create_mock_user_dependency(email: str, role: str):
    async def _mock_user():
        role_enum = UserRole(role)
        oid = f"test-oid-{email}"
        user, _ = await User.get_or_create(
            azure_oid=oid,
            defaults={"email": email, "role": role_enum}
        )
        return CurrentUserSchema(id=user.id, email=user.email, role=user.role.value)
    return _mock_user

# In test
app.dependency_overrides[get_current_user_from_azure] = create_mock_user_dependency("test@example.com", "admin")
```

## API Usage

### Using Swagger UI

1. Navigate to http://localhost:8004/docs
2. Click "Authorize" button
3. Check the `user_impersonation` scope
4. Click "Authorize" and log in with your Azure account
5. Try protected endpoints

### Using cURL with Token

```bash
# Get token from Azure (you'll need to do this via browser OAuth flow)
TOKEN="your-jwt-token"

# Use the token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8004/summaries/
```

## Differences from Previous Implementation

### Removed

- Custom JWT validation logic
- Manual JWKS fetching and caching
- Mock authentication mode
- `auth_validation.py` and `auth_testing.py` endpoints
- Complex test authentication helpers

### Added

- `fastapi-azure-auth` package dependency
- Simplified configuration via Settings class
- OpenAPI OAuth2 integration
- Cleaner separation of concerns

### Simplified

- Authentication is now a simple dependency injection
- Azure configuration is declarative
- Testing uses FastAPI's built-in dependency override
- Role mapping is centralized in one function

## Troubleshooting

### "Unable to fetch provider information"

- Check that `TENANT_ID` is correctly set
- Verify network connectivity to Azure endpoints

### "Invalid token"

- Ensure token is from the correct tenant
- Check that `APP_CLIENT_ID` matches your backend app registration
- Verify token hasn't expired
- Confirm `requestedAccessTokenVersion` is set to `2` in Azure

### Swagger UI redirect issues

- Use `localhost` not `127.0.0.1`
- Ensure redirect URI in Azure matches exactly: `http://localhost:8004/oauth2-redirect`
- Check CORS settings in `BACKEND_CORS_ORIGINS`

### Role mapping not working

- Check that Azure app roles are assigned to users in Azure Portal
- Verify group membership if using group-based roles
- Review logs to see what roles/groups are in the token

## Resources

- [fastapi-azure-auth Documentation](https://intility.github.io/fastapi-azure-auth/)
- [Azure App Registrations](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps)
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/)

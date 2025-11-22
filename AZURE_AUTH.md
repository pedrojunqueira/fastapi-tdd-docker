# Azure JWT Authentication Setup

This application supports hybrid authentication:

- **Mock Authentication** for development and testing
- **Azure JWT Authentication** for production environments

## Configuration

The authentication mode is controlled by environment variables:

### Environment Variables

```bash
# Authentication Mode
USE_MOCK_AUTH=true          # Set to 'false' for Azure JWT in production

# Azure Entra ID Configuration (required for production)
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
JWT_ALGORITHM=RS256
JWT_AUDIENCE=your-client-id-here  # Usually same as client_id
```

## Development Setup (Mock Authentication)

For development, mock authentication is enabled by default:

```bash
USE_MOCK_AUTH=true
```

### Mock Token Format

Mock tokens follow this format: `mock:email:role`

Example mock tokens:

```bash
# Admin user
Authorization: Bearer mock:admin@test.com:admin

# Writer user
Authorization: Bearer mock:writer@test.com:writer

# Reader user
Authorization: Bearer mock:reader@test.com:reader
```

## Production Setup (Azure JWT)

### Step 1: Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Configure your app:
   - **Name**: Your FastAPI App
   - **Supported account types**: Choose appropriate option
   - **Redirect URI**: Configure as needed for your frontend

### Step 2: Configure App Roles

1. In your app registration, go to **App roles**
2. Create the following roles:
   - **Admin**: Full access to all resources
   - **Writer**: Can create and manage own content
   - **Reader**: Read-only access

### Step 3: Environment Configuration

Set the following environment variables:

```bash
# Disable mock authentication
USE_MOCK_AUTH=false

# Azure configuration
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-app-client-id
JWT_ALGORITHM=RS256
JWT_AUDIENCE=your-app-client-id
```

### Step 4: Token Acquisition

Your frontend application needs to acquire JWT tokens from Azure Entra ID using one of these flows:

- **Authorization Code Flow** (recommended for web apps)
- **Client Credentials Flow** (for service-to-service)
- **On-Behalf-Of Flow** (for API chaining)

## Role Mapping

The application maps Azure roles to internal roles:

| Azure Role | Application Role | Permissions             |
| ---------- | ---------------- | ----------------------- |
| Admin      | admin            | Full access             |
| Writer     | writer           | Create/edit own content |
| Reader     | reader           | Read-only access        |

## Security Features

- **JWT Signature Verification**: Uses Azure's JWKS endpoint
- **Token Expiration**: Respects Azure JWT expiration times
- **Audience Validation**: Ensures tokens are for this application
- **Issuer Validation**: Validates tokens come from your Azure tenant
- **Role-Based Access Control**: Enforces permissions at endpoint level
- **User Ownership**: Users can only modify their own resources (except admins)

## Testing

### Mock Authentication Tests

```bash
# Run tests with mock authentication (default)
docker-compose exec web python -m pytest tests/test_auth.py -v
```

### Azure JWT Testing

For testing Azure JWT integration, you'll need:

1. Valid Azure JWT tokens
2. Configured Azure app registration
3. Environment variables set for production mode

## Troubleshooting

### Common Issues

1. **Import errors for jwt libraries**:

   ```bash
   # Install missing dependencies
   docker-compose exec web uv pip install pyjwt[crypto] cryptography python-jose[cryptography]
   ```

2. **Invalid JWT token**:

   - Check token expiration
   - Verify audience matches your client_id
   - Ensure issuer matches your tenant

3. **Role mapping issues**:
   - Verify roles are assigned in Azure app registration
   - Check role claims in JWT token
   - Review role mapping logic in `_map_azure_roles_to_app_roles()`

### Debug Mode

Enable debug logging to troubleshoot authentication issues:

```python
import logging
logging.getLogger("app.auth").setLevel(logging.DEBUG)
```

## Migration Guide

### From Mock to Azure JWT

1. Update environment variables
2. Configure Azure app registration
3. Update frontend to use Azure authentication
4. Test with actual Azure JWT tokens
5. Deploy to production

The hybrid authentication system allows seamless transition between development and production environments without code changes.

# 🧪 Azure Authentication Testing Guide

This guide shows you how to test your FastAPI application with **real Azure users** and understand the complete authentication and authorization flow.

## 🎯 What You'll Learn

1. How users are **automatically created** in your app when they first authenticate
2. How **Azure roles/groups** map to your application roles
3. How to test **different authorization levels**
4. How to troubleshoot authentication issues

## 🚀 Quick Start

### Step 1: Switch to Azure JWT Mode

1. Edit `docker-compose.yml`:

   ```yaml
   - USE_MOCK_AUTH=false # Change from true to false
   ```

2. Restart containers:
   ```bash
   docker compose restart
   ```

### Step 2: Get a Real Azure Token

Choose one of these methods:

#### Option A: Azure CLI (Recommended)

```bash
# Install Azure CLI if you haven't: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
az login
az account get-access-token --resource 70050862-5a60-4865-b3b5-4bbf913e4ca9
```

#### Option B: Browser-based OAuth (Manual)

1. Open this URL in your browser:
   ```
   https://login.microsoftonline.com/078c6c18-7434-4931-81cd-7b9603fda5a2/oauth2/v2.0/authorize?client_id=70050862-5a60-4865-b3b5-4bbf913e4ca9&response_type=token&redirect_uri=http://localhost:8000&scope=70050862-5a60-4865-b3b5-4bbf913e4ca9/.default&response_mode=fragment
   ```
2. Login with your Azure account
3. Extract the `access_token` from the URL fragment

### Step 3: Test Authentication

#### A. Using FastAPI Swagger UI

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_TOKEN_HERE`
4. Try the `/auth/test/me` endpoint

#### B. Using curl

```bash
curl -X GET "http://localhost:8000/auth/test/me" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🔍 Testing Endpoints

Your app now has several testing endpoints:

### 1. Get Your Auth Info

```http
GET /auth/test/me
```

Shows everything your app knows about you:

- User ID and email
- Current role (admin/writer/reader)
- Azure Object ID
- Permissions

### 2. Test Authorization Levels

```http
GET /auth/test/test-authorization/reader   # All users
GET /auth/test/test-authorization/writer   # Writers and admins only
GET /auth/test/test-authorization/admin    # Admins only
```

### 3. Change Your Role (Development Only)

```http
POST /auth/test/change-role/admin
POST /auth/test/change-role/writer
POST /auth/test/change-role/reader
```

### 4. List All Users (Admin Only)

```http
GET /auth/test/users
```

## 📊 Understanding User Creation

When you first authenticate with Azure, your app automatically:

1. **Validates your JWT token** against Azure's public keys
2. **Extracts user information**:

   - Email (from `preferred_username`, `email`, or `upn` claims)
   - Azure Object ID (from `oid` claim - this is your unique identifier)
   - Roles/Groups (from `roles` and `groups` claims)

3. **Maps Azure roles to app roles**:

   - Azure roles: `admin`, `administrator`, `fastapi.admin` → **Admin**
   - Azure roles: `writer`, `editor`, `fastapi.writer` → **Writer**
   - Azure groups: `fastapi-admins`, `system-administrators` → **Admin**
   - Default: **Reader**

4. **Creates/updates user in database**:
   ```sql
   INSERT INTO user (azure_oid, email, role) VALUES (?, ?, ?)
   ON CONFLICT(azure_oid) DO UPDATE SET email = ?, role = ?
   ```

## 🛠️ Troubleshooting

### Problem: "Invalid token" error

**Solution**: Check these endpoints:

```bash
# Test JWKS connectivity
curl http://localhost:8000/auth/jwks

# Validate your token
curl -X POST "http://localhost:8000/auth/validate-token" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Problem: "Access denied" for authorization

**Cause**: Your user doesn't have the required role.
**Solutions**:

1. **Development**: Use `/auth/test/change-role/admin` to promote yourself
2. **Production**: Configure Azure app roles or add user to appropriate Azure AD groups

### Problem: User not being created

**Check**: The `/auth/test/me` endpoint shows exactly what's happening with user creation.

## 🔐 Role Assignment Options

You have multiple ways to assign roles:

### Option 1: Azure App Roles (Recommended)

1. Go to Azure Portal → App Registrations → Your App
2. Add app roles: `admin`, `writer`, `reader`
3. Assign users to roles

### Option 2: Azure AD Groups

1. Create groups: `fastapi-admins`, `fastapi-writers`, `fastapi-readers`
2. Add users to groups
3. Configure group claims in your Azure app

### Option 3: Development Override

Use the test endpoints to temporarily change roles for testing.

## 📝 Example Test Flow

```bash
# 1. Get token
TOKEN=$(az account get-access-token --resource 70050862-5a60-4865-b3b5-4bbf913e4ca9 --query accessToken -o tsv)

# 2. Check your user info
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/test/me

# 3. Test reader access (should work)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/test/test-authorization/reader

# 4. Test admin access (might fail)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/test/test-authorization/admin

# 5. Promote yourself to admin (development only)
curl -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/test/promote-to-admin

# 6. Test admin access again (should work now in mock mode, need new token in Azure mode)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/test/test-authorization/admin
```

## 🎉 Success!

If everything works, you should see:

- Your user automatically created in the database
- Proper role assignment based on Azure configuration
- Authorization working correctly for different endpoints
- Clear error messages when access is denied

This confirms your 2-tier authentication system is working perfectly! 🚀

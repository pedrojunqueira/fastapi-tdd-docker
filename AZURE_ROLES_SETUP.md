# Azure AD App Roles Setup Guide

This guide shows you how to configure the three roles (Admin, Writer, Reader) in your Azure AD app registration and assign them to users for testing.

## Step 1: Add App Roles to Backend API App Registration

1. **Go to Azure Portal** → Azure Active Directory → App registrations
2. **Find your Backend API app**: `ab2eb96c-e97e-422f-a405-adbf8a1c0c66`
3. **Click on "App roles"** in the left menu
4. **Click "+ Create app role"** and add each role:

### Admin Role

- **Display name**: `Admin`
- **Allowed member types**: `Users/Groups`
- **Value**: `admin` (lowercase, must match code exactly)
- **Description**: `Full administrative access - can create, read, update, delete all summaries and manage users`
- **Enable this app role**: ✅ Checked
- Click **Apply**

### Writer Role

- **Display name**: `Writer`
- **Allowed member types**: `Users/Groups`
- **Value**: `writer` (lowercase, must match code exactly)
- **Description**: `Can create, read, update, and delete their own summaries`
- **Enable this app role**: ✅ Checked
- Click **Apply**

### Reader Role

- **Display name**: `Reader`
- **Allowed member types**: `Users/Groups`
- **Value**: `reader` (lowercase, must match code exactly)
- **Description**: `Read-only access - can only view summaries`
- **Enable this app role**: ✅ Checked
- Click **Apply**

## Step 2: Assign Roles to Users

Now you need to assign these roles to users for testing.

### Option A: Via Enterprise Applications (Recommended for Testing)

1. **Go to**: Azure Portal → Azure Active Directory → **Enterprise applications**
2. **Search for your Backend API app** by name or client ID: `ab2eb96c-e97e-422f-a405-adbf8a1c0c66`
3. **Click on** "Users and groups" in the left menu
4. **Click** "+ Add user/group"
5. **Select the user** you want to assign a role to
6. **Click** "Select a role"
7. **Choose** Admin, Writer, or Reader
8. **Click** "Assign"

**Repeat this for different test users with different roles.**

### Option B: Via App Registrations (Alternative)

1. Go to your Backend API app registration
2. Click "Managed application in local directory" link
3. Follow steps 3-8 from Option A above

## Step 3: Configure Token to Include Roles

The roles will be automatically included in the JWT token as a `roles` claim. Make sure your app registration is configured correctly:

1. **Go to**: Backend API App Registration → **Token configuration**
2. **Verify** that "roles" claim is included (it should be by default)
3. If not present, click "+ Add optional claim"
   - Token type: **Access**
   - Claim: **roles**
   - Click **Add**

## Step 4: Test the Roles

### Testing in Swagger UI

1. **Open Swagger UI**: http://localhost:8004/docs
2. **Click "Authorize"**
3. **Login with different users** to test different roles

### Expected Behavior:

#### Reader Role

- ✅ Can GET /summaries/ (see only their own)
- ✅ Can GET /summaries/{id}/ (only their own)
- ❌ Cannot POST /summaries/ (403 Forbidden)
- ❌ Cannot PUT /summaries/{id}/ (403 Forbidden)
- ❌ Cannot DELETE /summaries/{id}/ (403 Forbidden)

#### Writer Role

- ✅ Can GET /summaries/ (see only their own)
- ✅ Can GET /summaries/{id}/ (only their own)
- ✅ Can POST /summaries/ (create new)
- ✅ Can PUT /summaries/{id}/ (only their own)
- ✅ Can DELETE /summaries/{id}/ (only their own)
- ❌ Cannot see/modify other users' summaries (unless admin)

#### Admin Role

- ✅ Can GET /summaries/ (sees ALL summaries)
- ✅ Can GET /summaries/{id}/ (any summary)
- ✅ Can POST /summaries/
- ✅ Can PUT /summaries/{id}/ (any summary)
- ✅ Can DELETE /summaries/{id}/ (any summary)
- ✅ Full access to all resources

## Step 5: Verify Token Claims

To verify that roles are being sent in the token, you can:

1. **Login via Swagger UI**
2. **Check the application logs**:
   ```bash
   docker compose logs web | grep "Azure roles"
   ```
   You should see lines like:
   ```
   DEBUG Azure roles: ['admin'], groups: []
   INFO User assigned admin role
   ```

### Decode the JWT Token (Optional)

1. After authenticating in Swagger UI, open browser DevTools (F12)
2. Go to Network tab
3. Find a request to your API
4. Copy the Authorization header value (the token after "Bearer ")
5. Go to https://jwt.ms/ or https://jwt.io/
6. Paste the token
7. Look for the `roles` claim in the payload:
   ```json
   {
     "aud": "ab2eb96c-e97e-422f-a405-adbf8a1c0c66",
     "oid": "user-object-id",
     "email": "user@example.com",
     "roles": ["admin"],
     ...
   }
   ```

## Role Mapping Logic

The application maps Azure roles to app roles in `app/auth.py`:

```python
def _map_azure_roles_to_app_roles(claims: dict) -> UserRole:
    roles = claims.get("roles", [])  # App roles you configured
    groups = claims.get("groups", [])  # Azure AD groups (optional)

    # Admin roles
    if any(role.lower() in ["admin", "administrator", "fastapi.admin"] for role in roles):
        return UserRole.ADMIN

    # Writer roles
    if any(role.lower() in ["writer", "editor", "fastapi.writer"] for role in roles):
        return UserRole.WRITER

    # Default: Reader
    return UserRole.READER
```

**Important**: The role value you configured in Azure (`admin`, `writer`, `reader`) must match exactly (case-insensitive).

## Troubleshooting

### Roles not appearing in token?

- Make sure you assigned the role in **Enterprise Applications** → **Users and groups**
- Logout and login again to get a fresh token
- Check Token configuration in app registration

### User still has wrong role?

- Check the application logs for role mapping debug info
- Verify the `roles` claim in the JWT token
- Make sure the role value matches exactly (`admin`, `writer`, `reader`)

### 403 Forbidden errors?

- Check user's role in database: `docker compose exec web-db psql -U postgres -d web_dev -c "SELECT email, role FROM user;"`
- The role is set when user first authenticates - may need to delete user from DB and re-authenticate to pick up new Azure role

### Force role update for existing user:

```sql
-- Connect to database
docker compose exec web-db psql -U postgres -d web_dev

-- Update user role manually
UPDATE "user" SET role = 'admin' WHERE email = 'your.email@example.com';

-- Check updated roles
SELECT email, role FROM "user";
```

## Testing Checklist

- [ ] Created 3 app roles in Backend API app registration (admin, writer, reader)
- [ ] Assigned admin role to test user 1
- [ ] Assigned writer role to test user 2
- [ ] Assigned reader role to test user 3 (or use default)
- [ ] Tested admin user can access all endpoints
- [ ] Tested writer can create/update/delete their own summaries
- [ ] Tested reader can only view summaries (gets 403 on POST/PUT/DELETE)
- [ ] Verified roles appear in JWT token
- [ ] Checked application logs show correct role assignment

## Next Steps

Once roles are working, you can:

1. Add user management endpoints (admin only)
2. Add group-based role assignment
3. Implement more granular permissions
4. Add audit logging for role-based actions
5. Remove `allow_guest_users=True` to restrict to tenant users only

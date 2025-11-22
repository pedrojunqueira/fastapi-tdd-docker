# 🎯 Azure Authentication - Working Solution

Since Azure CLI is having consent issues, here are **working alternatives** to get your Azure JWT token:

## 🌐 **Method 1: Browser-Based Token (Easiest)**

### Step 1: Fix Azure App Registration

1. Go to **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Find your app: **fastapi-tdd-auth** (70050862-5a60-4865-b3b5-4bbf913e4ca9)
3. Go to **Authentication** → **Platform configurations**
4. Click **+ Add a platform** → **Single-page application (SPA)**
5. Add redirect URI: `http://localhost:8004/auth/callback`
6. Click **Configure**

### Step 2: Get Token via Browser

Open this URL in your browser:

```
https://login.microsoftonline.com/078c6c18-7434-4931-81cd-7b9603fda5a2/oauth2/v2.0/authorize?client_id=70050862-5a60-4865-b3b5-4bbf913e4ca9&response_type=token&redirect_uri=http://localhost:8004/auth/callback&scope=openid%20profile%20email&response_mode=fragment
```

After login, you'll be redirected to a URL like:

```
http://localhost:8004/auth/callback#access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6...&token_type=Bearer&expires_in=3599
```

Copy the `access_token` value.

## 🔧 **Method 2: Fix Azure CLI Consent**

### Option A: Admin Consent

1. In Azure Portal, go to your app registration
2. Go to **API permissions**
3. Click **Grant admin consent for [Your Tenant]**

### Option B: Add Redirect URI for Azure CLI

1. In **Authentication** → **Redirect URIs**
2. Add: `http://localhost`
3. Save

Then retry:

```bash
az login --tenant "078c6c18-7434-4931-81cd-7b9603fda5a2"
az account get-access-token --resource 70050862-5a60-4865-b3b5-4bbf913e4ca9
```

## 🧪 **Method 3: Use Postman/Insomnia**

1. **POST** to: `https://login.microsoftonline.com/078c6c18-7434-4931-81cd-7b9603fda5a2/oauth2/v2.0/token`
2. **Body** (form-encoded):
   ```
   grant_type=client_credentials
   client_id=70050862-5a60-4865-b3b5-4bbf913e4ca9
   client_secret=YOUR_CLIENT_SECRET
   scope=https://graph.microsoft.com/.default
   ```

## ✅ **Test Your Token**

Once you have a token, test it with:

```bash
# Switch to Azure mode
export USE_MOCK_AUTH=false

# Test token validation
curl -X POST "http://localhost:8004/auth/validate-token" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Test user creation
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://localhost:8004/auth/test/me

# Test authorization
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://localhost:8004/auth/test/test-authorization/admin
```

## 🎯 **Expected Results**

When working correctly, you should see:

1. ✅ Token validates successfully
2. 👤 User automatically created in database with Azure OID
3. 🎭 Role assigned based on your Azure roles/groups
4. 🔐 Authorization working for different endpoints

The fastest path is **Method 1** - just add the SPA platform configuration in Azure Portal and use the browser URL!

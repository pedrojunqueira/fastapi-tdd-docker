# Deployment Guide

This project supports two deployment environments:

1. **Development** - Manual deployment using `azd up` (local CLI)
2. **Production** - Automated deployment via GitHub Actions CI/CD

---

## Prerequisites

### Azure AD App Registrations (One-time Setup)

You need **two** app registrations in Azure Entra ID:

#### Backend API App Registration

1. Go to **Azure Portal** → **Microsoft Entra ID** → **App registrations** → **New registration**
2. Name: `summaries-api` (or your choice)
3. Supported account types: **Single tenant**
4. Click **Register**
5. Note the **Application (client) ID** → This is your `AZURE_API_CLIENT_ID`
6. Go to **Expose an API**:
   - Click **Add** next to Application ID URI → accept default `api://<client-id>`
   - Click **Add a scope**:
     - Scope name: `user_impersonation`
     - Who can consent: **Admins and users**
     - Admin consent display name: `Access Summaries API`
     - State: **Enabled**

#### Frontend SPA App Registration

1. Go to **App registrations** → **New registration**
2. Name: `summaries-frontend` (or your choice)
3. Supported account types: **Single tenant**
4. Redirect URI: Select **Single-page application (SPA)** → `http://localhost:3000`
5. Click **Register**
6. Note the **Application (client) ID** → This is your `AZURE_CLIENT_ID`
7. Go to **API permissions** → **Add a permission**:
   - Select **My APIs** → `summaries-api`
   - Check `user_impersonation`
   - Click **Add permissions**
   - Click **Grant admin consent**

#### Note Your IDs

| Variable              | Description            | Where to find                 |
| --------------------- | ---------------------- | ----------------------------- |
| `AZURE_TENANT_ID`     | Directory (tenant) ID  | Any app registration overview |
| `AZURE_CLIENT_ID`     | Frontend SPA client ID | Frontend app registration     |
| `AZURE_API_CLIENT_ID` | Backend API client ID  | Backend app registration      |

---

## Option 1: Development Deployment (Manual)

Use this for initial infrastructure setup and testing.

### Step 1: Configure azd Environment

```bash
# Login to Azure
az login
azd auth login

# Create/select environment
azd env new dev
azd env select dev

# Set required variables
azd env set AZURE_CLIENT_ID "<frontend-spa-client-id>"
azd env set AZURE_TENANT_ID "<your-tenant-id>"
azd env set AZURE_API_CLIENT_ID "<backend-api-client-id>"
```

### Step 2: Deploy

```bash
azd up
```

This will:

1. Create Azure Container Apps Environment
2. Deploy PostgreSQL database container
3. Deploy FastAPI backend (with Azure AD env vars from Bicep)
4. Deploy React frontend
5. Auto-redeploy frontend with correct URLs (via postprovision hook)
6. Run database migrations automatically

### Step 3: Add Redirect URI

After deployment, add the frontend URL to the SPA app registration:

1. Go to **Azure Portal** → **App registrations** → **summaries-frontend**
2. Go to **Authentication** → **Single-page application**
3. Add redirect URI: `https://ca-frontend-xxxxx.region.azurecontainerapps.io/`
4. Click **Save**

---

## Option 2: Production Deployment (CI/CD)

The CI/CD pipeline automatically deploys to production when code is pushed to `master`.

### Step 1: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name                   | Value                       | Description                            |
| ----------------------------- | --------------------------- | -------------------------------------- |
| `AZURE_CLIENT_ID`             | Service Principal client ID | For Azure authentication               |
| `AZURE_CLIENT_SECRET`         | Service Principal secret    | For Azure authentication               |
| `AZURE_TENANT_ID`             | Azure AD tenant ID          | For Azure authentication               |
| `AZURE_SUBSCRIPTION_ID`       | Azure subscription ID       | Target subscription                    |
| `AZURE_AD_FRONTEND_CLIENT_ID` | Frontend SPA client ID      | Same as `AZURE_CLIENT_ID` from app reg |
| `AZURE_AD_TENANT_ID`          | Azure AD tenant ID          | For frontend auth config               |
| `AZURE_AD_API_CLIENT_ID`      | Backend API client ID       | For frontend auth config               |

> **Note:** `AZURE_CLIENT_ID`/`AZURE_CLIENT_SECRET` are for the **Service Principal** (CI/CD auth).
> `AZURE_AD_*` secrets are for the **App Registrations** (user auth).

### Step 2: Create Service Principal (if not exists)

```bash
az ad sp create-for-rbac --name "github-actions-sp" --role contributor \
  --scopes /subscriptions/<subscription-id> \
  --sdk-auth
```

Use the output values for `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`.

### Step 3: Push to Master

```bash
git add .
git commit -m "Deploy to production"
git push origin master
```

The CI/CD pipeline will:

1. Run tests
2. Run code quality checks
3. Run security scans
4. Build Docker images
5. Deploy to Azure with `azd up`
6. Auto-redeploy frontend with correct Azure AD config

### Step 4: Add Production Redirect URI

After the first successful deployment, add the production frontend URL:

1. Go to **Azure Portal** → **App registrations** → **summaries-frontend**
2. Go to **Authentication** → **Single-page application**
3. Add redirect URI: `https://ca-frontend-xxxxx.region.azurecontainerapps.io/`
4. Click **Save**

---

## Environment Variables Reference

### Backend (set automatically via Bicep)

| Variable               | Description                          |
| ---------------------- | ------------------------------------ |
| `DATABASE_URL`         | PostgreSQL connection string         |
| `ENVIRONMENT`          | `production`                         |
| `TENANT_ID`            | Azure AD tenant ID                   |
| `APP_CLIENT_ID`        | Backend API client ID                |
| `OPENAPI_CLIENT_ID`    | Frontend SPA client ID (for Swagger) |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins                 |

### Frontend (set at build time via Docker build args)

| Variable               | Description            |
| ---------------------- | ---------------------- |
| `VITE_AZURE_CLIENT_ID` | Frontend SPA client ID |
| `VITE_AZURE_TENANT_ID` | Azure AD tenant ID     |
| `VITE_API_CLIENT_ID`   | Backend API client ID  |
| `VITE_REDIRECT_URI`    | Frontend URL           |
| `VITE_API_BASE_URL`    | Backend API URL        |

---

## Useful Commands

```bash
# View deployed resources
az containerapp list --output table

# Check backend logs
az containerapp logs show --name ca-web-<suffix> -g <rg-name> --type console --tail 100

# Redeploy specific service
azd deploy web
azd deploy frontend

# Tear down all resources
azd down

# Switch environments
azd env select dev
azd env select production
```

---

## Troubleshooting

### `api://` empty error

The frontend wasn't built with `VITE_API_CLIENT_ID`. Ensure:

- `AZURE_API_CLIENT_ID` is set in azd environment
- Redeploy frontend: `azd deploy frontend`

### Backend missing Azure AD config

Check Bicep deployed the env vars:

```bash
az containerapp show --name ca-web-<suffix> -g <rg-name> --query "properties.template.containers[0].env"
```

### Authentication redirect error

Ensure the exact frontend URL (with trailing slash) is in the SPA redirect URIs.

### Database tables not created

Migrations should run automatically. If not:

```bash
az containerapp exec --name ca-web-<suffix> -g <rg-name> --command ".venv/bin/aerich upgrade"
```

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React SPA     │────▶│  FastAPI API    │────▶│   PostgreSQL    │
│   (Frontend)    │     │   (Backend)     │     │   (Database)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
        ┌─────────────────────┐
        │   Azure Entra ID    │
        │   (Authentication)  │
        └─────────────────────┘
```

All services run as **Azure Container Apps** in a shared environment.

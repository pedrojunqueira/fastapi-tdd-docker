# Summaries Frontend

A React/TypeScript SPA for the Summaries API with Azure AD authentication.

## Features

- **Azure AD Authentication** using MSAL (Microsoft Authentication Library)
- **Role-based access control**:
  - **Reader**: Can only view their profile (pending approval state)
  - **Writer**: Can manage their own summaries
  - **Admin**: Full access + user management
- **User Management** (Admin only): Approve pending users, change roles, delete users
- **Summary Management**: Create, read, update, delete URL summaries

## Setup

### 1. Azure AD Configuration

You need to register a **Single Page Application (SPA)** in Azure AD:

1. Go to Azure Portal → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: `Summaries Frontend` (or similar)
4. Supported account types: "Accounts in this organizational directory only"
5. Redirect URI: Select "Single-page application (SPA)" and enter `http://localhost:3000`
6. Click "Register"

After registration:

1. Copy the **Application (client) ID** - this is `VITE_AZURE_CLIENT_ID`
2. Go to "API permissions" → "Add a permission"
3. Select "My APIs" → Select your backend API
4. Check `user_impersonation` scope
5. Click "Add permissions"
6. Click "Grant admin consent for [your tenant]"

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

```env
# The SPA App Registration Client ID
VITE_AZURE_CLIENT_ID=your-spa-client-id

# Your Azure AD Tenant ID
VITE_AZURE_TENANT_ID=your-tenant-id

# The Backend API App Registration Client ID (for scope)
VITE_API_CLIENT_ID=your-backend-api-client-id

# Redirect URI (must match Azure AD registration)
VITE_REDIRECT_URI=http://localhost:3000

# API Base URL (proxied through Vite in dev)
VITE_API_BASE_URL=/api
```

### 3. Running with Docker Compose

From the project root:

```bash
docker compose up --build
```

This will start:

- Frontend at http://localhost:3000
- Backend API at http://localhost:8004

### 4. Running Locally (without Docker)

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable components
│   │   ├── Navbar.tsx
│   │   └── ProtectedRoute.tsx
│   ├── config/          # Configuration
│   │   └── authConfig.ts
│   ├── context/         # React contexts
│   │   └── AuthContext.tsx
│   ├── pages/           # Page components
│   │   ├── LoginPage.tsx
│   │   ├── SummariesPage.tsx
│   │   └── UsersAdminPage.tsx
│   ├── services/        # API service layer
│   │   └── api.ts
│   ├── types/           # TypeScript types
│   │   └── index.ts
│   ├── App.tsx          # Main App component
│   ├── App.css          # Global styles
│   └── main.tsx         # Entry point
├── Dockerfile           # Production Docker image
├── Dockerfile.dev       # Development Docker image
├── nginx.conf           # Nginx config for production
└── package.json
```

## Authentication Flow

1. User clicks "Sign in with Microsoft"
2. MSAL redirects to Azure AD login
3. After successful login, user is redirected back with tokens
4. Frontend calls `/users/me` to check if user is registered
5. If not registered, user can click "Complete Registration"
6. After registration, user gets `reader` role (pending approval)
7. Admin can promote user to `writer` to grant access

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` folder, ready to be served by Nginx or any static file server.

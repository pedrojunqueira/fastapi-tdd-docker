// Azure AD / MSAL Configuration
// These values should match your Azure App Registration

export const msalConfig = {
  auth: {
    // The client ID of your SPA registered in Azure AD
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID || "",
    // The tenant ID of your Azure AD
    authority:
      "https://login.microsoftonline.com/" +
      (import.meta.env.VITE_AZURE_TENANT_ID || ""),
    // Where to redirect after login - must be registered in Azure AD
    redirectUri: import.meta.env.VITE_REDIRECT_URI || "http://localhost:3000",
    postLogoutRedirectUri:
      import.meta.env.VITE_REDIRECT_URI || "http://localhost:3000",
  },
  cache: {
    cacheLocation: "sessionStorage" as const,
    storeAuthStateInCookie: false,
  },
};

// The scopes you want to request from Azure AD
// This should match the API scope exposed by your backend
export const loginRequest = {
  scopes: [
    `api://${import.meta.env.VITE_API_CLIENT_ID || ""}/user_impersonation`,
  ],
};

// API configuration
export const apiConfig = {
  baseUrl: import.meta.env.VITE_API_BASE_URL || "/api",
};

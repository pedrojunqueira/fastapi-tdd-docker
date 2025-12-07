import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { MsalProvider } from "@azure/msal-react";
import { PublicClientApplication, EventType } from "@azure/msal-browser";
import { msalConfig } from "./config/authConfig";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Navbar } from "./components/Navbar";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { SummariesPage } from "./pages/SummariesPage";
import { UsersAdminPage } from "./pages/UsersAdminPage";

// Initialize MSAL instance
const msalInstance = new PublicClientApplication(msalConfig);

// Handle redirect promise to complete authentication after redirect
msalInstance.initialize().then(() => {
  // Handle the redirect response
  msalInstance
    .handleRedirectPromise()
    .then((response) => {
      if (response) {
        // Set the active account after successful login
        msalInstance.setActiveAccount(response.account);
      }
    })
    .catch((error) => {
      console.error("Error handling redirect:", error);
    });

  // Set active account on page load if one exists
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length > 0) {
    msalInstance.setActiveAccount(accounts[0]);
  }

  // Listen for login events
  msalInstance.addEventCallback((event) => {
    if (event.eventType === EventType.LOGIN_SUCCESS && event.payload) {
      const payload = event.payload as { account: any };
      msalInstance.setActiveAccount(payload.account);
    }
  });
});

function AppRoutes() {
  const { isAuthenticated, user } = useAuth();

  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-16">
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated && user ? (
                <Navigate to="/summaries" replace />
              ) : (
                <LoginPage />
              )
            }
          />
          <Route
            path="/summaries"
            element={
              <ProtectedRoute>
                <SummariesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute requiredRole="admin">
                <UsersAdminPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              <Navigate
                to={isAuthenticated && user ? "/summaries" : "/login"}
                replace
              />
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
}

function App() {
  return (
    <MsalProvider instance={msalInstance}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </MsalProvider>
  );
}

export default App;

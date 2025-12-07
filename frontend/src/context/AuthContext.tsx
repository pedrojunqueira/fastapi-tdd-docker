import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { loginRequest } from "../config/authConfig";
import { api } from "../services/api";
import type { AuthContextType, User } from "../types";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { instance, accounts, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Acquire token silently when authenticated
  const acquireToken = useCallback(async () => {
    if (accounts.length === 0) {
      setAccessToken(null);
      return null;
    }

    try {
      const response = await instance.acquireTokenSilent({
        ...loginRequest,
        account: accounts[0],
      });
      setAccessToken(response.accessToken);
      return response.accessToken;
    } catch (error) {
      console.error("Failed to acquire token silently:", error);
      // If silent acquisition fails, redirect to login
      try {
        await instance.acquireTokenRedirect(loginRequest);
        // This won't return - page will redirect
        return null;
      } catch (redirectError) {
        console.error("Failed to acquire token via redirect:", redirectError);
        setAccessToken(null);
        return null;
      }
    }
  }, [instance, accounts]);

  // Fetch user profile from backend
  const fetchUserProfile = useCallback(async (token: string) => {
    try {
      const userData = await api.getCurrentUser(token);
      setUser(userData);
      return userData;
    } catch (error) {
      console.error("Failed to fetch user profile:", error);
      setUser(null);
      return null;
    }
  }, []);

  // Register user in backend
  const registerUser = useCallback(async () => {
    const token = accessToken || (await acquireToken());
    if (!token) return null;

    try {
      const userData = await api.registerUser(token);
      setUser(userData);
      return userData;
    } catch (error) {
      console.error("Failed to register user:", error);
      return null;
    }
  }, [accessToken, acquireToken]);

  // Refresh user data
  const refreshUser = useCallback(async () => {
    const token = accessToken || (await acquireToken());
    if (token) {
      await fetchUserProfile(token);
    }
  }, [accessToken, acquireToken, fetchUserProfile]);

  // Login handler - use redirect instead of popup for better compatibility
  const login = useCallback(async () => {
    try {
      await instance.loginRedirect(loginRequest);
    } catch (error) {
      console.error("Login failed:", error);
    }
  }, [instance]);

  // Logout handler - use redirect instead of popup
  const logout = useCallback(() => {
    instance.logoutRedirect();
    setUser(null);
    setAccessToken(null);
  }, [instance]);

  // Effect to handle authentication state changes
  useEffect(() => {
    const initAuth = async () => {
      if (inProgress !== InteractionStatus.None) {
        return;
      }

      setIsLoading(true);

      if (isAuthenticated && accounts.length > 0) {
        const token = await acquireToken();
        if (token) {
          // Try to fetch existing user profile
          const userData = await fetchUserProfile(token);
          if (!userData) {
            // User not registered yet - they'll need to click register
            console.log("User not registered in backend");
          }
        }
      }

      setIsLoading(false);
    };

    initAuth();
  }, [isAuthenticated, accounts, inProgress, acquireToken, fetchUserProfile]);

  const value: AuthContextType = {
    isAuthenticated,
    isLoading: isLoading || inProgress !== InteractionStatus.None,
    user,
    accessToken,
    login,
    logout,
    registerUser,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

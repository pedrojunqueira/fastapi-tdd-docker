import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { ReactNode } from "react";

interface ProtectedRouteProps {
  children: ReactNode;
  requiredRole?: "admin" | "writer" | "reader";
}

export function ProtectedRoute({
  children,
  requiredRole,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-gray-500">
        <div className="w-10 h-10 border-3 border-gray-300 border-t-primary rounded-full animate-spin mb-4"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!user) {
    // User is authenticated with Azure but not registered
    return <Navigate to="/login" replace />;
  }

  // Check role requirements
  if (requiredRole) {
    const roleHierarchy = { admin: 3, writer: 2, reader: 1 };
    const userLevel = roleHierarchy[user.role] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;

    if (userLevel < requiredLevel) {
      return (
        <div className="p-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-red-100 text-red-800 border border-red-200 p-4 rounded-lg">
              Access denied. You don't have permission to view this page.
            </div>
          </div>
        </div>
      );
    }
  }

  return <>{children}</>;
}

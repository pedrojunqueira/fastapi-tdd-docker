import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated || !user) {
    return null;
  }

  const isActive = (path: string) => location.pathname === path;

  const getRoleBadgeClass = (role: string) => {
    switch (role) {
      case "admin":
        return "bg-primary text-white";
      case "writer":
        return "bg-green-500 text-white";
      case "reader":
        return "bg-yellow-500 text-gray-800";
      default:
        return "bg-gray-500 text-white";
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 h-16 bg-slate-900 flex items-center px-6 z-50 shadow-lg">
      <div className="text-white text-xl font-bold">
        <Link to="/" className="hover:text-gray-300">
          Summaries
        </Link>
      </div>

      <div className="flex gap-2 ml-8">
        <Link
          to="/summaries"
          className={`px-4 py-2 rounded transition-colors ${
            isActive("/summaries")
              ? "bg-primary text-white"
              : "text-gray-300 hover:text-white hover:bg-white/10"
          }`}
        >
          My Summaries
        </Link>

        {user.role === "admin" && (
          <Link
            to="/admin/users"
            className={`px-4 py-2 rounded transition-colors ${
              isActive("/admin/users")
                ? "bg-primary text-white"
                : "text-gray-300 hover:text-white hover:bg-white/10"
            }`}
          >
            User Management
          </Link>
        )}
      </div>

      <div className="ml-auto flex items-center gap-4">
        <span className="text-gray-200 text-sm flex items-center gap-2">
          {user.email}
          <span
            className={`text-xs px-2 py-1 rounded-full font-medium uppercase ${getRoleBadgeClass(
              user.role
            )}`}
          >
            {user.role}
          </span>
        </span>
        <button
          onClick={logout}
          className="px-3 py-1.5 text-sm bg-gray-600 text-white rounded hover:bg-gray-500 transition-colors"
        >
          Sign Out
        </button>
      </div>
    </nav>
  );
}

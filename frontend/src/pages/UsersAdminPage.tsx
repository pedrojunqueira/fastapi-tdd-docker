import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import type { User } from "../types";

export function UsersAdminPage() {
  const { user: currentUser, accessToken } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchUsers = async () => {
    if (!accessToken) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await api.getUsers(accessToken);
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch users");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [accessToken]);

  const handleRoleChange = async (
    userId: number,
    newRole: "admin" | "writer" | "reader"
  ) => {
    if (!accessToken) return;

    try {
      await api.updateUser(accessToken, userId, { role: newRole });
      setSuccessMessage(`User role updated to ${newRole}`);
      fetchUsers();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to update user role"
      );
    }
  };

  const handleDelete = async (userId: number, userEmail: string) => {
    if (!accessToken) return;
    if (!confirm(`Are you sure you want to delete user ${userEmail}?`)) return;

    try {
      await api.deleteUser(accessToken, userId);
      setSuccessMessage("User deleted successfully");
      fetchUsers();

      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete user");
    }
  };

  // Check if current user is admin
  if (currentUser?.role !== "admin") {
    return (
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold mb-4">User Management</h1>
          <div className="bg-red-100 text-red-800 border border-red-200 p-4 rounded-lg">
            <p>Access denied. Administrator privileges required.</p>
          </div>
        </div>
      </div>
    );
  }

  // Separate users by role for easier management
  const pendingUsers = users.filter((u) => u.role === "reader");
  const activeUsers = users.filter((u) => u.role === "writer");
  const adminUsers = users.filter((u) => u.role === "admin");

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">User Management</h1>

        {error && (
          <div className="bg-red-100 text-red-800 border border-red-200 p-4 rounded-lg mb-4 flex justify-between items-center">
            {error}
            <button
              onClick={() => setError(null)}
              className="text-red-800 hover:text-red-900 text-xl font-bold"
            >
              ×
            </button>
          </div>
        )}

        {successMessage && (
          <div className="bg-green-100 text-green-800 border border-green-200 p-4 rounded-lg mb-4">
            {successMessage}
          </div>
        )}

        {isLoading ? (
          <div className="flex flex-col items-center py-16 text-gray-500">
            <div className="w-10 h-10 border-4 border-gray-300 border-t-primary rounded-full animate-spin mb-4"></div>
            <p>Loading users...</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Pending Approval Section */}
            {pendingUsers.length > 0 && (
              <section>
                <h2 className="text-xl font-semibold mb-2 flex items-center gap-2">
                  <span className="px-2 py-1 text-sm bg-yellow-100 text-yellow-800 rounded">
                    Pending Approval
                  </span>
                  <span className="text-gray-500">({pendingUsers.length})</span>
                </h2>
                <p className="text-gray-600 mb-4">
                  These users have registered but need to be approved to use the
                  app.
                </p>
                <div className="space-y-3">
                  {pendingUsers.map((user) => (
                    <div
                      key={user.id}
                      className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-400 flex justify-between items-center"
                    >
                      <div>
                        <span className="font-medium">{user.email}</span>
                        <span className="block text-sm text-gray-500">
                          Registered:{" "}
                          {user.created_at
                            ? new Date(user.created_at).toLocaleDateString()
                            : "N/A"}
                        </span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleRoleChange(user.id, "writer")}
                          className="px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                        >
                          Approve as Writer
                        </button>
                        <button
                          onClick={() => handleDelete(user.id, user.email)}
                          className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Active Writers Section */}
            <section>
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span className="px-2 py-1 text-sm bg-blue-100 text-blue-800 rounded">
                  Writers
                </span>
                <span className="text-gray-500">({activeUsers.length})</span>
              </h2>
              <div className="space-y-3">
                {activeUsers.length === 0 ? (
                  <p className="text-gray-500 py-4">No writers yet.</p>
                ) : (
                  activeUsers.map((user) => (
                    <div
                      key={user.id}
                      className="bg-white rounded-lg shadow p-4 flex justify-between items-center"
                    >
                      <div>
                        <span className="font-medium">{user.email}</span>
                        <span className="block text-sm text-gray-500">
                          Last login:{" "}
                          {user.last_login
                            ? new Date(user.last_login).toLocaleString()
                            : "Never"}
                        </span>
                      </div>
                      <div className="flex gap-2 items-center">
                        <select
                          value={user.role}
                          onChange={(e) =>
                            handleRoleChange(
                              user.id,
                              e.target.value as "admin" | "writer" | "reader"
                            )
                          }
                          className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="reader">Reader (Pending)</option>
                          <option value="writer">Writer</option>
                          <option value="admin">Admin</option>
                        </select>
                        <button
                          onClick={() => handleDelete(user.id, user.email)}
                          className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>

            {/* Admins Section */}
            <section>
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span className="px-2 py-1 text-sm bg-purple-100 text-purple-800 rounded">
                  Administrators
                </span>
                <span className="text-gray-500">({adminUsers.length})</span>
              </h2>
              <div className="space-y-3">
                {adminUsers.map((user) => (
                  <div
                    key={user.id}
                    className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-400 flex justify-between items-center"
                  >
                    <div>
                      <span className="font-medium">
                        {user.email}
                        {user.id === currentUser?.id && (
                          <span className="ml-2 px-2 py-0.5 text-xs bg-primary text-white rounded">
                            You
                          </span>
                        )}
                      </span>
                      <span className="block text-sm text-gray-500">
                        Last login:{" "}
                        {user.last_login
                          ? new Date(user.last_login).toLocaleString()
                          : "Never"}
                      </span>
                    </div>
                    <div className="flex gap-2 items-center">
                      {user.id !== currentUser?.id && (
                        <>
                          <select
                            value={user.role}
                            onChange={(e) =>
                              handleRoleChange(
                                user.id,
                                e.target.value as "admin" | "writer" | "reader"
                              )
                            }
                            className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary"
                          >
                            <option value="reader">Reader (Pending)</option>
                            <option value="writer">Writer</option>
                            <option value="admin">Admin</option>
                          </select>
                          <button
                            onClick={() => handleDelete(user.id, user.email)}
                            className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                          >
                            Delete
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

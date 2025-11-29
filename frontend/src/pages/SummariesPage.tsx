import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import type {
  Summary,
  SummaryCreatePayload,
  SummaryUpdatePayload,
} from "../types";

export function SummariesPage() {
  const { user, accessToken } = useAuth();
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingSummary, setEditingSummary] = useState<Summary | null>(null);

  // Form state
  const [formUrl, setFormUrl] = useState("");
  const [formSummary, setFormSummary] = useState("");

  const fetchSummaries = async () => {
    if (!accessToken) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await api.getSummaries(accessToken);
      setSummaries(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch summaries"
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSummaries();
  }, [accessToken]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken) return;

    try {
      const payload: SummaryCreatePayload = {
        url: formUrl,
        ...(formSummary && { summary: formSummary }),
      };
      await api.createSummary(accessToken, payload);
      setShowForm(false);
      resetForm();
      fetchSummaries();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create summary");
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken || !editingSummary) return;

    try {
      const payload: SummaryUpdatePayload = {
        url: formUrl,
        summary: formSummary,
      };
      await api.updateSummary(accessToken, editingSummary.id, payload);
      setEditingSummary(null);
      resetForm();
      fetchSummaries();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update summary");
    }
  };

  const handleDelete = async (summaryId: number) => {
    if (!accessToken) return;
    if (!confirm("Are you sure you want to delete this summary?")) return;

    try {
      await api.deleteSummary(accessToken, summaryId);
      fetchSummaries();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete summary");
    }
  };

  const startEdit = (summary: Summary) => {
    setEditingSummary(summary);
    setFormUrl(summary.url);
    setFormSummary(summary.summary);
    setShowForm(false);
  };

  const resetForm = () => {
    setFormUrl("");
    setFormSummary("");
  };

  const cancelEdit = () => {
    setEditingSummary(null);
    resetForm();
  };

  const cancelCreate = () => {
    setShowForm(false);
    resetForm();
  };

  // Check if user can create/edit summaries
  const canWrite = user?.role === "writer" || user?.role === "admin";
  const isAdmin = user?.role === "admin";

  if (!canWrite) {
    return (
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold mb-4">Summaries</h1>
          <div className="bg-yellow-100 text-yellow-800 border border-yellow-300 p-4 rounded-lg">
            <p className="font-medium">Your account is pending approval.</p>
            <p>
              An administrator needs to promote your account to "writer" role
              before you can access summaries.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">My Summaries</h1>
          {canWrite && !showForm && !editingSummary && (
            <button
              onClick={() => setShowForm(true)}
              className="px-4 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors"
            >
              Add Summary
            </button>
          )}
        </div>

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

        {/* Create Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6 max-w-xl">
            <h2 className="text-xl font-semibold mb-4">New Summary</h2>
            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label htmlFor="url" className="block font-medium mb-1">
                  URL *
                </label>
                <input
                  type="url"
                  id="url"
                  value={formUrl}
                  onChange={(e) => setFormUrl(e.target.value)}
                  placeholder="https://example.com"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="summary" className="block font-medium mb-1">
                  Summary (optional)
                </label>
                <textarea
                  id="summary"
                  value={formSummary}
                  onChange={(e) => setFormSummary(e.target.value)}
                  placeholder="Enter a summary or leave blank for auto-generation"
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors"
                >
                  Create
                </button>
                <button
                  type="button"
                  onClick={cancelCreate}
                  className="px-4 py-2 bg-gray-500 text-white font-medium rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Edit Form */}
        {editingSummary && (
          <div className="bg-white rounded-lg shadow p-6 mb-6 max-w-xl">
            <h2 className="text-xl font-semibold mb-4">Edit Summary</h2>
            <form onSubmit={handleUpdate}>
              <div className="mb-4">
                <label htmlFor="edit-url" className="block font-medium mb-1">
                  URL *
                </label>
                <input
                  type="url"
                  id="edit-url"
                  value={formUrl}
                  onChange={(e) => setFormUrl(e.target.value)}
                  placeholder="https://example.com"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="edit-summary"
                  className="block font-medium mb-1"
                >
                  Summary *
                </label>
                <textarea
                  id="edit-summary"
                  value={formSummary}
                  onChange={(e) => setFormSummary(e.target.value)}
                  placeholder="Enter your summary"
                  rows={4}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors"
                >
                  Save
                </button>
                <button
                  type="button"
                  onClick={cancelEdit}
                  className="px-4 py-2 bg-gray-500 text-white font-medium rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Summaries List */}
        {isLoading ? (
          <div className="flex flex-col items-center py-16 text-gray-500">
            <div className="w-10 h-10 border-4 border-gray-300 border-t-primary rounded-full animate-spin mb-4"></div>
            <p>Loading summaries...</p>
          </div>
        ) : summaries.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <p>
              No summaries yet. Click "Add Summary" to create your first one!
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {summaries.map((summary) => (
              <div
                key={summary.id}
                className="bg-white rounded-lg shadow p-6 border-l-4 border-primary"
              >
                <div className="flex justify-between items-start mb-4">
                  <a
                    href={summary.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary font-medium hover:underline break-all"
                  >
                    {summary.url}
                  </a>
                  {(isAdmin || summary.user_id === user?.id) && (
                    <div className="flex gap-2 ml-4 flex-shrink-0">
                      <button
                        onClick={() => startEdit(summary)}
                        className="px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(summary.id)}
                        className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
                <p className="text-gray-700 mb-4">{summary.summary}</p>
                <div className="text-sm text-gray-500">
                  Created: {new Date(summary.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

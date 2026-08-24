import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useOrg } from "../contexts/OrgContext";
import { listDashboards, createDashboard, deleteDashboard } from "../api/dashboards";
import type { Dashboard } from "../api/dashboards";

export default function DashboardsPage() {
  const { currentOrg } = useOrg();
  const navigate = useNavigate();

  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", is_public: false });
  const [creating, setCreating] = useState(false);

  const fetchDashboards = () => {
    if (!currentOrg) return;
    setLoading(true);
    listDashboards(currentOrg.id)
      .then(({ data }) => setDashboards(data))
      .catch(() => setError("Failed to load dashboards."))
      .finally(() => setLoading(false));
  };

  useEffect(fetchDashboards, [currentOrg]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentOrg) return;
    setCreating(true);
    try {
      const { data } = await createDashboard(currentOrg.id, form);
      setDashboards((prev) => [data, ...prev]);
      setShowForm(false);
      setForm({ name: "", description: "", is_public: false });
    } catch {
      setError("Failed to create dashboard.");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!currentOrg) return;
    if (!window.confirm("Delete this dashboard?")) return;
    try {
      await deleteDashboard(currentOrg.id, id);
      setDashboards((prev) => prev.filter((d) => d.id !== id));
    } catch {
      setError("Delete failed.");
    }
  };

  if (!currentOrg) {
    return <div className="page-empty">No organization selected.</div>;
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2 className="page-title">Dashboards</h2>
        <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancel" : "+ New Dashboard"}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h3 className="card-title">Create Dashboard</h3>
          <form onSubmit={handleCreate} className="create-form">
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                required
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <input
                type="text"
                value={form.description}
                onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
              />
            </div>
            <div className="form-check">
              <input
                type="checkbox"
                id="is_public"
                checked={form.is_public}
                onChange={(e) => setForm((p) => ({ ...p, is_public: e.target.checked }))}
              />
              <label htmlFor="is_public">Make public</label>
            </div>
            <button type="submit" className="btn btn-primary" disabled={creating}>
              {creating ? "Creating…" : "Create"}
            </button>
          </form>
        </div>
      )}

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading-screen"><div className="spinner" /></div>
      ) : (
        <div className="grid grid-cols-3">
          {dashboards.length === 0 ? (
            <p className="empty-state">No dashboards yet.</p>
          ) : (
            dashboards.map((db) => (
              <div
                key={db.id}
                className="card dashboard-card"
                onClick={() => navigate(`/orgs/${currentOrg.id}/dashboards/${db.id}`)}
              >
                <div className="dashboard-card-header">
                  <h3 className="dashboard-name">{db.name}</h3>
                  {db.is_public && <span className="badge badge-info">Public</span>}
                </div>
                <p className="dashboard-desc">{db.description || "No description"}</p>
                <div className="dashboard-card-footer">
                  <span className="text-muted">
                    {new Date(db.updated_at).toLocaleDateString()}
                  </span>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={(e) => { e.stopPropagation(); handleDelete(db.id); }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

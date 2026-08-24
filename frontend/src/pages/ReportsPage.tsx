import React, { useEffect, useState } from "react";
import { useOrg } from "../contexts/OrgContext";
import { listReports, createReport, generateReport, deleteReport } from "../api/reports";
import type { Report } from "../api/reports";

const FORMAT_LABELS: Record<string, string> = {
  pdf: "PDF",
  xlsx: "Excel",
  csv: "CSV",
  html: "HTML",
};

export default function ReportsPage() {
  const { currentOrg } = useOrg();

  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: "",
    executive_summary: "",
    report_format: "pdf" as Report["report_format"],
  });
  const [creating, setCreating] = useState(false);
  const [generating, setGenerating] = useState<string | null>(null);

  const fetchReports = () => {
    if (!currentOrg) return;
    setLoading(true);
    listReports(currentOrg.id)
      .then(({ data }) => setReports(data))
      .catch(() => setError("Failed to load reports."))
      .finally(() => setLoading(false));
  };

  useEffect(fetchReports, [currentOrg]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentOrg) return;
    setCreating(true);
    try {
      const { data } = await createReport(currentOrg.id, form);
      setReports((prev) => [data, ...prev]);
      setShowForm(false);
      setForm({ title: "", executive_summary: "", report_format: "pdf" });
    } catch {
      setError("Failed to create report.");
    } finally {
      setCreating(false);
    }
  };

  const handleGenerate = async (id: string) => {
    if (!currentOrg) return;
    setGenerating(id);
    try {
      await generateReport(currentOrg.id, id);
      fetchReports();
    } catch {
      setError("Generation failed.");
    } finally {
      setGenerating(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (!currentOrg) return;
    if (!window.confirm("Delete this report?")) return;
    try {
      await deleteReport(currentOrg.id, id);
      setReports((prev) => prev.filter((r) => r.id !== id));
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
        <h2 className="page-title">Reports</h2>
        <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancel" : "+ New Report"}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h3 className="card-title">Create Report</h3>
          <form onSubmit={handleCreate} className="create-form">
            <div className="form-group">
              <label>Title</label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))}
                required
              />
            </div>
            <div className="form-group">
              <label>Executive Summary</label>
              <textarea
                value={form.executive_summary}
                onChange={(e) => setForm((p) => ({ ...p, executive_summary: e.target.value }))}
                rows={3}
              />
            </div>
            <div className="form-group">
              <label>Format</label>
              <select
                value={form.report_format}
                onChange={(e) =>
                  setForm((p) => ({ ...p, report_format: e.target.value as Report["report_format"] }))
                }
              >
                {Object.entries(FORMAT_LABELS).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
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
        <div className="card">
          {reports.length === 0 ? (
            <p className="empty-state">No reports yet.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Format</th>
                  <th>Status</th>
                  <th>Generated</th>
                  <th>Created</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r) => (
                  <tr key={r.id}>
                    <td className="font-medium">{r.title}</td>
                    <td>
                      <span className="badge badge-neutral">
                        {FORMAT_LABELS[r.report_format] ?? r.report_format}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${r.status === "generated" ? "badge-success" : "badge-info"}`}>
                        {r.status}
                      </span>
                    </td>
                    <td>{r.generated_at ? new Date(r.generated_at).toLocaleDateString() : "—"}</td>
                    <td>{new Date(r.created_at).toLocaleDateString()}</td>
                    <td className="action-cell">
                      {r.status === "draft" && (
                        <button
                          className="btn btn-sm btn-secondary"
                          onClick={() => handleGenerate(r.id)}
                          disabled={generating === r.id}
                        >
                          {generating === r.id ? "…" : "Generate"}
                        </button>
                      )}
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDelete(r.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

import React, { useEffect, useState, useRef } from "react";
import { useOrg } from "../contexts/OrgContext";
import { listDatasets, uploadDataset, deleteDataset } from "../api/datasets";
import type { Dataset } from "../api/datasets";

const STATUS_COLORS: Record<string, string> = {
  ready: "badge-success",
  processing: "badge-info",
  uploading: "badge-info",
  validating: "badge-info",
  failed: "badge-error",
  archived: "badge-neutral",
};

export default function DatasetsPage() {
  const { currentOrg } = useOrg();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadName, setUploadName] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const fetchDatasets = () => {
    if (!currentOrg) return;
    setLoading(true);
    listDatasets(currentOrg.id)
      .then(({ data }) => setDatasets(data))
      .catch(() => setError("Failed to load datasets."))
      .finally(() => setLoading(false));
  };

  useEffect(fetchDatasets, [currentOrg]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentOrg || !fileRef.current?.files?.length) return;
    const file = fileRef.current.files[0];
    const fd = new FormData();
    fd.append("file", file);
    fd.append("name", uploadName || file.name);
    setUploading(true);
    setUploadError(null);
    try {
      await uploadDataset(currentOrg.id, fd);
      setUploadName("");
      if (fileRef.current) fileRef.current.value = "";
      fetchDatasets();
    } catch {
      setUploadError("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!currentOrg) return;
    if (!window.confirm("Delete this dataset?")) return;
    try {
      await deleteDataset(currentOrg.id, id);
      setDatasets((prev) => prev.filter((d) => d.id !== id));
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
        <h2 className="page-title">Datasets</h2>
      </div>

      <div className="card upload-card">
        <h3 className="card-title">Upload Dataset</h3>
        <form onSubmit={handleUpload} className="upload-form">
          <input
            type="text"
            placeholder="Dataset name (optional)"
            value={uploadName}
            onChange={(e) => setUploadName(e.target.value)}
            className="form-input"
          />
          <input
            ref={fileRef}
            type="file"
            accept=".csv,.xlsx,.xls,.json,.xml,.parquet"
            className="form-input"
            required
          />
          {uploadError && <div className="alert alert-error">{uploadError}</div>}
          <button type="submit" className="btn btn-primary" disabled={uploading}>
            {uploading ? "Uploading…" : "Upload"}
          </button>
        </form>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading-screen"><div className="spinner" /></div>
      ) : (
        <div className="card">
          {datasets.length === 0 ? (
            <p className="empty-state">No datasets yet. Upload one to get started.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Rows</th>
                  <th>Columns</th>
                  <th>Created</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {datasets.map((ds) => (
                  <tr key={ds.id}>
                    <td className="font-medium">{ds.name}</td>
                    <td>
                      <span className={`badge ${STATUS_COLORS[ds.status] ?? "badge-neutral"}`}>
                        {ds.status}
                      </span>
                    </td>
                    <td>{ds.row_count ?? "—"}</td>
                    <td>{ds.column_count ?? "—"}</td>
                    <td>{new Date(ds.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDelete(ds.id)}
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

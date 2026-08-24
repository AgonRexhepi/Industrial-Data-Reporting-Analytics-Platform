import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useOrg } from "../contexts/OrgContext";
import { getDashboard, listWidgets } from "../api/dashboards";
import type { Dashboard, DashboardWidget } from "../api/dashboards";

const WIDGET_ICONS: Record<string, string> = {
  kpi: "📈",
  table: "📋",
  bar: "📊",
  line: "📉",
  pie: "🥧",
  area: "🏔",
  scatter: "✦",
  heatmap: "🔥",
};

export default function DashboardDetailPage() {
  const { dashboardId } = useParams<{ dashboardId: string }>();
  const { currentOrg } = useOrg();

  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [widgets, setWidgets] = useState<DashboardWidget[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentOrg || !dashboardId) return;
    setLoading(true);
    Promise.all([
      getDashboard(currentOrg.id, dashboardId),
      listWidgets(currentOrg.id, dashboardId),
    ])
      .then(([{ data: db }, { data: wgs }]) => {
        setDashboard(db);
        setWidgets(wgs);
      })
      .catch(() => setError("Failed to load dashboard."))
      .finally(() => setLoading(false));
  }, [currentOrg, dashboardId]);

  if (loading) return <div className="loading-screen"><div className="spinner" /></div>;
  if (error) return <div className="alert alert-error">{error}</div>;
  if (!dashboard) return null;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2 className="page-title">{dashboard.name}</h2>
          {dashboard.description && (
            <p className="page-subtitle">{dashboard.description}</p>
          )}
        </div>
        {dashboard.is_public && <span className="badge badge-info">Public</span>}
      </div>

      {widgets.length === 0 ? (
        <div className="card">
          <p className="empty-state">
            This dashboard has no widgets yet. Use the API or admin to add widgets.
          </p>
        </div>
      ) : (
        <div className="widgets-grid">
          {widgets.map((w) => (
            <div
              key={w.id}
              className="widget-card"
              style={{
                gridColumn: `span ${Math.min(w.width, 12)}`,
              }}
            >
              <div className="widget-header">
                <span className="widget-icon">
                  {WIDGET_ICONS[w.widget_type] ?? "📦"}
                </span>
                <h4 className="widget-title">{w.title}</h4>
                <span className="badge badge-neutral">{w.widget_type}</span>
              </div>
              <div className="widget-body">
                <p className="text-muted">
                  Widget visualization requires a connected dataset.
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

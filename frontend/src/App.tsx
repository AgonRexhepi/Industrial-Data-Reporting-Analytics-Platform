import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { OrgProvider } from "./contexts/OrgContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DatasetsPage from "./pages/DatasetsPage";
import DashboardsPage from "./pages/DashboardsPage";
import DashboardDetailPage from "./pages/DashboardDetailPage";
import ReportsPage from "./pages/ReportsPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <OrgProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route path="/orgs/:orgId/datasets" element={<DatasetsPage />} />
                <Route path="/orgs/:orgId/dashboards" element={<DashboardsPage />} />
                <Route path="/orgs/:orgId/dashboards/:dashboardId" element={<DashboardDetailPage />} />
                <Route path="/orgs/:orgId/reports" element={<ReportsPage />} />
                <Route path="/" element={<Navigate to="/login" replace />} />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </OrgProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useOrg } from "../contexts/OrgContext";

/**
 * Redirects authenticated users to their first organization's datasets page,
 * and unauthenticated users to the login page.
 */
export default function RootRedirect() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { currentOrg, isLoading: orgLoading } = useOrg();

  if (authLoading || orgLoading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (currentOrg) {
    return <Navigate to={`/orgs/${currentOrg.id}/datasets`} replace />;
  }

  return <Navigate to="/login" replace />;
}

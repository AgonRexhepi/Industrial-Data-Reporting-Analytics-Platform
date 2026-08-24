import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useOrg } from "../contexts/OrgContext";

export default function Layout() {
  const { user, logout } = useAuth();
  const { currentOrg } = useOrg();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const orgPrefix = currentOrg ? `/orgs/${currentOrg.id}` : "";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-icon">⚙</span>
          <span className="brand-name">IndustrialBI</span>
        </div>
        <nav className="sidebar-nav">
          <NavLink to={`${orgPrefix}/datasets`} className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
            <span className="nav-icon">📊</span> Datasets
          </NavLink>
          <NavLink to={`${orgPrefix}/dashboards`} className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
            <span className="nav-icon">🗂</span> Dashboards
          </NavLink>
          <NavLink to={`${orgPrefix}/reports`} className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
            <span className="nav-icon">📄</span> Reports
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          <span className="user-name">{user?.email}</span>
          <button className="btn-logout" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

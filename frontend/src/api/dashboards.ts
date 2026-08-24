import apiClient from "./client";

export interface Dashboard {
  id: string;
  name: string;
  description: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface DashboardWidget {
  id: string;
  title: string;
  widget_type: string;
  configuration: Record<string, unknown>;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
}

export const listDashboards = (orgId: string) =>
  apiClient.get<Dashboard[]>(`/organizations/${orgId}/dashboards/`);

export const getDashboard = (orgId: string, id: string) =>
  apiClient.get<Dashboard>(`/organizations/${orgId}/dashboards/${id}/`);

export const createDashboard = (
  orgId: string,
  payload: Pick<Dashboard, "name" | "description" | "is_public">,
) => apiClient.post<Dashboard>(`/organizations/${orgId}/dashboards/`, payload);

export const deleteDashboard = (orgId: string, id: string) =>
  apiClient.delete(`/organizations/${orgId}/dashboards/${id}/`);

export const listWidgets = (orgId: string, dashboardId: string) =>
  apiClient.get<DashboardWidget[]>(
    `/organizations/${orgId}/dashboards/${dashboardId}/widgets/`,
  );

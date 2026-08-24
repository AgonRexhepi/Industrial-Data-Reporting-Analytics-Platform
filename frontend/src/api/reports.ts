import apiClient from "./client";

export interface Report {
  id: string;
  title: string;
  executive_summary: string;
  report_format: "pdf" | "xlsx" | "csv" | "html";
  status: "draft" | "generated";
  generated_at: string | null;
  created_at: string;
  updated_at: string;
}

export const listReports = (orgId: string) =>
  apiClient.get<Report[]>(`/organizations/${orgId}/reports/`);

export const getReport = (orgId: string, id: string) =>
  apiClient.get<Report>(`/organizations/${orgId}/reports/${id}/`);

export const createReport = (
  orgId: string,
  payload: Pick<Report, "title" | "executive_summary" | "report_format">,
) => apiClient.post<Report>(`/organizations/${orgId}/reports/`, payload);

export const generateReport = (orgId: string, id: string) =>
  apiClient.post(`/organizations/${orgId}/reports/${id}/generate/`);

export const deleteReport = (orgId: string, id: string) =>
  apiClient.delete(`/organizations/${orgId}/reports/${id}/`);

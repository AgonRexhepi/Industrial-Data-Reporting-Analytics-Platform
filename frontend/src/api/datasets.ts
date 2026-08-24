import apiClient from "./client";

export interface Dataset {
  id: string;
  name: string;
  description: string;
  status: "uploading" | "processing" | "validating" | "ready" | "failed" | "archived";
  row_count: number | null;
  column_count: number | null;
  created_at: string;
  updated_at: string;
}

export const listDatasets = (orgId: string) =>
  apiClient.get<Dataset[]>(`/organizations/${orgId}/datasets/`);

export const getDataset = (orgId: string, id: string) =>
  apiClient.get<Dataset>(`/organizations/${orgId}/datasets/${id}/`);

export const uploadDataset = (orgId: string, formData: FormData) =>
  apiClient.post<Dataset>(`/organizations/${orgId}/ingestion/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

export const deleteDataset = (orgId: string, id: string) =>
  apiClient.delete(`/organizations/${orgId}/datasets/${id}/`);

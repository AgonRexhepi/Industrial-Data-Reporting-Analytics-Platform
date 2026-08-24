import apiClient from "./client";

export interface Organization {
  id: string;
  name: string;
  slug: string;
}

export const listOrganizations = () =>
  apiClient.get<Organization[]>("/organizations/");

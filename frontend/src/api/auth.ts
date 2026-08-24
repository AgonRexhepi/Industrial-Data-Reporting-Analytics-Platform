import apiClient from "./client";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

export interface UserProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
}

export const login = (payload: LoginPayload) =>
  apiClient.post<TokenResponse>("/auth/login/", payload);

export const register = (payload: RegisterPayload) =>
  apiClient.post<UserProfile>("/auth/register/", payload);

export const getMe = () => apiClient.get<UserProfile>("/auth/me/");

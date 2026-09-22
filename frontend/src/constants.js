export const API_BASE = '/api/v1';

export const AUTH_COOKIE = 'access_token';

export const SEED_LOGIN = { email: 'admin@example.com', password: 'admin123' };

export const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export const endpoints = {
  login: `${API_BASE}/auth/login`,
  logout: `${API_BASE}/auth/logout`,
  me: `${API_BASE}/auth/me`,
  companies: `${API_BASE}/companies`,
  company: (id) => `${API_BASE}/companies/${id}`,
  employees: `${API_BASE}/employees`,
  employee: (id) => `${API_BASE}/employees/${id}`,
  projects: `${API_BASE}/projects`,
  project: (id) => `${API_BASE}/projects/${id}`,
};
import { endpoints } from './constants.js';

export async function apiFetch(path, { method = 'GET', body } = {}) {
  const headers = {};
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  const res = await fetch(path, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    credentials: 'include',
  });
  if (res.status === 204) {
    return null;
  }
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }
  if (!res.ok) {
    const detail = data?.detail ?? res.statusText;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg ?? JSON.stringify(d)).join('; ')
      : detail;
    const err = new Error(message || `Request failed: ${res.status}`);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

export async function loginRequest(email, password) {
  const form = new URLSearchParams();
  form.append('username', email);
  form.append('password', password);
  const res = await fetch(endpoints.login, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString(),
    credentials: 'include',
  });
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }
  if (!res.ok) {
    const detail = data?.detail ?? res.statusText;
    const err = new Error(typeof detail === 'string' ? detail : 'Login failed');
    err.status = res.status;
    throw err;
  }
  return data;
}

export const logoutRequest = () => apiFetch(endpoints.logout, { method: 'POST' });

export const meRequest = () => apiFetch(endpoints.me);

export const api = {
  listCompanies: (skip = 0, limit = 100) =>
    apiFetch(`${endpoints.companies}?skip=${skip}&limit=${limit}`),
  getCompany: (id) => apiFetch(endpoints.company(id)),
  createCompany: (data) => apiFetch(endpoints.companies, { method: 'POST', body: data }),
  updateCompany: (id, data) => apiFetch(endpoints.company(id), { method: 'PUT', body: data }),
  deleteCompany: (id) => apiFetch(endpoints.company(id), { method: 'DELETE' }),

  listEmployees: ({ companyId, skip = 0, limit = 100 } = {}) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (companyId) params.append('company_id', companyId);
    return apiFetch(`${endpoints.employees}?${params.toString()}`);
  },
  createEmployee: (data) => apiFetch(endpoints.employees, { method: 'POST', body: data }),
  updateEmployee: (id, data) => apiFetch(endpoints.employee(id), { method: 'PUT', body: data }),
  deleteEmployee: (id) => apiFetch(endpoints.employee(id), { method: 'DELETE' }),

  listProjects: ({ companyId, skip = 0, limit = 100 } = {}) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (companyId) params.append('company_id', companyId);
    return apiFetch(`${endpoints.projects}?${params.toString()}`);
  },
  createProject: (data) => apiFetch(endpoints.projects, { method: 'POST', body: data }),
  updateProject: (id, data) => apiFetch(endpoints.project(id), { method: 'PUT', body: data }),
  deleteProject: (id) => apiFetch(endpoints.project(id), { method: 'DELETE' }),
};
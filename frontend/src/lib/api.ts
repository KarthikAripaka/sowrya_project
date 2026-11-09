/**
 * MediEvidence AI Frontend API Client
 * Connects directly to FastAPI backend on port 8000 or via Next.js proxy
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('medi_ai_token');
}

export function setAuthToken(token: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('medi_ai_token', token);
  }
}

export function clearAuthToken() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('medi_ai_token');
    localStorage.removeItem('medi_ai_user');
  }
}

export function getStoredUser(): any | null {
  if (typeof window === 'undefined') return null;
  const user = localStorage.getItem('medi_ai_user');
  try {
    if (user) return JSON.parse(user);
  } catch {}
  // Default instant free guest user: zero auth burden
  return {
    id: 1,
    email: "guest@medicalai.org",
    full_name: "Guest User (Free Access)",
    is_active: true
  };
}

export function setStoredUser(user: any) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('medi_ai_user', JSON.stringify(user));
  }
}

async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // Do not set Content-Type if body is FormData
  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errMsg = `Request failed: ${res.statusText}`;
    try {
      const errJson = await res.json();
      errMsg = errJson.detail || errJson.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }

  return res.json();
}

export const api = {
  // Auth
  async login(email: string, password: string) {
    const data = await fetchAPI('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setAuthToken(data.access_token);
    setStoredUser(data.user);
    return data;
  },

  async register(email: string, password: string, fullName: string) {
    const data = await fetchAPI('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    setAuthToken(data.access_token);
    setStoredUser(data.user);
    return data;
  },

  async logout() {
    try {
      await fetchAPI('/auth/logout', { method: 'POST' });
    } catch {}
    clearAuthToken();
  },

  async getMe() {
    return fetchAPI('/auth/me');
  },

  // Dashboard
  async getDashboardStats() {
    return fetchAPI('/dashboard/stats');
  },

  // Reports
  async uploadReport(formData: FormData) {
    return fetchAPI('/reports/upload', {
      method: 'POST',
      body: formData,
    });
  },

  async getReports() {
    return fetchAPI('/reports');
  },

  async getReport(id: string | number) {
    return fetchAPI(`/reports/${id}`);
  },

  async deleteReport(id: string | number) {
    return fetchAPI(`/reports/${id}`, { method: 'DELETE' });
  },

  getReportPdfUrl(id: string | number) {
    return `${API_BASE}/reports/${id}/pdf`;
  },

  // X-rays
  async uploadXray(formData: FormData) {
    return fetchAPI('/analysis/xray', {
      method: 'POST',
      body: formData,
    });
  },

  async getXrays() {
    return fetchAPI('/analysis/xray');
  },

  async getXray(id: string | number) {
    return fetchAPI(`/analysis/xray/${id}`);
  },

  getXrayPdfUrl(id: string | number) {
    return `${API_BASE}/analysis/xray/${id}/pdf`;
  },

  // History
  async getHistory(search?: string, reportType?: string) {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (reportType) params.append('report_type', reportType);
    return fetchAPI(`/history?${params.toString()}`);
  },

  async deleteHistoryItem(type: 'report' | 'xray', id: string | number) {
    return fetchAPI(`/history/${type}/${id}`, { method: 'DELETE' });
  },

  // RAG Knowledge
  async queryRAG(query: string, topK = 4) {
    return fetchAPI('/rag/query', {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK }),
    });
  },

  async getCuratedSources() {
    return fetchAPI('/rag/sources');
  },

  // Settings & DPDP Data Deletion
  async updateProfile(fullName?: string, password?: string) {
    return fetchAPI('/users/profile', {
      method: 'PUT',
      body: JSON.stringify({ full_name: fullName, password }),
    });
  },

  async deleteAllUserData() {
    return fetchAPI('/users/data', { method: 'DELETE' });
  },
};


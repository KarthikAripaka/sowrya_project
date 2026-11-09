/**
 * MediEvidence AI Frontend API Client
 * Connects directly to FastAPI backend on port 8000 or via Next.js proxy
 */

/**
 * Dynamically resolve backend API Base URL:
 * 1. Explicit NEXT_PUBLIC_API_URL environment variable (if set in Vercel)
 * 2. If running in a remote browser (e.g. *.vercel.app), use relative '/api/v1' to route through Next.js proxy rewrite
 * 3. Local fallback to http://localhost:8000/api/v1
 */
function getApiBase(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '');
  }
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host !== 'localhost' && host !== '127.0.0.1') {
      return '/api/v1';
    }
  }
  return 'http://localhost:8000/api/v1';
}

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

  const apiBase = getApiBase();
  const url = `${apiBase}${endpoint}`;

  let res: Response;
  try {
    res = await fetch(url, {
      ...options,
      headers,
    });
  } catch (err: any) {
    const isRemote = typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
    const guidance = isRemote
      ? "The Vercel frontend is online, but the FastAPI backend is not yet connected. Deploy your backend to a cloud host (Render/Railway) or set NEXT_PUBLIC_API_URL in your Vercel Environment Variables."
      : "Cannot reach FastAPI backend. Make sure the backend server is running on port 8000 (.\\start_backend.bat).";
    throw new Error(`Backend Connection Unavailable: ${guidance}`);
  }

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
    return `${getApiBase()}/reports/${id}/pdf`;
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
    return `${getApiBase()}/analysis/xray/${id}/pdf`;
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


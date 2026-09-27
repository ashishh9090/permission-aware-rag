import { Persona, User, DocumentItem, RAGResponse, AuditLog, AuditSummary } from './types';

const API_BASE = '/api/v1';

let authToken: string | null = localStorage.getItem('rag_token');

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    localStorage.setItem('rag_token', token);
  } else {
    localStorage.removeItem('rag_token');
  }
};

export const getAuthToken = () => authToken;

const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
};

export const api = {
  // Auth & Personas
  async getPersonas(): Promise<Persona[]> {
    const res = await fetch(`${API_BASE}/auth/personas`);
    return res.json();
  },

  async login(username: string, password = 'password123') {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      throw new Error('Authentication failed');
    }
    const data = await res.json();
    setAuthToken(data.access_token);
    return data;
  },

  async getMe(): Promise<User> {
    return fetchWithAuth('/auth/me');
  },

  // Documents
  async listDocuments(): Promise<DocumentItem[]> {
    return fetchWithAuth('/documents');
  },

  async uploadDocument(formData: FormData): Promise<DocumentItem> {
    const headers: Record<string, string> = {};
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async createRawDocument(payload: {
    document_name: string;
    document_type: string;
    classification: string;
    allowed_roles: string[];
    allowed_groups: string[];
    content: string;
    summary?: string;
  }): Promise<DocumentItem> {
    return fetchWithAuth('/documents/create-raw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },

  async updatePermissions(
    docId: string,
    payload: {
      classification?: string;
      allowed_roles?: string[];
      allowed_groups?: string[];
    }
  ): Promise<DocumentItem> {
    return fetchWithAuth(`/documents/${docId}/permissions`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },

  async deleteDocument(docId: string): Promise<any> {
    return fetchWithAuth(`/documents/${docId}`, {
      method: 'DELETE',
    });
  },

  // RAG & Retrieval
  async queryRAG(
    query: string,
    simulateMidFlightRevocationDocId?: string
  ): Promise<RAGResponse> {
    return fetchWithAuth('/rag/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        top_k: 5,
        simulate_mid_flight_revocation_doc_id: simulateMidFlightRevocationDocId || undefined,
      }),
    });
  },

  // Audit
  async getAuditLogs(limit = 50, actionFilter?: string): Promise<AuditLog[]> {
    const query = new URLSearchParams({ limit: String(limit) });
    if (actionFilter) query.append('action', actionFilter);
    return fetchWithAuth(`/audit/logs?${query.toString()}`);
  },

  async getAuditSummary(): Promise<AuditSummary> {
    return fetchWithAuth('/audit/summary');
  },
};

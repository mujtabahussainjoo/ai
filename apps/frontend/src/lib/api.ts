const envBaseUrl = typeof import.meta !== 'undefined' && import.meta.env
  ? (import.meta.env as Record<string, string>).VITE_API_BASE_URL
  : '';

export const API_BASE = envBaseUrl
  ? `${envBaseUrl.replace(/\/+$/, '')}/api/v1`
  : '/api/v1';

export interface UserProfile {
  id: string;
  email: string;
  display_name: string | null;
  roles: string[];
  created_at: string;
}

export interface ConversationSummary {
  id: string;
  title: string | null;
  last_message_at: string | null;
  created_at: string;
  updated_at: string;
  agent_kind?: string;
}

export interface DocumentSummary {
  id: string;
  filename: string;
  content_type: string | null;
  size_bytes: number;
  status: string;
  chunk_count: number;
  error_message: string | null;
  created_at: string;
}

export interface MessageOut {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  model: string | null;
  created_at: string;
  token_usage?: Record<string, unknown> | null;
}

export interface ProviderStatus {
  name: string;
  display_name: string;
  description: string;
  model_suggestions: Record<string, string[]>;
  chat_unsupported: boolean;
  enabled: boolean;
  configured: boolean;
  key_fingerprint: string | null;
  default_model: string;
  model_chat: string | null;
  base_url: string | null;
  fallback_order: number | null;
  capabilities: string[];
  is_default: boolean;
}

export interface LogEntry {
  ts: string;
  level: string;
  logger: string;
  message: string;
  request_id?: string | null;
  exc_info?: string | null;
  [key: string]: unknown;
}

export interface ThirdPartyApi {
  id: string;
  name: string;
  description: string | null;
  base_url: string;
  method: string;
  code: string | null;
  key_fingerprint: string | null;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface Paginated<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export class ApiError extends Error {
  code?: string;
  status?: number;

  constructor(message: string, options: { code?: string; status?: number } = {}) {
    super(message);
    this.code = options.code;
    this.status = options.status;
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  token?: string | null;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, token } = options;
  const headers: Record<string, string> = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  let payload: unknown = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const errorPayload = (payload as { error?: { code?: string; message?: string } } | null)?.error;
    throw new ApiError(errorPayload?.message ?? `Request failed (${response.status})`, {
      code: errorPayload?.code,
      status: response.status,
    });
  }
  return (payload as { data: T }).data as T;
}

export const api = {
  get: <T>(path: string, token?: string | null) => request<T>(path, { method: 'GET', token }),
  post: <T>(path: string, body: unknown, token?: string | null) =>
    request<T>(path, { method: 'POST', body, token }),
  put: <T>(path: string, body: unknown, token?: string | null) =>
    request<T>(path, { method: 'PUT', body, token }),
  del: <T>(path: string, token?: string | null) => request<T>(path, { method: 'DELETE', token }),
};

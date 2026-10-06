import type {
  AuthResponse,
  ChatHistoryTurn,
  ChatMessage,
  ChatResponse,
  Product,
  PublicUser,
} from "./types";

const TOKEN_KEY = "cc_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(path, { ...init, headers });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return (await res.json()) as T;
}

export const api = {
  listProducts: (params: { search?: string; garment_type?: string } = {}) => {
    const q = new URLSearchParams();
    if (params.search) q.set("search", params.search);
    if (params.garment_type) q.set("garment_type", params.garment_type);
    const qs = q.toString();
    return request<Product[]>(`/api/products${qs ? `?${qs}` : ""}`);
  },
  getProduct: (id: string) => request<Product>(`/api/products/${encodeURIComponent(id)}`),
  garmentTypes: () => request<string[]>("/api/garment-types"),
  signup: (body: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    confirm_password: string;
  }) =>
    request<AuthResponse>("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  login: (body: { email: string; password: string }) =>
    request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  me: () => request<PublicUser>("/api/auth/me"),
  chat: (message: string, history: ChatMessage[], currentProductId?: string) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        history,
        current_product_id: currentProductId ?? null,
      }),
    }),
  chatHistory: () => request<ChatHistoryTurn[]>("/api/chat/history"),
};

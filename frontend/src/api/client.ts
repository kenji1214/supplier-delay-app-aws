import type { Backorder, BackorderDetail, BackorderFilters, Comment, CommentPayload } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-User-Name": localStorage.getItem("currentUser") || "poc.planner",
      ...(options.headers || {})
    }
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json();
}

export async function fetchBackorders(filters: BackorderFilters): Promise<Backorder[]> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (key === "planner_codes") {
      (value as string[]).forEach((planner) => params.append("planner_codes", planner));
      return;
    }
    if (value) params.set(key, String(value));
  });
  return request<Backorder[]>(`/api/backorders?${params.toString()}`);
}

export function fetchBackorderDetail(shipmentKey: string): Promise<BackorderDetail> {
  return request<BackorderDetail>(`/api/backorders/${encodeURIComponent(shipmentKey)}`);
}

export function fetchPlannerCodes(): Promise<string[]> {
  return request<string[]>("/api/planner-codes");
}

export function createComment(shipmentKey: string, payload: CommentPayload): Promise<Comment> {
  return request<Comment>(`/api/backorders/${encodeURIComponent(shipmentKey)}/comments`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateComment(commentId: number, payload: Partial<CommentPayload>): Promise<Comment> {
  return request<Comment>(`/api/comments/${commentId}`, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export function deleteComment(commentId: number): Promise<void> {
  return request<void>(`/api/comments/${commentId}`, { method: "DELETE" });
}

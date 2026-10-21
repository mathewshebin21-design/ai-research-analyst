"use client";

import { getToken } from "./auth";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string,
  ) {
    super(message);
  }
}

function messageFrom(detail: unknown): { message: string; code?: string } {
  if (typeof detail === "string") return { message: detail };
  if (detail && typeof detail === "object" && "code" in detail) return { message: String((detail as { code: string }).code), code: (detail as { code: string }).code };
  if (Array.isArray(detail)) return { message: detail.map((d) => d?.msg ?? "").filter(Boolean).join("; ") || "Check the form and try again." };
  return { message: "Something went wrong. Try again." };
}

export async function api<T>(path: string, init: RequestInit & { json?: unknown; asFile?: boolean } = {}): Promise<T> {
  const token = await getToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let body = init.body;
  if (init.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(init.json);
  }
  let r: Response;
  try {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { json: _json, asFile: _asFile, ...rest } = init;
    r = await fetch(`${API_URL}${path}`, { ...rest, headers, body });
  } catch {
    throw new ApiError(0, "The research service could not be reached. Check your connection and try again.");
  }
  if (!r.ok) {
    let detail: unknown;
    try {
      detail = (await r.json()).detail;
    } catch {
      detail = undefined;
    }
    const { message, code } = messageFrom(detail);
    throw new ApiError(r.status, r.status === 401 ? "Sign in to continue." : message, code);
  }
  const type = r.headers.get("content-type") ?? "";
  return (init.asFile || !type.includes("application/json") ? r.blob() : r.json()) as Promise<T>;
}

/** Reads a server-sent event stream with the auth header (EventSource cannot send one). */
export async function streamEvents(path: string, onEvent: (e: { event: string; data: string }) => void, signal: AbortSignal) {
  const token = await getToken();
  const r = await fetch(`${API_URL}${path}`, { headers: token ? { Authorization: `Bearer ${token}` } : {}, signal });
  if (!r.ok || !r.body) throw new ApiError(r.status, "Progress updates are unavailable.");
  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) return;
    buffer += decoder.decode(value, { stream: true });
    let i;
    while ((i = buffer.indexOf("\n\n")) >= 0) {
      const chunk = buffer.slice(0, i);
      buffer = buffer.slice(i + 2);
      let event = "message";
      const data: string[] = [];
      for (const line of chunk.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data.push(line.slice(5).trim());
      }
      if (data.length) onEvent({ event, data: data.join("\n") });
    }
  }
}

export function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

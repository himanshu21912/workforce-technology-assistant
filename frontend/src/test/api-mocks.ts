import { vi } from "vitest";

import type { ChatSession } from "@/features/sessions/types/session.types";
import type { ConversationMessage } from "@/features/chat/types/chat.types";

export function buildSession(overrides: Partial<ChatSession> = {}): ChatSession {
  return {
    session_id: "11111111-1111-4111-8111-111111111111",
    title: "Engineering Team Analysis",
    created_at: "2026-09-08T10:00:00Z",
    updated_at: "2026-09-08T10:05:00Z",
    message_count: 0,
    ...overrides,
  };
}

export function buildMessage(
  overrides: Partial<ConversationMessage> = {},
): ConversationMessage {
  return {
    id: "22222222-2222-4222-8222-222222222222",
    role: "user",
    content: "Which internal employees know Python?",
    created_at: "2026-09-08T10:01:00Z",
    metadata: {},
    ...overrides,
  };
}

export const healthPayload = {
  status: "ok",
  service: {
    name: "Workforce Technology Assistant API",
    version: "0.6.0",
    environment: "development",
  },
  dependencies: {
    postgres: { status: "connected", message: null },
    redis: { status: "connected", message: null },
    ollama: { status: "connected", message: null },
  },
};

export interface RouteHandler {
  (request: { method: string; url: string; body: unknown }):
    | Response
    | Promise<Response>;
}

export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

/**
 * Installs a fetch mock that dispatches on "METHOD /path". Any request
 * without a handler fails loudly so tests cannot silently pass.
 */
export function mockApi(routes: Record<string, RouteHandler>) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input.toString();
    const method = (init?.method ?? "GET").toUpperCase();
    const path = new URL(url).pathname;
    const search = new URL(url).search;

    const handler =
      routes[`${method} ${path}${search}`] ?? routes[`${method} ${path}`];

    if (!handler) {
      throw new Error(`Unhandled request: ${method} ${path}${search}`);
    }

    const body = init?.body ? JSON.parse(String(init.body)) : null;

    return handler({ method, url, body });
  });

  vi.stubGlobal("fetch", fetchMock);

  return fetchMock;
}

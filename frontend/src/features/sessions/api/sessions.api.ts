import { apiEndpoints } from "@/lib/api/endpoints";
import { apiRequest } from "@/lib/api/api-client";
import {
  chatSessionSchema,
  deleteSessionResponseSchema,
  sessionHistorySchema,
  sessionListResponseSchema,
} from "@/features/sessions/schemas/session.schema";
import type {
  ChatSession,
  DeleteSessionResponse,
  SessionHistory,
  SessionListResponse,
} from "@/features/sessions/types/session.types";

export const SESSION_LIST_LIMIT = 50;

export function listSessions(
  signal?: AbortSignal,
  limit = SESSION_LIST_LIMIT,
): Promise<SessionListResponse> {
  return apiRequest({
    path: apiEndpoints.sessionList(limit),
    schema: sessionListResponseSchema,
    signal,
  });
}

export function createSession(
  title?: string,
  signal?: AbortSignal,
): Promise<ChatSession> {
  return apiRequest({
    method: "POST",
    path: apiEndpoints.sessions(),
    body: { title: title ?? null },
    schema: chatSessionSchema,
    signal,
  });
}

export function getSessionHistory(
  sessionId: string,
  signal?: AbortSignal,
): Promise<SessionHistory> {
  return apiRequest({
    path: apiEndpoints.session(sessionId),
    schema: sessionHistorySchema,
    signal,
  });
}

export function renameSession(
  sessionId: string,
  title: string,
  signal?: AbortSignal,
): Promise<ChatSession> {
  return apiRequest({
    method: "PATCH",
    path: apiEndpoints.session(sessionId),
    body: { title },
    schema: chatSessionSchema,
    signal,
  });
}

export function deleteSession(
  sessionId: string,
  signal?: AbortSignal,
): Promise<DeleteSessionResponse> {
  return apiRequest({
    method: "DELETE",
    path: apiEndpoints.session(sessionId),
    schema: deleteSessionResponseSchema,
    signal,
  });
}

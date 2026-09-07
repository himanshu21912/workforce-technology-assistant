export const API_V1_PREFIX = "/api/v1";

/**
 * Single source of truth for every backend path used by the client.
 */
export const apiEndpoints = {
  health: () => `${API_V1_PREFIX}/health`,
  ask: () => `${API_V1_PREFIX}/ask`,
  sessions: () => `${API_V1_PREFIX}/sessions`,
  sessionList: (limit: number) =>
    `${API_V1_PREFIX}/sessions?limit=${encodeURIComponent(limit)}`,
  session: (sessionId: string) =>
    `${API_V1_PREFIX}/sessions/${encodeURIComponent(sessionId)}`,
} as const;

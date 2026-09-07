import type { ChatSession } from "@/features/sessions/types/session.types";

/** Local, case-insensitive filtering of the backend-ordered session list. */
export function filterSessions(
  sessions: ChatSession[],
  searchTerm: string,
): ChatSession[] {
  const normalizedTerm = searchTerm.trim().toLowerCase();

  if (!normalizedTerm) {
    return sessions;
  }

  return sessions.filter((session) =>
    session.title.toLowerCase().includes(normalizedTerm),
  );
}

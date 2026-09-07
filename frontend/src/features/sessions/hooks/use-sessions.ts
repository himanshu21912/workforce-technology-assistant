"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { toErrorMessage } from "@/lib/api/errors";
import { useIsMounted } from "@/hooks/use-is-mounted";
import {
  createSession as createSessionRequest,
  deleteSession as deleteSessionRequest,
  listSessions,
  renameSession as renameSessionRequest,
} from "@/features/sessions/api/sessions.api";
import type { ChatSession } from "@/features/sessions/types/session.types";

export interface UseSessionsResult {
  sessions: ChatSession[];
  isLoading: boolean;
  error: string | null;
  isCreating: boolean;
  pendingDeleteId: string | null;
  pendingRenameId: string | null;
  refresh: () => Promise<ChatSession[]>;
  createSession: (title?: string) => Promise<ChatSession>;
  renameSession: (sessionId: string, title: string) => Promise<ChatSession>;
  deleteSession: (sessionId: string) => Promise<void>;
  removeSessionLocally: (sessionId: string) => void;
}

export function useSessions(): UseSessionsResult {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const [pendingRenameId, setPendingRenameId] = useState<string | null>(null);

  const isMounted = useIsMounted();
  const requestIdRef = useRef(0);

  const refresh = useCallback(async (): Promise<ChatSession[]> => {
    const requestId = ++requestIdRef.current;

    try {
      const response = await listSessions();

      if (!isMounted() || requestId !== requestIdRef.current) {
        return response.sessions;
      }

      setSessions(response.sessions);
      setError(null);

      return response.sessions;
    } catch (caught) {
      if (isMounted() && requestId === requestIdRef.current) {
        setError(toErrorMessage(caught, "Sessions could not be loaded."));
      }

      throw caught;
    } finally {
      if (isMounted() && requestId === requestIdRef.current) {
        setIsLoading(false);
      }
    }
  }, [isMounted]);

  useEffect(() => {
    void refresh().catch(() => {
      // Surfaced through the error state.
    });
  }, [refresh]);

  const createSession = useCallback(
    async (title?: string): Promise<ChatSession> => {
      setIsCreating(true);

      try {
        const session = await createSessionRequest(title);

        if (isMounted()) {
          setSessions((current) => [
            session,
            ...current.filter(
              (item) => item.session_id !== session.session_id,
            ),
          ]);
          setError(null);
        }

        return session;
      } finally {
        if (isMounted()) {
          setIsCreating(false);
        }
      }
    },
    [isMounted],
  );

  const renameSession = useCallback(
    async (sessionId: string, title: string): Promise<ChatSession> => {
      setPendingRenameId(sessionId);

      try {
        const updated = await renameSessionRequest(sessionId, title);

        if (isMounted()) {
          setSessions((current) =>
            current.map((item) =>
              item.session_id === updated.session_id ? updated : item,
            ),
          );
        }

        return updated;
      } finally {
        if (isMounted()) {
          setPendingRenameId(null);
        }
      }
    },
    [isMounted],
  );

  const removeSessionLocally = useCallback((sessionId: string) => {
    setSessions((current) =>
      current.filter((item) => item.session_id !== sessionId),
    );
  }, []);

  const deleteSession = useCallback(
    async (sessionId: string): Promise<void> => {
      setPendingDeleteId(sessionId);

      try {
        await deleteSessionRequest(sessionId);

        if (isMounted()) {
          removeSessionLocally(sessionId);
        }
      } finally {
        if (isMounted()) {
          setPendingDeleteId(null);
        }
      }
    },
    [isMounted, removeSessionLocally],
  );

  return {
    sessions,
    isLoading,
    error,
    isCreating,
    pendingDeleteId,
    pendingRenameId,
    refresh,
    createSession,
    renameSession,
    deleteSession,
    removeSessionLocally,
  };
}

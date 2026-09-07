"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { isApiError, toErrorMessage } from "@/lib/api/errors";
import { useIsMounted } from "@/hooks/use-is-mounted";
import { getSessionHistory } from "@/features/sessions/api/sessions.api";
import type { SessionHistory } from "@/features/sessions/types/session.types";

interface HistoryState {
  sessionId: string;
  isLoading: boolean;
  history: SessionHistory | null;
  error: string | null;
  isNotFound: boolean;
}

export interface UseSessionHistoryResult {
  history: SessionHistory | null;
  isLoading: boolean;
  error: string | null;
  isNotFound: boolean;
  reload: () => Promise<void>;
  applyHistory: (history: SessionHistory) => void;
}

/**
 * Loads the conversation history for the selected session. State is keyed
 * by session id, so a stale response can never be shown for a session the
 * user has already switched away from.
 */
export function useSessionHistory(
  sessionId: string | null,
): UseSessionHistoryResult {
  const [state, setState] = useState<HistoryState | null>(null);

  const isMounted = useIsMounted();
  const abortControllerRef = useRef<AbortController | null>(null);

  const load = useCallback(
    async (targetSessionId: string) => {
      abortControllerRef.current?.abort();

      const controller = new AbortController();
      abortControllerRef.current = controller;

      setState({
        sessionId: targetSessionId,
        isLoading: true,
        history: null,
        error: null,
        isNotFound: false,
      });

      try {
        const history = await getSessionHistory(
          targetSessionId,
          controller.signal,
        );

        if (!isMounted() || controller.signal.aborted) {
          return;
        }

        setState({
          sessionId: targetSessionId,
          isLoading: false,
          history,
          error: null,
          isNotFound: false,
        });
      } catch (caught) {
        if (controller.signal.aborted || !isMounted()) {
          return;
        }

        const notFound = isApiError(caught) && caught.isNotFound;

        setState({
          sessionId: targetSessionId,
          isLoading: false,
          history: null,
          error: notFound
            ? null
            : toErrorMessage(caught, "This conversation could not be loaded."),
          isNotFound: notFound,
        });
      }
    },
    [isMounted],
  );

  useEffect(() => {
    if (!sessionId) {
      return;
    }

    async function loadSelectedSession(targetSessionId: string) {
      await load(targetSessionId);
    }

    void loadSelectedSession(sessionId);

    return () => {
      abortControllerRef.current?.abort();
    };
  }, [sessionId, load]);

  const reload = useCallback(async () => {
    if (sessionId) {
      await load(sessionId);
    }
  }, [sessionId, load]);

  const applyHistory = useCallback((next: SessionHistory) => {
    setState({
      sessionId: next.session.session_id,
      isLoading: false,
      history: next,
      error: null,
      isNotFound: false,
    });
  }, []);

  const current = state && state.sessionId === sessionId ? state : null;

  return {
    history: current?.history ?? null,
    // A session with no state yet is still waiting for its first load.
    isLoading: sessionId !== null && (current === null || current.isLoading),
    error: current?.error ?? null,
    isNotFound: current?.isNotFound ?? false,
    reload,
    applyHistory,
  };
}

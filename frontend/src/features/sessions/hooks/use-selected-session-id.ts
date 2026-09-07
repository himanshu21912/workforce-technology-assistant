"use client";

import { useCallback, useSyncExternalStore } from "react";

const SESSION_QUERY_PARAM = "session";

const listeners = new Set<() => void>();

function notifyListeners(): void {
  for (const listener of listeners) {
    listener();
  }
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  window.addEventListener("popstate", listener);

  return () => {
    listeners.delete(listener);
    window.removeEventListener("popstate", listener);
  };
}

function readSessionIdFromUrl(): string | null {
  const value = new URLSearchParams(window.location.search).get(
    SESSION_QUERY_PARAM,
  );

  return value && value.trim() ? value : null;
}

export interface UseSelectedSessionIdResult {
  selectedSessionId: string | null;
  /** True until the browser URL has been read after hydration. */
  isRestoring: boolean;
  selectSession: (sessionId: string | null) => void;
}

/**
 * Keeps the selected session in the `?session=` query parameter. The URL
 * is an external store, so server and client markup stay consistent and
 * the value survives a page reload.
 */
export function useSelectedSessionId(): UseSelectedSessionIdResult {
  const isHydrated = useSyncExternalStore(
    subscribe,
    () => true,
    () => false,
  );

  const selectedSessionId = useSyncExternalStore(
    subscribe,
    readSessionIdFromUrl,
    () => null,
  );

  const selectSession = useCallback((sessionId: string | null) => {
    const url = new URL(window.location.href);

    if (sessionId) {
      url.searchParams.set(SESSION_QUERY_PARAM, sessionId);
    } else {
      url.searchParams.delete(SESSION_QUERY_PARAM);
    }

    window.history.replaceState(window.history.state, "", url.toString());
    notifyListeners();
  }, []);

  return {
    selectedSessionId,
    isRestoring: !isHydrated,
    selectSession,
  };
}

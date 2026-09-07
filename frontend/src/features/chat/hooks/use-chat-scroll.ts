"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const BOTTOM_THRESHOLD_PX = 80;

interface UseChatScrollOptions {
  /** Changes whenever the rendered conversation changes. */
  messageCount: number;
  /** Changes when a different conversation is displayed. */
  sessionId: string | null;
}

interface PinnedState {
  sessionId: string | null;
  isPinned: boolean;
}

export interface UseChatScrollResult {
  containerRef: React.RefObject<HTMLDivElement | null>;
  isPinnedToBottom: boolean;
  scrollToBottom: (behavior?: ScrollBehavior) => void;
}

/**
 * Keeps the newest message visible without yanking the viewport away from
 * a user who has scrolled up to read earlier messages. Each conversation
 * starts pinned to the bottom again.
 */
export function useChatScroll({
  messageCount,
  sessionId,
}: UseChatScrollOptions): UseChatScrollResult {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [pinnedState, setPinnedState] = useState<PinnedState>({
    sessionId,
    isPinned: true,
  });
  const isPinnedRef = useRef(true);

  const isPinnedToBottom =
    pinnedState.sessionId === sessionId ? pinnedState.isPinned : true;

  const scrollToBottom = useCallback((behavior: ScrollBehavior = "smooth") => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    container.scrollTo({ top: container.scrollHeight, behavior });
  }, []);

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    const handleScroll = () => {
      const distanceFromBottom =
        container.scrollHeight - container.scrollTop - container.clientHeight;
      const isPinned = distanceFromBottom <= BOTTOM_THRESHOLD_PX;

      isPinnedRef.current = isPinned;
      setPinnedState({ sessionId, isPinned });
    };

    container.addEventListener("scroll", handleScroll, { passive: true });

    return () => {
      container.removeEventListener("scroll", handleScroll);
    };
  }, [sessionId]);

  // Open every conversation at its newest message.
  useEffect(() => {
    isPinnedRef.current = true;
    scrollToBottom("auto");
  }, [sessionId, scrollToBottom]);

  useEffect(() => {
    if (isPinnedRef.current) {
      scrollToBottom("smooth");
    }
  }, [messageCount, scrollToBottom]);

  return { containerRef, isPinnedToBottom, scrollToBottom };
}

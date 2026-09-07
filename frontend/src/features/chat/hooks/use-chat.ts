"use client";

import { useCallback, useState } from "react";

import { isApiError, toErrorMessage } from "@/lib/api/errors";
import { useIsMounted } from "@/hooks/use-is-mounted";
import { askQuestion } from "@/features/chat/api/ask.api";
import { getSessionHistory } from "@/features/sessions/api/sessions.api";
import type { SessionHistory } from "@/features/sessions/types/session.types";
import type {
  ChatMessage,
  OptimisticMessage,
} from "@/features/chat/types/chat.types";

interface UseChatOptions {
  sessionId: string | null;
  serverMessages: ChatMessage[];
  /** Replaces the authoritative history once the backend confirms a turn. */
  applyHistory: (history: SessionHistory) => void;
  /** Refreshes the sidebar, whose titles and counts change after a turn. */
  onTurnCompleted: () => void;
  /** Called when the backend reports the session no longer exists. */
  onSessionMissing: (sessionId: string) => void;
}

interface TurnState {
  sessionId: string;
  optimisticMessages: OptimisticMessage[];
  isSending: boolean;
  error: string | null;
  failedQuestion: string | null;
}

export interface UseChatResult {
  messages: ChatMessage[];
  isSending: boolean;
  error: string | null;
  failedQuestion: string | null;
  sendQuestion: (question: string) => Promise<void>;
  retryFailedQuestion: () => Promise<void>;
  dismissError: () => void;
}

function createOptimisticUserMessage(question: string): OptimisticMessage {
  return {
    id: `optimistic-user-${Date.now()}`,
    role: "user",
    content: question,
    created_at: new Date().toISOString(),
    metadata: {},
    pending: true,
  };
}

/**
 * Owns the in-flight question for the selected session. Turn state is
 * keyed by session id so switching sessions never leaks a pending
 * question or error into another conversation.
 */
export function useChat({
  sessionId,
  serverMessages,
  applyHistory,
  onTurnCompleted,
  onSessionMissing,
}: UseChatOptions): UseChatResult {
  const [turn, setTurn] = useState<TurnState | null>(null);

  const isMounted = useIsMounted();

  const currentTurn = turn && turn.sessionId === sessionId ? turn : null;
  const isSending = currentTurn?.isSending ?? false;
  const failedQuestion = currentTurn?.failedQuestion ?? null;

  const sendQuestion = useCallback(
    async (rawQuestion: string) => {
      const question = rawQuestion.trim();

      if (!question || !sessionId || isSending) {
        return;
      }

      const targetSessionId = sessionId;

      setTurn({
        sessionId: targetSessionId,
        optimisticMessages: [createOptimisticUserMessage(question)],
        isSending: true,
        error: null,
        failedQuestion: null,
      });

      try {
        const answer = await askQuestion({
          session_id: targetSessionId,
          question,
          context: null,
        });

        let freshHistory: SessionHistory | null = null;

        try {
          freshHistory = await getSessionHistory(targetSessionId);
        } catch {
          // The answer is already available; history reconciles on the
          // next successful load.
        }

        if (!isMounted()) {
          return;
        }

        if (
          freshHistory &&
          freshHistory.session.session_id === targetSessionId
        ) {
          // Authoritative history replaces the optimistic messages in the
          // same update, so no turn is ever rendered twice.
          applyHistory(freshHistory);
          setTurn(null);
        } else {
          setTurn({
            sessionId: targetSessionId,
            optimisticMessages: [
              createOptimisticUserMessage(question),
              {
                id: `optimistic-assistant-${Date.now()}`,
                role: "assistant",
                content: answer.answer,
                created_at: new Date().toISOString(),
                metadata: {
                  source: answer.source,
                  tools_used: answer.tools_used,
                  cache_hit: answer.cache_hit,
                  similarity_score: answer.similarity_score,
                  model_name: answer.model_name,
                },
                pending: true,
              },
            ],
            isSending: false,
            error: null,
            failedQuestion: null,
          });
        }

        onTurnCompleted();
      } catch (caught) {
        if (!isMounted()) {
          return;
        }

        setTurn({
          sessionId: targetSessionId,
          optimisticMessages: [],
          isSending: false,
          error: toErrorMessage(
            caught,
            "The assistant could not answer this question.",
          ),
          failedQuestion: question,
        });

        if (isApiError(caught) && caught.isNotFound) {
          onSessionMissing(targetSessionId);
        }
      }
    },
    [
      sessionId,
      isSending,
      isMounted,
      applyHistory,
      onTurnCompleted,
      onSessionMissing,
    ],
  );

  const retryFailedQuestion = useCallback(async () => {
    if (failedQuestion) {
      await sendQuestion(failedQuestion);
    }
  }, [failedQuestion, sendQuestion]);

  const dismissError = useCallback(() => {
    setTurn(null);
  }, []);

  return {
    messages: [
      ...serverMessages,
      ...(currentTurn?.optimisticMessages ?? []),
    ],
    isSending,
    error: currentTurn?.error ?? null,
    failedQuestion,
    sendQuestion,
    retryFailedQuestion,
    dismissError,
  };
}

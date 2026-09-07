"use client";

import type { RefObject } from "react";
import { Info, Menu, Pencil, RefreshCw } from "lucide-react";

import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/ui/icon-button";
import { Skeleton } from "@/components/ui/skeleton";
import { MessageList } from "@/features/chat/components/message-list";
import {
  QuestionComposer,
  type QuestionComposerHandle,
} from "@/features/chat/components/question-composer";
import type { ChatMessage } from "@/features/chat/types/chat.types";
import type { ChatSession } from "@/features/sessions/types/session.types";

interface ChatPanelProps {
  session: ChatSession | null;
  messages: ChatMessage[];
  isLoadingHistory: boolean;
  isSending: boolean;
  historyError: string | null;
  sendError: string | null;
  canRetrySend: boolean;
  composerRef: RefObject<QuestionComposerHandle | null>;
  onSubmitQuestion: (question: string) => void;
  onSelectPrompt: (prompt: string) => void;
  onRefresh: () => void;
  onRetryHistory: () => void;
  onRetrySend: () => void;
  onDismissSendError: () => void;
  onRenameSession: () => void;
  onOpenSessions: () => void;
  onOpenProjectInfo: () => void;
}

export function ChatPanel({
  session,
  messages,
  isLoadingHistory,
  isSending,
  historyError,
  sendError,
  canRetrySend,
  composerRef,
  onSubmitQuestion,
  onSelectPrompt,
  onRefresh,
  onRetryHistory,
  onRetrySend,
  onDismissSendError,
  onRenameSession,
  onOpenSessions,
  onOpenProjectInfo,
}: ChatPanelProps) {
  return (
    <section
      aria-label="Conversation"
      className="flex h-full min-h-0 flex-col overflow-hidden rounded-none border-slate-200 bg-white lg:rounded-xl lg:border"
    >
      <header className="flex items-center gap-3 border-b border-slate-100 px-4 py-3 sm:px-6">
        <IconButton
          label="Open sessions"
          onClick={onOpenSessions}
          className="lg:hidden"
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </IconButton>

        <div className="flex min-w-0 flex-1 items-center gap-3">
          {session ? (
            <>
              <h1 className="truncate text-base font-semibold text-slate-900">
                {session.title}
              </h1>
              <span className="hidden shrink-0 items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 sm:inline-flex">
                <span
                  className="h-1.5 w-1.5 rounded-full bg-emerald-500"
                  aria-hidden="true"
                />
                Active
              </span>
              <IconButton
                label="Rename session"
                onClick={onRenameSession}
                className="max-sm:hidden"
              >
                <Pencil className="h-4 w-4" aria-hidden="true" />
              </IconButton>
            </>
          ) : isLoadingHistory ? (
            <Skeleton className="h-5 w-48" />
          ) : (
            <h1 className="truncate text-base font-semibold text-slate-900">
              No session selected
            </h1>
          )}
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={onRefresh}
            disabled={!session || isLoadingHistory}
            className="max-sm:hidden"
          >
            <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />
            Refresh
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={onOpenProjectInfo}
            className="xl:hidden"
          >
            <Info className="h-3.5 w-3.5" aria-hidden="true" />
            <span className="hidden sm:inline">Session Info</span>
          </Button>
        </div>
      </header>

      {historyError ? (
        <div className="px-5 pt-4 sm:px-6">
          <Alert
            tone="error"
            title="Conversation unavailable"
            action={
              <Button variant="secondary" size="sm" onClick={onRetryHistory}>
                Retry
              </Button>
            }
          >
            {historyError}
          </Alert>
        </div>
      ) : null}

      <MessageList
        messages={messages}
        sessionId={session?.session_id ?? null}
        isLoadingHistory={isLoadingHistory}
        isAwaitingAnswer={isSending}
        onSelectPrompt={onSelectPrompt}
      />

      <p aria-live="polite" className="sr-only">
        {isSending ? "Generating an answer" : ""}
      </p>

      {sendError ? (
        <div className="px-5 pb-1 sm:px-6">
          <Alert
            tone="error"
            title="The question could not be answered"
            action={
              <div className="flex gap-2">
                {canRetrySend ? (
                  <Button variant="secondary" size="sm" onClick={onRetrySend}>
                    Retry
                  </Button>
                ) : null}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onDismissSendError}
                >
                  Dismiss
                </Button>
              </div>
            }
          >
            {sendError}
          </Alert>
        </div>
      ) : null}

      <QuestionComposer
        ref={composerRef}
        isSending={isSending}
        isSessionReady={Boolean(session)}
        onSubmit={onSubmitQuestion}
      />
    </section>
  );
}

"use client";

import { MessageSquarePlus, RefreshCw } from "lucide-react";

import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { SessionListItem } from "@/features/sessions/components/session-list-item";
import type { ChatSession } from "@/features/sessions/types/session.types";

interface SessionListProps {
  sessions: ChatSession[];
  selectedSessionId: string | null;
  isLoading: boolean;
  error: string | null;
  searchTerm: string;
  pendingDeleteId: string | null;
  onRetry: () => void;
  onSelect: (sessionId: string) => void;
  onRename: (session: ChatSession) => void;
  onDelete: (session: ChatSession) => void;
}

export function SessionList({
  sessions,
  selectedSessionId,
  isLoading,
  error,
  searchTerm,
  pendingDeleteId,
  onRetry,
  onSelect,
  onRename,
  onDelete,
}: SessionListProps) {
  if (isLoading) {
    return (
      <div className="space-y-2 px-1" aria-busy="true" aria-live="polite">
        <span className="sr-only">Loading sessions</span>
        {[0, 1, 2, 3].map((item) => (
          <div key={item} className="space-y-2 rounded-lg p-2.5">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        tone="error"
        title="Sessions unavailable"
        action={
          <Button variant="secondary" size="sm" onClick={onRetry}>
            <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />
            Retry
          </Button>
        }
      >
        {error}
      </Alert>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-200 px-4 py-8 text-center">
        <MessageSquarePlus
          className="mx-auto h-6 w-6 text-slate-400"
          aria-hidden="true"
        />
        <p className="mt-2 text-sm font-medium text-slate-700">
          {searchTerm ? "No matching sessions" : "No sessions yet"}
        </p>
        <p className="mt-1 text-xs text-slate-500">
          {searchTerm
            ? "Try a different search term."
            : "Start a new session to ask your first question."}
        </p>
      </div>
    );
  }

  return (
    <ul aria-label="Conversation sessions" className="space-y-1">
      {sessions.map((session) => (
        <SessionListItem
          key={session.session_id}
          session={session}
          isSelected={session.session_id === selectedSessionId}
          isDeleting={pendingDeleteId === session.session_id}
          onSelect={onSelect}
          onRename={onRename}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}

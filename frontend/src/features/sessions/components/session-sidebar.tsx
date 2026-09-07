"use client";

import { useState } from "react";
import { Bot, Plus, Search, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { SessionList } from "@/features/sessions/components/session-list";
import { filterSessions } from "@/features/sessions/utils/filter-sessions";
import type { ChatSession } from "@/features/sessions/types/session.types";

interface SessionSidebarProps {
  sessions: ChatSession[];
  selectedSessionId: string | null;
  isLoading: boolean;
  isCreating: boolean;
  error: string | null;
  pendingDeleteId: string | null;
  onRetry: () => void;
  onCreateSession: () => void;
  onSelectSession: (sessionId: string) => void;
  onRenameSession: (session: ChatSession) => void;
  onDeleteSession: (session: ChatSession) => void;
  onClearAllSessions: () => void;
  /** The drawer supplies its own heading, so the brand block is dropped. */
  showBrandHeader?: boolean;
}

export function SessionSidebar({
  sessions,
  selectedSessionId,
  isLoading,
  isCreating,
  error,
  pendingDeleteId,
  onRetry,
  onCreateSession,
  onSelectSession,
  onRenameSession,
  onDeleteSession,
  onClearAllSessions,
  showBrandHeader = true,
}: SessionSidebarProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const visibleSessions = filterSessions(sessions, searchTerm);

  return (
    <div className="flex h-full flex-col bg-white">
      {showBrandHeader ? (
        <div className="flex items-center gap-3 bg-sidebar-header px-5 py-4">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
            <Bot className="h-5 w-5 text-white" aria-hidden="true" />
          </span>
          <span>
            <span className="block text-sm font-semibold text-white">
              Workforce Assistant
            </span>
            <span className="block text-xs text-slate-300">
              AI-Powered Knowledge Hub
            </span>
          </span>
        </div>
      ) : null}

      <div className="flex min-h-0 flex-1 flex-col px-4 py-4">
        <h2 className="px-1 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          Sessions
        </h2>

        <Button
          onClick={onCreateSession}
          disabled={isCreating}
          className="mt-3 w-full"
        >
          {isCreating ? (
            <Spinner className="h-4 w-4" />
          ) : (
            <Plus className="h-4 w-4" aria-hidden="true" />
          )}
          New Session
        </Button>

        <div className="relative mt-3">
          <label htmlFor="session-search" className="sr-only">
            Search sessions
          </label>
          <input
            id="session-search"
            type="search"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Search sessions..."
            className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-3 pr-9 text-sm text-slate-800 placeholder:text-slate-400 focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-brand"
          />
          <Search
            className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
            aria-hidden="true"
          />
        </div>

        <div className="scroll-panel mt-3 min-h-0 flex-1 overflow-y-auto pr-1">
          <SessionList
            sessions={visibleSessions}
            selectedSessionId={selectedSessionId}
            isLoading={isLoading}
            error={error}
            searchTerm={searchTerm}
            pendingDeleteId={pendingDeleteId}
            onRetry={onRetry}
            onSelect={onSelectSession}
            onRename={onRenameSession}
            onDelete={onDeleteSession}
          />
        </div>
      </div>

      <div className="border-t border-slate-100 px-4 py-4">
        <Button
          variant="danger"
          onClick={onClearAllSessions}
          disabled={sessions.length === 0}
          className="w-full"
        >
          <Trash2 className="h-4 w-4" aria-hidden="true" />
          Clear All Sessions
        </Button>

        {selectedSessionId ? (
          <div className="mt-3 rounded-lg bg-panel-muted px-3 py-2.5">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              Current Session
            </p>
            <p className="mt-1 break-all font-mono text-[11px] text-slate-600">
              {selectedSessionId}
            </p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

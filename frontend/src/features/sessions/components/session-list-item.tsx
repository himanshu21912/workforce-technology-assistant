"use client";

import { MessageSquare } from "lucide-react";

import { cn } from "@/lib/cn";
import { formatShortDateTime } from "@/lib/format/date";
import { Spinner } from "@/components/ui/spinner";
import { SessionActionsMenu } from "@/features/sessions/components/session-actions-menu";
import type { ChatSession } from "@/features/sessions/types/session.types";

interface SessionListItemProps {
  session: ChatSession;
  isSelected: boolean;
  isDeleting: boolean;
  onSelect: (sessionId: string) => void;
  onRename: (session: ChatSession) => void;
  onDelete: (session: ChatSession) => void;
}

export function SessionListItem({
  session,
  isSelected,
  isDeleting,
  onSelect,
  onRename,
  onDelete,
}: SessionListItemProps) {
  return (
    <li
      className={cn(
        "group relative rounded-lg border transition-colors",
        isSelected
          ? "border-brand/30 bg-brand-soft"
          : "border-transparent hover:bg-slate-50",
      )}
    >
      <div className="flex items-start gap-2 p-2.5">
        <button
          type="button"
          onClick={() => onSelect(session.session_id)}
          aria-current={isSelected ? "true" : undefined}
          className="flex min-w-0 flex-1 items-start gap-2.5 text-left focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
        >
          <MessageSquare
            className={cn(
              "mt-0.5 h-4 w-4 shrink-0",
              isSelected ? "text-brand" : "text-slate-400",
            )}
            aria-hidden="true"
          />
          <span className="min-w-0 flex-1">
            <span
              className={cn(
                "block truncate text-sm font-medium",
                isSelected ? "text-brand-strong" : "text-slate-800",
              )}
            >
              {session.title}
            </span>
            <span className="mt-0.5 flex items-center gap-1.5 truncate whitespace-nowrap text-xs text-slate-500">
              <span>{formatShortDateTime(session.updated_at)}</span>
              <span aria-hidden="true">·</span>
              <span>
                {session.message_count}{" "}
                {session.message_count === 1 ? "msg" : "msgs"}
              </span>
            </span>
          </span>
        </button>

        {isDeleting ? (
          <Spinner className="mt-1 h-4 w-4 text-slate-400" />
        ) : (
          <SessionActionsMenu
            sessionTitle={session.title}
            onRename={() => onRename(session)}
            onDelete={() => onDelete(session)}
          />
        )}
      </div>
    </li>
  );
}

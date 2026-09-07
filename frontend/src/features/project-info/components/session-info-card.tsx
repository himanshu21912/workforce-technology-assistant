"use client";

import { useState } from "react";
import { Check, Copy, MessageSquare, Clock, Hash } from "lucide-react";

import { IconButton } from "@/components/ui/icon-button";
import { formatDateTime } from "@/lib/format/date";
import type { ChatSession } from "@/features/sessions/types/session.types";

interface SessionInfoCardProps {
  session: ChatSession | null;
  cacheHitCount: number;
}

export function SessionInfoCard({
  session,
  cacheHitCount,
}: SessionInfoCardProps) {
  const [hasCopied, setHasCopied] = useState(false);

  if (!session) {
    return (
      <section
        aria-label="Session information"
        className="rounded-xl border border-slate-200 bg-white p-4"
      >
        <h2 className="text-sm font-semibold text-slate-900">
          Session Information
        </h2>
        <p className="mt-2 text-sm text-slate-600">
          Select or create a session to see its details.
        </p>
      </section>
    );
  }

  const copySessionId = async () => {
    try {
      await navigator.clipboard.writeText(session.session_id);
      setHasCopied(true);
      window.setTimeout(() => setHasCopied(false), 2000);
    } catch {
      setHasCopied(false);
    }
  };

  return (
    <section
      aria-label="Session information"
      className="rounded-xl border border-slate-200 bg-white p-4"
    >
      <h2 className="text-sm font-semibold text-slate-900">
        Session Information
      </h2>

      <dl className="mt-3 space-y-2.5 text-sm">
        <div className="flex items-start justify-between gap-3">
          <dt className="flex items-center gap-2 text-slate-600">
            <Hash className="h-3.5 w-3.5 text-slate-400" aria-hidden="true" />
            Session ID
          </dt>
          <dd className="flex min-w-0 items-center gap-1">
            <span className="truncate font-mono text-[11px] text-slate-700">
              {session.session_id}
            </span>
            <IconButton
              label="Copy session ID"
              onClick={copySessionId}
              className="h-6 w-6"
            >
              {hasCopied ? (
                <Check className="h-3.5 w-3.5 text-emerald-600" aria-hidden="true" />
              ) : (
                <Copy className="h-3.5 w-3.5" aria-hidden="true" />
              )}
            </IconButton>
          </dd>
        </div>

        <div className="flex items-center justify-between gap-3">
          <dt className="flex items-center gap-2 text-slate-600">
            <Clock className="h-3.5 w-3.5 text-slate-400" aria-hidden="true" />
            Created
          </dt>
          <dd className="text-slate-800">{formatDateTime(session.created_at)}</dd>
        </div>

        <div className="flex items-center justify-between gap-3">
          <dt className="flex items-center gap-2 text-slate-600">
            <Clock className="h-3.5 w-3.5 text-slate-400" aria-hidden="true" />
            Last activity
          </dt>
          <dd className="text-slate-800">{formatDateTime(session.updated_at)}</dd>
        </div>

        <div className="flex items-center justify-between gap-3">
          <dt className="flex items-center gap-2 text-slate-600">
            <MessageSquare
              className="h-3.5 w-3.5 text-slate-400"
              aria-hidden="true"
            />
            Messages
          </dt>
          <dd className="text-slate-800">{session.message_count}</dd>
        </div>

        <div className="flex items-center justify-between gap-3">
          <dt className="text-slate-600">Cache hits</dt>
          <dd className="text-slate-800">
            {cacheHitCount} in this conversation
          </dd>
        </div>
      </dl>
    </section>
  );
}

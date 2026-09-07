"use client";

import { useEffect } from "react";
import { Info, X } from "lucide-react";

import { IconButton } from "@/components/ui/icon-button";

interface ToastProps {
  message: string | null;
  onDismiss: () => void;
  durationMs?: number;
}

/** Transient, non-blocking notification announced politely. */
export function Toast({ message, onDismiss, durationMs = 6000 }: ToastProps) {
  useEffect(() => {
    if (!message) {
      return;
    }

    const timeout = window.setTimeout(onDismiss, durationMs);

    return () => window.clearTimeout(timeout);
  }, [message, onDismiss, durationMs]);

  if (!message) {
    return null;
  }

  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed bottom-5 left-1/2 z-50 flex max-w-md -translate-x-1/2 items-start gap-2 rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-700 shadow-lg"
    >
      <Info className="mt-0.5 h-4 w-4 shrink-0 text-brand" aria-hidden="true" />
      <span className="min-w-0 flex-1">{message}</span>
      <IconButton label="Dismiss notification" onClick={onDismiss} className="h-6 w-6">
        <X className="h-3.5 w-3.5" aria-hidden="true" />
      </IconButton>
    </div>
  );
}

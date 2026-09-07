"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Spinner } from "@/components/ui/spinner";
import { SESSION_TITLE_MAX_LENGTH } from "@/features/chat/constants/suggested-prompts";
import type { ChatSession } from "@/features/sessions/types/session.types";

interface RenameSessionDialogProps {
  session: ChatSession | null;
  isSaving: boolean;
  error: string | null;
  onSubmit: (title: string) => void;
  onCancel: () => void;
}

export function RenameSessionDialog({
  session,
  isSaving,
  error,
  onSubmit,
  onCancel,
}: RenameSessionDialogProps) {
  const [title, setTitle] = useState(session?.title ?? "");

  const trimmedTitle = title.trim();

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (trimmedTitle) {
      onSubmit(trimmedTitle);
    }
  };

  return (
    <Modal
      isOpen={session !== null}
      title="Rename session"
      description="Give this conversation a clearer name."
      onClose={onCancel}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="session-title"
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Session title
          </label>
          <input
            id="session-title"
            value={title}
            maxLength={SESSION_TITLE_MAX_LENGTH}
            onChange={(event) => setTitle(event.target.value)}
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-800 focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-brand"
          />
          <p className="mt-1 text-xs text-slate-500">
            {trimmedTitle.length}/{SESSION_TITLE_MAX_LENGTH} characters
          </p>
        </div>

        {error ? (
          <p role="alert" className="text-sm text-rose-600">
            {error}
          </p>
        ) : null}

        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onCancel} disabled={isSaving}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSaving || !trimmedTitle}>
            {isSaving ? <Spinner className="h-3.5 w-3.5" /> : null}
            Save changes
          </Button>
        </div>
      </form>
    </Modal>
  );
}

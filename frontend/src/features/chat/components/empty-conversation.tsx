"use client";

import { Sparkles } from "lucide-react";

import { SUGGESTED_PROMPTS } from "@/features/chat/constants/suggested-prompts";

interface EmptyConversationProps {
  onSelectPrompt: (prompt: string) => void;
}

export function EmptyConversation({ onSelectPrompt }: EmptyConversationProps) {
  return (
    <div className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center py-10 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-soft text-brand-strong">
        <Sparkles className="h-6 w-6" aria-hidden="true" />
      </span>

      <h3 className="mt-4 text-lg font-semibold text-slate-900">
        Ask about your workforce and technology
      </h3>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">
        Search internal employee capabilities, discover current public GitHub
        repositories, or combine both in a single recommendation.
      </p>

      <ul className="mt-6 grid w-full gap-2 sm:grid-cols-2">
        {SUGGESTED_PROMPTS.map((prompt) => (
          <li key={prompt}>
            <button
              type="button"
              onClick={() => onSelectPrompt(prompt)}
              className="h-full w-full rounded-xl border border-slate-200 bg-white px-3.5 py-3 text-left text-sm text-slate-700 transition-colors hover:border-brand/40 hover:bg-brand-soft focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
            >
              {prompt}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

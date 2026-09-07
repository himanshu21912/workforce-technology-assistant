import { Bot } from "lucide-react";

export function AssistantThinking() {
  return (
    <div className="flex gap-3" aria-hidden="true">
      <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-50 text-emerald-700">
        <Bot className="h-4 w-4" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold text-slate-900">Assistant</p>
        <div className="mt-1.5 inline-flex items-center gap-2 rounded-xl border border-emerald-100 bg-emerald-50/40 px-3.5 py-3">
          <span className="flex gap-1">
            {[0, 150, 300].map((delay) => (
              <span
                key={delay}
                style={{ animationDelay: `${delay}ms` }}
                className="h-1.5 w-1.5 animate-bounce rounded-full bg-emerald-500"
              />
            ))}
          </span>
          <span className="text-sm text-slate-600">
            Working on your answer…
          </span>
        </div>
      </div>
    </div>
  );
}

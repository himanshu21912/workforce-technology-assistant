import { AlertCircle, CheckCircle2, HelpCircle, XCircle } from "lucide-react";

import { cn } from "@/lib/cn";
import type {
  ServiceIndicator,
  ServiceIndicatorStatus,
} from "@/features/system-status/types/health.types";

const STATUS_PRESENTATION: Record<
  ServiceIndicatorStatus,
  { label: string; className: string; Icon: typeof CheckCircle2 }
> = {
  connected: {
    label: "Healthy",
    className: "border-emerald-200 bg-emerald-50 text-emerald-700",
    Icon: CheckCircle2,
  },
  degraded: {
    label: "Degraded",
    className: "border-amber-200 bg-amber-50 text-amber-800",
    Icon: AlertCircle,
  },
  unavailable: {
    label: "Unavailable",
    className: "border-rose-200 bg-rose-50 text-rose-700",
    Icon: XCircle,
  },
  loading: {
    label: "Checking",
    className: "border-slate-200 bg-slate-50 text-slate-600",
    Icon: HelpCircle,
  },
};

interface StatusIndicatorProps {
  indicator: ServiceIndicator;
}

/** Status is conveyed by icon and text as well as colour. */
export function StatusIndicator({ indicator }: StatusIndicatorProps) {
  const presentation = STATUS_PRESENTATION[indicator.status];
  const { Icon } = presentation;

  return (
    <li className="flex items-center justify-between gap-3 py-1.5">
      <span className="flex min-w-0 items-center gap-2">
        <Icon
          className={cn(
            "h-4 w-4 shrink-0",
            indicator.status === "connected"
              ? "text-emerald-600"
              : indicator.status === "degraded"
                ? "text-amber-600"
                : indicator.status === "unavailable"
                  ? "text-rose-600"
                  : "text-slate-400",
          )}
          aria-hidden="true"
        />
        <span className="truncate text-sm text-slate-700">
          {indicator.label}
        </span>
      </span>
      <span
        title={indicator.message ?? undefined}
        className={cn(
          "shrink-0 rounded-md border px-2 py-0.5 text-[11px] font-medium",
          presentation.className,
        )}
      >
        {presentation.label}
      </span>
    </li>
  );
}

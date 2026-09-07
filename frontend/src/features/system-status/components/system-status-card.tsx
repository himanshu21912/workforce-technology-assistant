"use client";

import { Activity, RefreshCw } from "lucide-react";

import { IconButton } from "@/components/ui/icon-button";
import { StatusIndicator } from "@/features/system-status/components/status-indicator";
import type {
  HealthResponse,
  ServiceIndicator,
} from "@/features/system-status/types/health.types";

interface SystemStatusCardProps {
  indicators: ServiceIndicator[];
  health: HealthResponse | null;
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
}

export function SystemStatusCard({
  indicators,
  health,
  isLoading,
  error,
  onRefresh,
}: SystemStatusCardProps) {
  const summary = error
    ? "Backend unreachable"
    : isLoading && !health
      ? "Checking services…"
      : health?.status === "ok"
        ? "All systems operational"
        : "Some services are degraded";

  return (
    <section
      aria-label="System status"
      className="rounded-xl border border-slate-200 bg-white p-4"
    >
      <div className="flex items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
          <Activity className="h-4 w-4 text-slate-500" aria-hidden="true" />
          System Status
        </h2>
        <IconButton label="Refresh system status" onClick={onRefresh}>
          <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />
        </IconButton>
      </div>

      <p className="mt-1 text-xs text-slate-600">{summary}</p>

      <ul className="mt-2 divide-y divide-slate-100">
        {indicators.map((indicator) => (
          <StatusIndicator key={indicator.key} indicator={indicator} />
        ))}
      </ul>

      {health ? (
        <p className="mt-2 border-t border-slate-100 pt-2 text-[11px] text-slate-500">
          {health.service.name} v{health.service.version} ·{" "}
          {health.service.environment}
        </p>
      ) : null}
    </section>
  );
}

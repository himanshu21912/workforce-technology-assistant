import { Info } from "lucide-react";

import {
  ARCHITECTURE_BRANCHES,
  ARCHITECTURE_FLOW,
  PROJECT_CAPABILITIES,
  PROJECT_DESCRIPTION,
  PROJECT_TITLE,
  TECHNOLOGY_BADGES,
} from "@/features/project-info/constants/project-info";

export function AboutCard() {
  return (
    <section
      aria-label="About this assistant"
      className="rounded-xl border border-slate-200 bg-white p-4"
    >
      <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
        <Info className="h-4 w-4 text-slate-500" aria-hidden="true" />
        About This Assistant
      </h2>

      <p className="mt-2 text-sm font-medium leading-6 text-slate-800">
        {PROJECT_TITLE}
      </p>
      <p className="mt-1.5 text-sm leading-6 text-slate-600">
        {PROJECT_DESCRIPTION}
      </p>

      <h3 className="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
        Key Capabilities
      </h3>
      <ul className="mt-2 space-y-1.5">
        {PROJECT_CAPABILITIES.map((capability) => (
          <li
            key={capability}
            className="flex gap-2 text-sm leading-6 text-slate-700"
          >
            <span
              className="mt-2.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand"
              aria-hidden="true"
            />
            {capability}
          </li>
        ))}
      </ul>

      <h3 className="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
        Architecture
      </h3>
      <p className="mt-2 rounded-lg bg-panel-muted px-3 py-2 font-mono text-[11px] leading-5 text-slate-700">
        {ARCHITECTURE_FLOW.join(" → ")}
      </p>
      <ul className="mt-1.5 space-y-1">
        {ARCHITECTURE_BRANCHES.map((branch) => (
          <li key={branch.label} className="text-[11px] leading-5 text-slate-600">
            <span className="font-semibold text-slate-700">{branch.label}:</span>{" "}
            <span className="font-mono">{branch.flow}</span>
          </li>
        ))}
      </ul>

      <h3 className="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
        Technology
      </h3>
      <ul className="mt-2 flex flex-wrap gap-1.5">
        {TECHNOLOGY_BADGES.map((technology) => (
          <li
            key={technology}
            className="rounded-md border border-slate-200 bg-panel-muted px-2 py-0.5 text-[11px] font-medium text-slate-700"
          >
            {technology}
          </li>
        ))}
      </ul>
    </section>
  );
}

import type { ReactNode } from "react";

interface AppShellProps {
  sidebar: ReactNode;
  main: ReactNode;
  aside: ReactNode;
}

/**
 * Desktop-first three-region layout. Each region scrolls independently;
 * the page itself never scrolls.
 */
export function AppShell({ sidebar, main, aside }: AppShellProps) {
  return (
    <div className="grid h-dvh w-full grid-cols-1 overflow-hidden bg-canvas lg:grid-cols-[17rem_minmax(0,1fr)] xl:grid-cols-[17.5rem_minmax(0,1fr)_21.5rem]">
      <aside
        aria-label="Sessions"
        className="hidden min-h-0 border-r border-slate-200 lg:block"
      >
        {sidebar}
      </aside>

      <main className="min-h-0 lg:p-3 xl:pr-0">{main}</main>

      <aside
        aria-label="Project information"
        className="scroll-panel hidden min-h-0 overflow-y-auto p-3 xl:block"
      >
        {aside}
      </aside>
    </div>
  );
}

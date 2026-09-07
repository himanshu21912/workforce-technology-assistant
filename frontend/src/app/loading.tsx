import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <div
      aria-busy="true"
      aria-live="polite"
      className="grid h-dvh grid-cols-1 gap-3 bg-canvas p-3 lg:grid-cols-[17rem_minmax(0,1fr)] xl:grid-cols-[17.5rem_minmax(0,1fr)_21.5rem]"
    >
      <span className="sr-only">Loading the assistant</span>
      <Skeleton className="hidden h-full rounded-xl lg:block" />
      <Skeleton className="h-full rounded-xl" />
      <Skeleton className="hidden h-full rounded-xl xl:block" />
    </div>
  );
}

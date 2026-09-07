const TIME_FORMATTER = new Intl.DateTimeFormat("en-US", {
  hour: "numeric",
  minute: "2-digit",
});

const SHORT_DATE_TIME_FORMATTER = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
});

const DATE_TIME_FORMATTER = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  hour: "numeric",
  minute: "2-digit",
});

function toDate(value: string): Date | null {
  const parsed = new Date(value);

  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function formatTime(value: string): string {
  const date = toDate(value);

  return date ? TIME_FORMATTER.format(date) : "";
}

/** Compact form for dense lists, e.g. "Sep 8, 1:15 AM". */
export function formatShortDateTime(value: string): string {
  const date = toDate(value);

  return date ? SHORT_DATE_TIME_FORMATTER.format(date) : "";
}

export function formatDateTime(value: string): string {
  const date = toDate(value);

  return date ? DATE_TIME_FORMATTER.format(date) : "";
}

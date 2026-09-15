/**
 * Number formatting pinned to a fixed locale ('en-US').
 *
 * Plain `.toLocaleString()` with no locale argument uses the *viewer's*
 * browser/OS locale - on a machine set to e.g. en-IN that silently
 * reformats "388,000" as "3,88,000". Ad performance numbers should look
 * the same for every viewer regardless of their locale settings, so every
 * number in this app must go through one of these instead of calling
 * `.toLocaleString()` directly.
 */
export function formatNumber(value: number, maximumFractionDigits = 0): string {
  return value.toLocaleString('en-US', { maximumFractionDigits });
}

export function formatCurrency(value: number, maximumFractionDigits = 0): string {
  return `$${formatNumber(value, maximumFractionDigits)}`;
}

/** Short axis-friendly date, e.g. "Jan 5" - fixed format so it's compact and never locale-dependent. */
export function formatShortDate(value: string | number | Date): string {
  return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/** Fuller date for tooltips/labels, e.g. "Jan 5, 2024". */
export function formatDate(value: string | number | Date): string {
  return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

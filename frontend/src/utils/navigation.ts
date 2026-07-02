export function safeRedirectPath(value: unknown, fallback = "/expenses"): string {
  if (typeof value !== "string" || !value.startsWith("/") || value.startsWith("//")) {
    return fallback;
  }
  return value;
}

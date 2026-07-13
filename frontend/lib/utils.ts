export function cn(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

export function shortId(id: string, n = 8) {
  return id.length <= n ? id : `${id.slice(0, n)}…`;
}

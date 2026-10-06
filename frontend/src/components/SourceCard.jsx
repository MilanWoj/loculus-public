// Author: MilanWoj
export default function SourceCard({ source, index }) {
  let host = source.url;
  try {
    host = new URL(source.url).hostname.replace(/^www\./, "");
  } catch {
    // malformed URL, fall back to the raw string
  }

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noreferrer"
      className="shrink-0 w-56 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-3 hover:border-[var(--color-accent)] transition-colors"
    >
      <div className="flex items-center gap-1.5 mb-1.5">
        <span className="text-[10px] font-mono text-[var(--color-accent)] bg-[var(--color-accent)]/10 rounded px-1.5 py-0.5">
          {index + 1}
        </span>
        <span className="text-xs text-[var(--color-text-muted)] truncate">
          {source.type === "document" ? "local document" : host}
        </span>
      </div>
      <p className="text-sm line-clamp-2">{source.title}</p>
    </a>
  );
}

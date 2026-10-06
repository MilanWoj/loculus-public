// Author: MilanWoj
const MODES = [
  { key: "auto", label: "Auto" },
  { key: "web", label: "Web" },
  { key: "docs", label: "Documents" },
];

export default function ModeToggle({ mode, onChange }) {
  return (
    <div className="inline-flex rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-1">
      {MODES.map((m) => (
        <button
          key={m.key}
          type="button"
          onClick={() => onChange(m.key)}
          className={`px-3 py-1.5 text-xs font-mono rounded-md transition-colors ${
            mode === m.key
              ? "bg-[var(--color-accent)] text-white"
              : "text-[var(--color-text-muted)] hover:text-[var(--color-text)]"
          }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}

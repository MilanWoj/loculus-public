// Author: MilanWoj
export default function MetricsFooter({ timings, ramMb }) {
  if (!timings && ramMb === null) return null;

  return (
    <div className="fixed bottom-3 right-4 text-[11px] font-mono text-[var(--color-text-muted)] flex gap-3">
      {timings && <span>{timings.total_ms} ms</span>}
      {ramMb !== null && <span>{Math.round(ramMb)} MB</span>}
    </div>
  );
}

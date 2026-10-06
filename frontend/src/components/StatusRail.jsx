// Author: MilanWoj
import { useEffect, useState } from "react";
import { fetchHealth } from "../lib/api";

const SERVICES = [
  { key: "llm", label: "LLM" },
  { key: "embeddings", label: "Embeddings" },
  { key: "qdrant", label: "Qdrant" },
  { key: "searxng", label: "SearXNG" },
];

export default function StatusRail() {
  const [status, setStatus] = useState({});

  useEffect(() => {
    const poll = async () => {
      try {
        setStatus(await fetchHealth());
      } catch {
        setStatus({});
      }
    };
    poll();
    const interval = setInterval(poll, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="fixed left-0 top-0 h-full w-14 flex flex-col items-center gap-4 py-6 border-r border-[var(--color-border)] bg-[var(--color-surface)]">
      {SERVICES.map((s) => {
        const up = status[s.key];
        return (
          <div key={s.key} className="group relative flex items-center">
            <span className={`w-2.5 h-2.5 rounded-full ${up ? "bg-[var(--color-status-up)] status-pulse" : "bg-[var(--color-status-down)]"}`} />
            <span className="absolute left-6 whitespace-nowrap text-xs font-mono bg-[var(--color-surface-raised)] border border-[var(--color-border)] rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
              {s.label} — {up ? "up" : "down"}
            </span>
          </div>
        );
      })}
    </aside>
  );
}

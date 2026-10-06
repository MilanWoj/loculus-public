// Author: MilanWoj
import { useState, useRef } from "react";
import { Search, Loader2 } from "lucide-react";
import StatusRail from "./components/StatusRail";
import ModeToggle from "./components/ModeToggle";
import SourceCard from "./components/SourceCard";
import ChatMessage from "./components/ChatMessage";
import MetricsFooter from "./components/MetricsFooter";
import { streamChat, fetchMetrics } from "./lib/api";

export default function App() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("auto");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [clarification, setClarification] = useState(null);
  const [timings, setTimings] = useState(null);
  const [ramMb, setRamMb] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setAnswer("");
    setSources([]);
    setWarnings([]);
    setClarification(null);
    setTimings(null);
    setError(null);

    try {
      await streamChat(query, mode, {
        onSources: setSources,
        onToken: (t) => setAnswer((prev) => prev + t),
        onWarning: (w) => setWarnings((prev) => [...prev, w]),
        onClarification: setClarification,
        onDone: async (t) => {
          setTimings(t);
          try {
            const metrics = await fetchMetrics();
            setRamMb(metrics.available ? metrics.llama_server_ram_mb : null);
          } catch {
            // never block the UI on this
          }
        },
        onError: (e) => setError(e),
      });
    } catch (err) {
      setError(`Unexpected error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen pl-14">
      <StatusRail />

      <main className="max-w-2xl mx-auto px-6 py-16">
        <header className="mb-8 text-center">
          <h1 className="font-display text-xl font-semibold tracking-tight">Loculus</h1>
        </header>

        <div className="flex justify-center mb-6">
          <ModeToggle mode={mode} onChange={setMode} />
        </div>

        <form onSubmit={handleSubmit} className="relative mb-8">
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search…"
            className="w-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl py-3.5 pl-4 pr-12 text-[15px] placeholder:text-[var(--color-text-muted)] focus:border-[var(--color-accent)] transition-colors"
          />
          <button
            type="submit"
            disabled={loading}
            aria-label="Search"
            className="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 flex items-center justify-center rounded-lg bg-[var(--color-accent)] text-white disabled:opacity-50"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
          </button>
        </form>

        {error && <p className="text-[var(--color-status-down)] text-sm font-mono mb-6">✕ {error}</p>}

        {warnings.map((w, i) => (
          <p key={i} className="text-[var(--color-accent-warm)] text-sm font-mono mb-4">⚠ {w}</p>
        ))}

        {clarification && (
          <div className="bg-[var(--color-surface)] border border-[var(--color-accent)] rounded-xl p-5 mb-6">
            <p className="text-xs text-[var(--color-text-muted)] font-mono mb-1.5">Clarification needed</p>
            <p className="text-[15px]">{clarification}</p>
          </div>
        )}

        {sources.length > 0 && (
          <div className="flex gap-3 overflow-x-auto pb-3 mb-6 -mx-1 px-1">
            {sources.map((s, i) => <SourceCard key={i} source={s} index={i} />)}
          </div>
        )}

        {answer && (
          <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
            <ChatMessage text={answer} sourcesCount={sources.length} />
          </div>
        )}
      </main>

      <MetricsFooter timings={timings} ramMb={ramMb} />
    </div>
  );
}

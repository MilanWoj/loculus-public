// Author: MilanWoj
export default function ChatMessage({ text, sourcesCount }) {
  const parts = text.split(/(\[\d+\])/g);

  return (
    <p className="text-[15px] leading-relaxed whitespace-pre-wrap">
      {parts.map((part, i) => {
        const match = part.match(/^\[(\d+)\]$/);
        if (!match) return part;

        const n = Number(match[1]);
        const valid = n >= 1 && n <= sourcesCount;
        return (
          <sup
            key={i}
            className={`font-mono text-xs mx-0.5 ${
              valid ? "text-[var(--color-accent)]" : "text-[var(--color-status-down)]"
            }`}
          >
            {part}
          </sup>
        );
      })}
    </p>
  );
}

// Author: MilanWoj
const API_BASE = import.meta.env.DEV ? "http://127.0.0.1:8000/api" : "/api";

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("health check failed");
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/metrics`);
  if (!res.ok) throw new Error("metrics fetch failed");
  return res.json();
}

export async function streamChat(query, mode, callbacks) {
  let response;
  try {
    response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, mode }),
    });
  } catch (err) {
    callbacks.onError?.(`Cannot reach the backend (${err.message}).`);
    return;
  }

  if (!response.ok || !response.body) {
    callbacks.onError?.("The backend returned an error.");
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const dispatch = (eventType, dataLines) => {
    const data = dataLines.join("\n");
    if (!data && eventType !== "done") return;
    try {
      switch (eventType) {
        case "sources":
          callbacks.onSources?.(JSON.parse(data));
          break;
        case "token":
        case "message":
          callbacks.onToken?.(data);
          break;
        case "warning":
          callbacks.onWarning?.(data);
          break;
        case "clarification":
          callbacks.onClarification?.(data);
          break;
        case "done":
          callbacks.onDone?.(JSON.parse(data));
          break;
        case "error":
          callbacks.onError?.(data);
          break;
      }
    } catch (err) {
      callbacks.onError?.(`Parse error (${eventType}): ${err.message}`);
    }
  };

  const processRawEvent = (rawEvent) => {
    let eventType = "message";
    const dataLines = [];
    for (const line of rawEvent.split("\n")) {
      if (line.startsWith("event:")) eventType = line.slice(6).trim();
      else if (line.startsWith("data:")) dataLines.push(line.slice(5).replace(/^ /, ""));
    }
    dispatch(eventType, dataLines);
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true }).replaceAll("\r\n", "\n");
    const events = buffer.split("\n\n");
    buffer = events.pop();
    for (const rawEvent of events) {
      if (rawEvent.trim()) processRawEvent(rawEvent);
    }
  }

  if (buffer.trim()) processRawEvent(buffer);
}

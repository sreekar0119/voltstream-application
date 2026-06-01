const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

async function request(path, options = {}) {
  const headers = options.body instanceof FormData
    ? { ...options.headers }
    : {
        "Content-Type": "application/json",
        ...options.headers
      };

  const response = await fetch(`${API_BASE}${path}`, {
    headers,
    ...options
  });

  if (!response.ok) {
    let message = await response.text();
    try {
      const parsed = JSON.parse(message);
      message = parsed.detail || message;
    } catch {
      // Keep the raw response text when the backend does not return JSON.
    }
    throw new Error(message || `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

async function streamRequest(path, body, handlers = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    let message = await response.text();
    try {
      const parsed = JSON.parse(message);
      message = parsed.detail || message;
    } catch {
      // Keep the raw response text when the backend does not return JSON.
    }
    throw new Error(message || `Request failed with ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let metadata = null;
  let finalResponse = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const raw of events) {
      const event = raw
        .split("\n")
        .find((line) => line.startsWith("event:"))
        ?.replace("event:", "")
        .trim();
      const dataLine = raw
        .split("\n")
        .find((line) => line.startsWith("data:"));
      if (!event || !dataLine) continue;

      const data = JSON.parse(dataLine.replace("data:", "").trim());
      if (event === "metadata") {
        metadata = data;
        handlers.onMetadata?.(data);
      }
      if (event === "trace") {
        handlers.onTrace?.(data);
      }
      if (event === "token") {
        finalResponse += data.token;
        handlers.onToken?.(data.token);
      }
      if (event === "done") {
        finalResponse = data.response || finalResponse;
      }
    }
  }

  return { ...(metadata ?? {}), response: finalResponse };
}

export const api = {
  liveDashboard: () => request("/dashboard/live"),
  analyticsHistory: (period) => request(`/analytics/history${period ? `?period=${period}` : ""}`),
  devices: () => request("/devices"),
  addDevice: (device) =>
    request("/devices", {
      method: "POST",
      body: JSON.stringify(device)
    }),
  updateDevice: (id, status) =>
    request(`/devices/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status })
    }),
  deleteDevice: (id) =>
    request(`/devices/${id}`, {
      method: "DELETE"
    }),
  billingSummary: () => request("/billing/summary"),
  energyChat: (message) =>
    request("/chat", {
      method: "POST",
      body: JSON.stringify({ message })
    }),
  deviceAgent: (message) =>
    request("/agent", {
      method: "POST",
      body: JSON.stringify({ message })
    }),
  streamDeviceAgent: (message, sessionId, handlers) =>
    streamRequest("/agent/stream", { message, session_id: sessionId }, handlers),
  documentQa: (question) =>
    request("/qa", {
      method: "POST",
      body: JSON.stringify({ question })
    })
};

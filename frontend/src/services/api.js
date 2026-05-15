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
  energyChat: (message, file) => {
    const formData = new FormData();
    formData.append("message", message);
    if (file) {
      formData.append("file", file);
    }

    return request("/chat", {
      method: "POST",
      body: formData
    });
  },
  documentQa: (question) =>
    request("/qa", {
      method: "POST",
      body: JSON.stringify({ question })
    })
};

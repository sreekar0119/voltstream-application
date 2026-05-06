const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json();
}

export const api = {
  liveDashboard: () => request("/dashboard/live"),
  analyticsHistory: (period) => request(`/analytics/history${period ? `?period=${period}` : ""}`),
  devices: () => request("/devices"),
  updateDevice: (id, status) =>
    request(`/devices/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status })
    }),
  billingSummary: () => request("/billing/summary")
};

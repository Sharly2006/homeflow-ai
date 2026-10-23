/**
 * HomeFlow AI - REST API Service Layer
 * Uses Fetch API to communicate with FastAPI backend.
 */

const BASE_URL = import.meta.env.VITE_API_URL || '';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      let errorDetail = 'API request failed';
      try {
        const errJson = await response.json();
        errorDetail = errJson.detail || errJson.message || errorDetail;
      } catch {
        errorDetail = `Error ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorDetail);
    }
    return await response.json();
  } catch (error) {
    console.error(`[API Error] ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // System Health
  getHealth: () => request('/api/health'),

  // Assistant Natural Language
  sendAssistantMessage: (query) =>
    request('/api/assistant', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),
  getActionLogs: (limit = 10) => request(`/api/actions?limit=${limit}`),

  // Tasks
  getTasks: (status = 'all', category = null) => {
    let q = `/api/tasks?status=${status}`;
    if (category) q += `&category=${encodeURIComponent(category)}`;
    return request(q);
  },
  createTask: (data) =>
    request('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateTask: (id, data) =>
    request(`/api/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  completeTask: (id) =>
    request(`/api/tasks/${id}/complete`, {
      method: 'POST',
    }),
  deleteTask: (id) =>
    request(`/api/tasks/${id}`, {
      method: 'DELETE',
    }),

  // Reminders
  getReminders: (includeCompleted = false) =>
    request(`/api/reminders?include_completed=${includeCompleted}`),
  createReminder: (data) =>
    request('/api/reminders', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  completeReminder: (id) =>
    request(`/api/reminders/${id}/complete`, {
      method: 'POST',
    }),
  deleteReminder: (id) =>
    request(`/api/reminders/${id}`, {
      method: 'DELETE',
    }),

  // Daily Summary
  getSummary: () => request('/api/summary'),

  // Simulated Entry Events
  getEntryEvents: (limit = 15) => request(`/api/events?limit=${limit}`),
  triggerSimulatedEvent: (data) =>
    request('/api/events', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // MCP Server Transparency
  getMcpTools: () => request('/api/mcp/tools'),
};

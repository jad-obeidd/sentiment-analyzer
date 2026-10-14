async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

export const analyze = (text) => request('/analyze', { method: 'POST', body: JSON.stringify({ text }) });
export const getHistory = (label) => request(`/history?limit=50${label ? `&label=${label}` : ''}`);
export const deleteItem = (id) => request(`/history/${id}`, { method: 'DELETE' });
export const clearHistory = () => request('/history', { method: 'DELETE' });
export const getStats = () => request('/stats');

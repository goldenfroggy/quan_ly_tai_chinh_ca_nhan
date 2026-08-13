const api = {
  async request(method, path, body) {
    const opts = { method, headers: {} };
    if (body !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    const res = await fetch(`/api${path}`, opts);
    let data = null;
    try { data = await res.json(); } catch (_) {}
    if (!res.ok) {
      const detail = data && (data.detail || data.message);
      const msg = typeof detail === "string" ? detail : "Có lỗi xảy ra";
      throw new Error(msg);
    }
    return data;
  },

  categories: {
    list: () => api.request("GET", "/categories"),
    create: (data) => api.request("POST", "/categories", data),
    update: (id, data) => api.request("PUT", `/categories/${id}`, data),
    remove: (id) => api.request("DELETE", `/categories/${id}`),
  },

  transactions: {
    list: (params) => {
      const qs = new URLSearchParams();
      Object.entries(params || {}).forEach(([k, v]) => {
        if (v !== "" && v !== null && v !== undefined) qs.set(k, v);
      });
      return api.request("GET", `/transactions?${qs}`);
    },
    create: (data) => api.request("POST", "/transactions", data),
    update: (id, data) => api.request("PUT", `/transactions/${id}`, data),
    remove: (id) => api.request("DELETE", `/transactions/${id}`),
  },

  budgets: {
    list: () => api.request("GET", "/budgets"),
    create: (data) => api.request("POST", "/budgets", data),
    update: (id, data) => api.request("PUT", `/budgets/${id}`, data),
    remove: (id) => api.request("DELETE", `/budgets/${id}`),
  },

  alerts: {
    list: (unreadOnly) =>
      api.request("GET", `/alerts${unreadOnly ? "?unread_only=true" : ""}`),
    unreadCount: () => api.request("GET", "/alerts/unread-count"),
    check: () => api.request("POST", "/alerts/check"),
    markRead: (id) => api.request("PUT", `/alerts/${id}/read`),
    markAllRead: () => api.request("PUT", "/alerts/read-all"),
  },

  dashboard: {
    summary: () => api.request("GET", "/dashboard/summary"),
  },
};

function fmtVND(n) {
  return (n === null || n === undefined ? 0 : n).toLocaleString("vi-VN", { maximumFractionDigits: 0 }) + " đ";
}

function fmtDate(d) {
  if (!d) return "";
  const [y, m, day] = String(d).slice(0, 10).split("-");
  return `${day}/${m}/${y}`;
}

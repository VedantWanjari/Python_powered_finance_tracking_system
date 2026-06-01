const DEFAULT_BASE_URL = "http://localhost:5000";

export class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = (baseUrl || localStorage.getItem("apiBaseUrl") || DEFAULT_BASE_URL).replace(/\/$/, "");
  }

  setBaseUrl(baseUrl) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    localStorage.setItem("apiBaseUrl", this.baseUrl);
  }

  async request(path, { method = "GET", body, params } = {}) {
    const url = new URL(`${this.baseUrl}${path}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
          url.searchParams.set(key, value);
        }
      });
    }

    const response = await fetch(url, {
      method,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    const payload = await response.json().catch(() => ({ message: "Invalid JSON response" }));
    if (!response.ok || payload.status === "error") {
      const message = payload.message || `Request failed (${response.status})`;
      const error = new Error(message);
      error.status = response.status;
      error.details = payload;
      throw error;
    }

    return payload;
  }

  auth = {
    register: (data) => this.request("/api/auth/register", { method: "POST", body: data }),
    login: (data) => this.request("/api/auth/login", { method: "POST", body: data }),
    logout: () => this.request("/api/auth/logout", { method: "POST" }),
    me: () => this.request("/api/auth/me"),
    updateProfile: (data) => this.request("/api/auth/me", { method: "PUT", body: data }),
  };

  transactions = {
    list: (params) => this.request("/api/transactions/", { params }),
    create: (data) => this.request("/api/transactions/", { method: "POST", body: data }),
    update: (id, data) => this.request(`/api/transactions/${id}`, { method: "PUT", body: data }),
    remove: (id) => this.request(`/api/transactions/${id}`, { method: "DELETE" }),
  };

  analytics = {
    dashboard: () => this.request("/api/analytics/dashboard"),
    trends: (months = 6) => this.request("/api/analytics/trends", { params: { months } }),
    categories: () => this.request("/api/analytics/categories"),
  };
}

export const api = new ApiClient();

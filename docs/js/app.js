import { api } from "./api-client.js";

const DEFAULT_PAGE = 1;
const DEFAULT_PER_PAGE = 20;
const DEFAULT_TREND_MONTHS = 6;

const state = {
  currentUser: null,
  transactions: [],
  editingId: null,
  charts: {},
};

const ui = {
  authScreen: document.getElementById("auth-screen"),
  appScreen: document.getElementById("app-screen"),
  logoutBtn: document.getElementById("logout-btn"),
  toast: document.getElementById("toast"),
  status: document.getElementById("connection-status"),
  transactionsTableBody: document.getElementById("transactions-table-body"),
  transactionForm: document.getElementById("transaction-form"),
  transactionFormTitle: document.getElementById("transaction-form-title"),
  transactionReset: document.getElementById("transaction-reset"),
  refreshTransactions: document.getElementById("refresh-transactions"),
  profileForm: document.getElementById("profile-form"),
  kpiCards: document.getElementById("kpi-cards"),
  categoryList: document.getElementById("category-list"),
};

const fmtCurrency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

const showToast = (message, type = "success") => {
  ui.toast.textContent = message;
  ui.toast.className = `toast ${type}`;
  ui.toast.classList.remove("hidden");
  window.setTimeout(() => ui.toast.classList.add("hidden"), 3000);
};

const setAuthView = (authenticated) => {
  ui.authScreen.classList.toggle("hidden", authenticated);
  ui.appScreen.classList.toggle("hidden", !authenticated);
  ui.logoutBtn.classList.toggle("hidden", !authenticated);
};

const setSection = (name) => {
  document.querySelectorAll("[data-page-section]").forEach((section) => {
    section.classList.toggle("hidden", section.dataset.pageSection !== name);
  });
  document.querySelectorAll(".subnav-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.section === name);
  });
};

const resetTransactionForm = () => {
  ui.transactionForm.reset();
  ui.transactionForm.transaction_id.value = "";
  state.editingId = null;
  ui.transactionFormTitle.textContent = "Add transaction";
};

const loadTransactions = async () => {
  const { data } = await api.transactions.list({
    page: DEFAULT_PAGE,
    per_page: DEFAULT_PER_PAGE,
    sort_by: "date",
    sort_order: "desc",
  });
  state.transactions = data;
  ui.transactionsTableBody.innerHTML = data.length
    ? data
        .map(
          (tx) => `<tr>
      <td>${tx.date || "-"}</td>
      <td>${tx.description}</td>
      <td>${tx.category_name || tx.category_id || "Uncategorized"}</td>
      <td>${tx.transaction_type}</td>
      <td>${fmtCurrency.format(tx.amount || 0)}</td>
      <td>
        <button class="btn btn-outline" data-edit-tx="${tx.id}" type="button">Edit</button>
        <button class="btn btn-outline" data-delete-tx="${tx.id}" type="button">Delete</button>
      </td>
    </tr>`
        )
        .join("")
    : '<tr><td colspan="6">No transactions available.</td></tr>';
};

const loadAnalytics = async () => {
  const dashboard = await api.analytics.dashboard();
  const categories = await api.analytics.categories();

  ui.kpiCards.innerHTML = [
    ["Income", dashboard.data.total_income],
    ["Expenses", dashboard.data.total_expenses],
    ["Balance", dashboard.data.net_balance],
    ["Transactions", dashboard.data.transaction_count],
  ]
    .map(([label, value]) => `<div class="kpi-item"><span>${label}</span><br /><strong>${label === "Transactions" ? value : fmtCurrency.format(value || 0)}</strong></div>`)
    .join("");

  ui.categoryList.innerHTML = categories.data.length
    ? categories.data.map((item) => `<li><span>${item.category_name || "Uncategorized"}</span><strong>${fmtCurrency.format(item.total || 0)}</strong></li>`).join("")
    : "<li><span>No category data yet</span></li>";

  if (state.charts.category) state.charts.category.destroy();
  state.charts.category = new Chart(document.getElementById("category-chart"), {
    type: "doughnut",
    data: {
      labels: categories.data.map((item) => item.category_name || "Uncategorized"),
      datasets: [{ data: categories.data.map((item) => item.total || 0) }],
    },
    options: { plugins: { legend: { labels: { color: "#e5e7eb" } } } },
  });

  try {
    const trends = await api.analytics.trends(DEFAULT_TREND_MONTHS);
    if (state.charts.trend) state.charts.trend.destroy();
    state.charts.trend = new Chart(document.getElementById("trend-chart"), {
      type: "line",
      data: {
        labels: trends.data.map((item) => item.month),
        datasets: [
          { label: "Income", data: trends.data.map((item) => item.income || 0), borderColor: "#22c55e" },
          { label: "Expense", data: trends.data.map((item) => item.expenses || 0), borderColor: "#ef4444" },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: "#e5e7eb" } } },
        scales: {
          x: { ticks: { color: "#94a3b8" } },
          y: { ticks: { color: "#94a3b8" } },
        },
      },
    });
  } catch {
    document.getElementById("trend-chart").closest("article").querySelector("h3").textContent = "Income vs Expense Trend (requires analyst/admin role)";
  }
};

const loadProfile = async () => {
  const me = await api.auth.me();
  state.currentUser = me.data;
  ui.profileForm.username.value = me.data.username || "";
  ui.profileForm.email.value = me.data.email || "";
  ui.profileForm.role.value = me.data.role || "";
  ui.status.textContent = `Connected: ${api.baseUrl}`;
};

const loadDashboard = async () => {
  await Promise.all([loadProfile(), loadTransactions(), loadAnalytics()]);
};

const parseTransactionForm = (form) => {
  const rawCategory = form.category_id.value.trim();
  return {
    amount: Number(form.amount.value),
    transaction_type: form.transaction_type.value,
    date: form.date.value,
    description: form.description.value.trim(),
    notes: form.notes.value.trim() || undefined,
    tags: form.tags.value.split(",").map((tag) => tag.trim()).filter(Boolean),
    category_id: rawCategory ? Number(rawCategory) : undefined,
  };
};

const bindEvents = () => {
  document.querySelectorAll("[data-auth-tab]").forEach((tabBtn) => {
    tabBtn.addEventListener("click", () => {
      document.querySelectorAll("[data-auth-tab]").forEach((item) => item.classList.toggle("active", item === tabBtn));
      document.querySelectorAll("[data-auth-panel]").forEach((panel) => panel.classList.toggle("hidden", panel.dataset.authPanel !== tabBtn.dataset.authTab));
    });
  });

  document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    try {
      await api.auth.login({ username: form.username.value, password: form.password.value });
      await loadDashboard();
      setAuthView(true);
      showToast("Logged in successfully.");
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  document.getElementById("register-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    try {
      await api.auth.register({ username: form.username.value, email: form.email.value, password: form.password.value });
      showToast("Registration complete. Please log in.");
      document.querySelector('[data-auth-tab="login"]').click();
      form.reset();
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  ui.logoutBtn.addEventListener("click", async () => {
    try {
      await api.auth.logout();
    } finally {
      setAuthView(false);
      showToast("Logged out.");
    }
  });

  ui.transactionForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const payload = parseTransactionForm(ui.transactionForm);
      if (state.editingId) {
        await api.transactions.update(state.editingId, payload);
        showToast("Transaction updated.");
      } else {
        await api.transactions.create(payload);
        showToast("Transaction created.");
      }
      resetTransactionForm();
      await Promise.all([loadTransactions(), loadAnalytics()]);
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  ui.transactionReset.addEventListener("click", resetTransactionForm);

  ui.refreshTransactions.addEventListener("click", async () => {
    try {
      await Promise.all([loadTransactions(), loadAnalytics()]);
      showToast("Data refreshed.");
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  ui.transactionsTableBody.addEventListener("click", async (event) => {
    const editId = event.target.getAttribute("data-edit-tx");
    const deleteId = event.target.getAttribute("data-delete-tx");

    if (editId) {
      const tx = state.transactions.find((item) => item.id === Number(editId));
      if (!tx) return;
      state.editingId = tx.id;
      ui.transactionFormTitle.textContent = `Edit transaction #${tx.id}`;
      ui.transactionForm.transaction_id.value = tx.id;
      ui.transactionForm.amount.value = tx.amount;
      ui.transactionForm.transaction_type.value = tx.transaction_type;
      ui.transactionForm.date.value = tx.date;
      ui.transactionForm.description.value = tx.description;
      ui.transactionForm.notes.value = tx.notes || "";
      ui.transactionForm.tags.value = (tx.tags || []).join(", ");
      ui.transactionForm.category_id.value = tx.category_id || "";
      return;
    }

    if (deleteId) {
      if (!window.confirm("Delete this transaction?")) return;
      try {
        await api.transactions.remove(deleteId);
        showToast("Transaction deleted.");
        await Promise.all([loadTransactions(), loadAnalytics()]);
      } catch (error) {
        showToast(error.message, "error");
      }
    }
  });

  ui.profileForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api.auth.updateProfile({ username: ui.profileForm.username.value, email: ui.profileForm.email.value });
      await loadProfile();
      showToast("Profile updated.");
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  document.querySelectorAll(".subnav-item").forEach((item) => {
    item.addEventListener("click", () => setSection(item.dataset.section));
  });
};

const init = async () => {
  bindEvents();

  try {
    await loadDashboard();
    setAuthView(true);
  } catch {
    setAuthView(false);
    ui.status.textContent = `API URL: ${api.baseUrl}`;
  }
};

init();

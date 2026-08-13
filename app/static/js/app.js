const state = {
  view: "dashboard",
  categories: [],
  txn: { page: 1, pageSize: 10, filters: {} },
  modal: null,
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

/* ---------- helpers ---------- */

function toast(msg, type = "success") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  $("#toasts").appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function catStyle(cat) {
  return `style="background:${cat.color || "#eef0f6"};"`;
}

function catIcon(cat, fallback) {
  return cat && cat.icon ? cat.icon : fallback;
}

function catName(cat) {
  return cat ? cat.name : "—";
}

function setBadge(count) {
  const badge = $("#alert-badge");
  if (count > 0) {
    badge.textContent = count;
    badge.classList.remove("hidden");
  } else {
    badge.classList.add("hidden");
  }
}

async function refreshBadge() {
  try {
    const { count } = await api.alerts.unreadCount();
    setBadge(count);
  } catch (_) {}
}

function switchView(name) {
  state.view = name;
  $$(".tab").forEach((t) => t.classList.toggle("active", t.dataset.view === name));
  $$("main[data-view]").forEach((m) =>
    m.classList.toggle("hidden", m.dataset.view !== name)
  );
  window.scrollTo(0, 0);
  if (name === "dashboard") renderDashboard();
  if (name === "transactions") renderTransactions();
  if (name === "budgets") renderBudgets();
  if (name === "categories") renderCategories();
  if (name === "alerts") renderAlerts();
}

/* ---------- dashboard ---------- */

async function renderDashboard() {
  try {
    const d = await api.dashboard.summary();
    $("#dash-income").textContent = fmtVND(d.income);
    $("#dash-expense").textContent = fmtVND(d.expense);
    $("#dash-balance").textContent = fmtVND(d.balance);
    $("#current-month").textContent = `Tháng ${d.month}`;

    state.budgets = d.budgets;
    state.txn.items = d.recent_transactions;

    $("#dash-budgets").innerHTML = d.budgets.length
      ? d.budgets.map(budgetRow).join("")
      : '<div class="empty">Chưa có hạn mức nào. Hãy tạo hạn mức để quản lý chi tiêu.</div>';

    $("#dash-recent").innerHTML = d.recent_transactions.length
      ? d.recent_transactions.map(txnRow).join("")
      : '<div class="empty">Chưa có giao dịch nào.</div>';

    const alertEls = d.recent_alerts.map(alertItemHtml).join("");
    $("#dash-alerts").innerHTML = d.recent_alerts.length
      ? alertEls
      : '<div class="empty">Không có cảnh báo nào. Tuyệt vời! 🎉</div>';

    setBadge(d.unread_alerts);
  } catch (e) {
    toast(e.message, "error");
  }
}

function budgetProgressClass(b) {
  if (b.percentage >= 100) return "danger";
  if (b.percentage >= b.alert_threshold) return "warn";
  return "";
}

function budgetRow(b) {
  const cls = budgetProgressClass(b);
  const over = b.remaining < 0;
  return `
  <div class="budget-card">
    <div class="budget-card-head">
      <div>
        <h4>${b.name}</h4>
        <div class="budget-cat">
          ${b.category ? catIcon(b.category, "🏷️") + " " + b.category.name : "Tổng thể"}
          · ${b.period === "yearly" ? "Năm" : "Tháng"} ${b.period_key ? "(" + b.period_key + ")" : ""}
          ${b.is_active ? "" : "· <span class='tag tag-expense'>Đã tắt</span>"}
        </div>
      </div>
      <div>
        <button class="btn-icon" data-action="budget-edit" data-id="${b.id}" title="Sửa">✏️</button>
        <button class="btn-icon" data-action="budget-delete" data-id="${b.id}" title="Xóa">🗑️</button>
      </div>
    </div>
    <div class="budget-amount">${fmtVND(b.amount)}</div>
    <div class="progress ${cls}"><div style="width:${Math.min(b.percentage, 100)}%"></div></div>
    <div class="budget-meta">
      <span>Đã chi: <b>${fmtVND(b.spent)}</b></span>
      <span>${b.percentage}%</span>
    </div>
    <div class="budget-meta" style="margin-top:4px;">
      <span class="${over ? "amount-expense" : ""}">Còn lại: ${fmtVND(b.remaining)}</span>
      <span>Ngưỡng cảnh báo: ${b.alert_threshold}%</span>
    </div>
  </div>`;
}

/* ---------- transactions ---------- */

async function loadCategories() {
  state.categories = await api.categories.list();
}

function fillCategoryFilter() {
  const sel = $("#f-category");
  const current = sel.value;
  sel.innerHTML = '<option value="">Tất cả danh mục</option>' +
    state.categories
      .filter((c) => c.type === "expense" || c.type === "income")
      .map((c) => `<option value="${c.id}" ${String(c.id) === current ? "selected" : ""}>${c.icon || ""} ${c.name}</option>`)
      .join("");
}

function txnRow(t) {
  const cat = t.category;
  const isExpense = t.type === "expense";
  return `
  <tr>
    <td>${fmtDate(t.transaction_date)}</td>
    <td><span class="txn-icon" ${catStyle(cat)}>${catIcon(cat, isExpense ? "💸" : "💰")}</span></td>
    <td>
      <div class="txn-name">${cat ? cat.name : "—"}</div>
      <div class="txn-sub">${t.note || ""}</div>
    </td>
    <td class="num ${isExpense ? "amount-expense" : "amount-income"}">
      ${isExpense ? "−" : "+"} ${fmtVND(t.amount)}
    </td>
    <td class="act">
      <button class="btn-icon" data-action="txn-edit" data-id="${t.id}" title="Sửa">✏️</button>
      <button class="btn-icon" data-action="txn-delete" data-id="${t.id}" title="Xóa">🗑️</button>
    </td>
  </tr>`;
}

async function renderTransactions() {
  try {
    fillCategoryFilter();
    const f = state.txn.filters;
    const data = await api.transactions.list({
      ...f,
      page: state.txn.page,
      page_size: state.txn.pageSize,
    });
    state.txn.items = data.items;
    $("#txn-tbody").innerHTML = data.items.length
      ? data.items.map(txnRow).join("")
      : `<tr><td colspan="5" class="empty">Không có giao dịch nào.</td></tr>`;

    const pages = data.pages;
    $("#txn-pagination").innerHTML = `
      <button data-action="txn-page" data-page="${data.page - 1}" ${data.page <= 1 ? "disabled" : ""}>‹</button>
      <span class="page-info">Trang ${data.page} / ${pages || 1} · ${data.total} giao dịch</span>
      <button data-action="txn-page" data-page="${data.page + 1}" ${data.page >= pages ? "disabled" : ""}>›</button>`;
  } catch (e) {
    toast(e.message, "error");
  }
}

function collectTxnFilters() {
  return {
    type: $("#f-type").value,
    category_id: $("#f-category").value,
    date_from: $("#f-date-from").value,
    date_to: $("#f-date-to").value,
  };
}

/* ---------- budgets ---------- */

async function renderBudgets() {
  try {
    const budgets = await api.budgets.list();
    state.budgets = budgets;
    $("#budget-grid").innerHTML = budgets.length
      ? budgets.map(budgetRow).join("")
      : '<div class="card empty">Chưa có hạn mức nào. Nhấn "+ Thêm hạn mức" để bắt đầu.</div>';
  } catch (e) {
    toast(e.message, "error");
  }
}

/* ---------- categories ---------- */

function catItem(c) {
  return `
  <div class="cat-item">
    <div class="cat-icon">${c.icon || "🏷️"}</div>
    <div class="cat-name">
      ${c.name}
      ${c.is_default ? '<span class="cat-badge">· mặc định</span>' : ""}
    </div>
    <button class="btn-icon" data-action="category-edit" data-id="${c.id}" title="Sửa">✏️</button>
    <button class="btn-icon" data-action="category-delete" data-id="${c.id}" title="Xóa">🗑️</button>
  </div>`;
}

async function renderCategories() {
  try {
    if (!state.categories.length) await loadCategories();
    const expense = state.categories.filter((c) => c.type === "expense");
    const income = state.categories.filter((c) => c.type === "income");
    $("#cat-expense").innerHTML = expense.length
      ? expense.map(catItem).join("")
      : '<div class="empty">Chưa có danh mục chi tiêu.</div>';
    $("#cat-income").innerHTML = income.length
      ? income.map(catItem).join("")
      : '<div class="empty">Chưa có danh mục thu nhập.</div>';
  } catch (e) {
    toast(e.message, "error");
  }
}

/* ---------- alerts ---------- */

function alertItemHtml(a) {
  const statusClass = a.is_read ? "read" : "unread";
  const statusPill = a.is_read
    ? '<span class="alert-status read-status">Đã đọc ✓</span>'
    : '<span class="alert-status unread-status">Chưa đọc</span>';
  const levelTag = a.level === "danger" ? "tag-expense" : "alert-level-warning";
  const meta = `${a.budget_name ? `<span class="tag ${levelTag}">${a.budget_name}</span> ` : ""}${a.category_name ? `<span class="tag">${a.category_name}</span> ` : ""}${fmtDate(a.created_at)}`;
  return `
  <div class="alert-item ${statusClass}">
    <div class="alert-icon">${a.level === "danger" ? "🚨" : "⚠️"}</div>
    <div class="alert-msg">
      <div class="alert-msg-title">${a.message}</div>
      <div class="alert-meta">${meta}</div>
    </div>
    ${statusPill}
    ${a.is_read ? "" : `<button class="btn btn-small" data-action="alert-read" data-id="${a.id}">Đánh dấu đã đọc</button>`}
  </div>`;
}

function alertRow(a) {
  return alertItemHtml(a);
}

async function renderAlerts() {
  try {
    const alerts = await api.alerts.list(false);
    $("#alert-list").innerHTML = alerts.length
      ? alerts.map(alertRow).join("")
      : '<div class="empty">Không có cảnh báo nào. 🎉</div>';
    refreshBadge();
  } catch (e) {
    toast(e.message, "error");
  }
}

/* ---------- modal ---------- */

function openModal(title, bodyHtml, modalType, id) {
  state.modal = { type: modalType, id: id || null };
  $("#modal-title").textContent = title;
  $("#modal-body").innerHTML = bodyHtml;
  $("#modal-overlay").classList.remove("hidden");
  bindModalForm(modalType);
}

function closeModal() {
  state.modal = null;
  $("#modal-overlay").classList.add("hidden");
  $("#modal-body").innerHTML = "";
}

function txnCategoryOptions(selected, type) {
  return state.categories
    .filter((c) => c.type === (type || "expense"))
    .map(
      (c) =>
        `<option value="${c.id}" ${c.id === selected ? "selected" : ""}>${c.icon || ""} ${c.name}</option>`
    )
    .join("");
}

function openTxnModal(txn) {
  const isEdit = !!txn;
  const type = txn ? txn.type : "expense";
  openModal(
    isEdit ? "Sửa giao dịch" : "Thêm giao dịch",
    `
    <div class="form-group">
      <label>Loại</label>
      <select id="m-type" data-bind="type">
        <option value="expense" ${type === "expense" ? "selected" : ""}>Chi tiêu</option>
        <option value="income" ${type === "income" ? "selected" : ""}>Thu nhập</option>
      </select>
    </div>
    <div class="form-group">
      <label>Số tiền (VNĐ)</label>
      <input type="number" id="m-amount" data-bind="amount" min="1" step="1000" value="${txn ? txn.amount : ""}" required />
    </div>
    <div class="form-group">
      <label>Danh mục</label>
      <select id="m-category" data-bind="category_id">
        ${txnCategoryOptions(txn ? txn.category_id : null, type)}
      </select>
    </div>
    <div class="form-group">
      <label>Ngày</label>
      <input type="date" id="m-date" data-bind="transaction_date" value="${txn ? txn.transaction_date : new Date().toISOString().slice(0, 10)}" required />
    </div>
    <div class="form-group">
      <label>Ghi chú</label>
      <input type="text" id="m-note" data-bind="note" maxlength="255" value="${(txn && txn.note) || ""}" placeholder="Ví dụ: Đi ăn tối..." />
    </div>`,
    "transaction",
    txn ? txn.id : null
  );
}

function openCategoryModal(cat) {
  const isEdit = !!cat;
  const type = cat ? cat.type : "expense";
  openModal(
    isEdit ? "Sửa danh mục" : "Thêm danh mục",
    `
    <div class="form-group">
      <label>Tên</label>
      <input type="text" id="m-name" data-bind="name" value="${(cat && cat.name) || ""}" maxlength="100" required />
    </div>
    <div class="form-group">
      <label>Loại</label>
      <select id="m-type" data-bind="type" ${isEdit ? "disabled" : ""}>
        <option value="expense" ${type === "expense" ? "selected" : ""}>Chi tiêu</option>
        <option value="income" ${type === "income" ? "selected" : ""}>Thu nhập</option>
      </select>
      ${isEdit ? '<div class="hint">Không thể đổi loại danh mục.</div>' : ""}
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Biểu tượng (emoji)</label>
        <input type="text" id="m-icon" data-bind="icon" value="${(cat && cat.icon) || ""}" maxlength="20" />
      </div>
      <div class="form-group">
        <label>Màu</label>
        <input type="color" id="m-color" data-bind="color" value="${(cat && cat.color) || "#6b7280"}" />
      </div>
    </div>`,
    "category",
    cat ? cat.id : null
  );
}

function openBudgetModal(budget) {
  const isEdit = !!budget;
  const categoryId = budget ? budget.category_id : "";
  openModal(
    isEdit ? "Sửa hạn mức" : "Thêm hạn mức",
    `
    <div class="form-group">
      <label>Tên hạn mức</label>
      <input type="text" id="m-name" data-bind="name" value="${(budget && budget.name) || ""}" maxlength="100" required />
    </div>
    <div class="form-group">
      <label>Số tiền (VNĐ)</label>
      <input type="number" id="m-amount" data-bind="amount" min="1" step="1000" value="${budget ? budget.amount : ""}" required />
    </div>
    <div class="form-group">
      <label>Danh mục (để trống = hạn mức tổng thể)</label>
      <select id="m-category" data-bind="category_id">
        <option value="">— Tổng thể (mọi chi tiêu) —</option>
        ${txnCategoryOptions(categoryId, "expense")}
      </select>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Chu kỳ</label>
        <select id="m-period" data-bind="period">
          <option value="monthly" ${(budget && budget.period) === "yearly" ? "" : "selected"}>Theo tháng</option>
          <option value="yearly" ${(budget && budget.period) === "yearly" ? "selected" : ""}>Theo năm</option>
        </select>
      </div>
      <div class="form-group">
        <label>Ngưỡng cảnh báo (%)</label>
        <input type="number" id="m-threshold" data-bind="alert_threshold" min="1" max="100" value="${(budget && budget.alert_threshold) || 80}" />
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Bắt đầu</label>
        <input type="date" id="m-start" data-bind="start_date" value="${(budget && budget.start_date) || new Date().toISOString().slice(0, 10)}" />
      </div>
      <div class="form-group">
        <label>Kết thúc (tùy chọn)</label>
        <input type="date" id="m-end" data-bind="end_date" value="${(budget && budget.end_date) || ""}" />
      </div>
    </div>
    <div class="form-check">
      <input type="checkbox" id="m-active" data-bind="is_active" ${!budget || budget.is_active ? "checked" : ""} />
      <label for="m-active" style="font-weight:400;">Hạn mức đang hoạt động</label>
    </div>`,
    "budget",
    budget ? budget.id : null
  );
}

function bindModalForm(type) {
  const typeSel = $("#m-type");
  if (type === "transaction" && typeSel) {
    typeSel.addEventListener("change", () => {
      const catSel = $("#m-category");
      if (catSel) {
        catSel.innerHTML = txnCategoryOptions(null, typeSel.value);
      }
    });
  }
}

function readModalForm() {
  const data = {};
  $$("#modal-body [data-bind]").forEach((el) => {
    if (el.type === "checkbox") {
      data[el.dataset.bind] = el.checked;
    } else {
      let val = el.value;
      if (el.dataset.bind === "category_id" && val === "") val = null;
      if (el.dataset.bind === "end_date" && val === "") val = null;
      data[el.dataset.bind] = val;
    }
  });
  return data;
}

async function saveModal() {
  const m = state.modal;
  if (!m) return;
  try {
    const data = readModalForm();
    if (m.type === "transaction") {
      data.amount = Number(data.amount);
      data.category_id = Number(data.category_id);
      if (!data.amount || !data.category_id) throw new Error("Vui lòng nhập đầy đủ thông tin");
      if (m.id) await api.transactions.update(m.id, data);
      else await api.transactions.create(data);
      toast(m.id ? "Đã cập nhật giao dịch" : "Đã thêm giao dịch");
    } else if (m.type === "category") {
      if (m.id) {
        await api.categories.update(m.id, { name: data.name, icon: data.icon, color: data.color });
      } else {
        await api.categories.create(data);
      }
      toast(m.id ? "Đã cập nhật danh mục" : "Đã thêm danh mục");
      await loadCategories();
    } else if (m.type === "budget") {
      data.amount = Number(data.amount);
      data.alert_threshold = Number(data.alert_threshold);
      if (!data.amount) throw new Error("Vui lòng nhập số tiền");
      if (m.id) await api.budgets.update(m.id, data);
      else await api.budgets.create(data);
      toast(m.id ? "Đã cập nhật hạn mức" : "Đã thêm hạn mức");
    }
    closeModal();
    refreshBadge();
    if (state.view === "dashboard") renderDashboard();
    if (state.view === "transactions") renderTransactions();
    if (state.view === "budgets") renderBudgets();
    if (state.view === "categories") renderCategories();
    if (state.view === "alerts") renderAlerts();
  } catch (e) {
    toast(e.message, "error");
  }
}

/* ---------- global actions ---------- */

function handleAction(action, target) {
  switch (action) {
    case "goto-dashboard":
      switchView("dashboard");
      break;
    case "goto-transactions":
      switchView("transactions");
      break;
    case "goto-budgets":
      switchView("budgets");
      break;
    case "goto-alerts":
      switchView("alerts");
      break;

    case "txn-create":
      openTxnModal(null);
      break;
    case "txn-edit":
      openTxnModal(state.txn.items ? state.txn.items.find((t) => t.id === Number(target.dataset.id)) : null);
      break;
    case "txn-delete":
      confirmDelete("giao dịch này", () => api.transactions.remove(target.dataset.id), renderTransactions);
      break;
    case "txn-filter":
      state.txn.filters = collectTxnFilters();
      state.txn.page = 1;
      renderTransactions();
      break;
    case "txn-reset":
      $("#f-type").value = "";
      $("#f-category").value = "";
      $("#f-date-from").value = "";
      $("#f-date-to").value = "";
      state.txn.filters = {};
      state.txn.page = 1;
      renderTransactions();
      break;
    case "txn-page":
      state.txn.page = Number(target.dataset.page);
      renderTransactions();
      break;

    case "budget-create":
      openBudgetModal(null);
      break;
    case "budget-edit":
      openBudgetModal(state.budgets ? state.budgets.find((b) => b.id === Number(target.dataset.id)) : null);
      break;
    case "budget-delete":
      confirmDelete("hạn mức này", () => api.budgets.remove(target.dataset.id), renderBudgets);
      break;

    case "category-create":
      openCategoryModal(null);
      break;
    case "category-edit":
      openCategoryModal(state.categories.find((c) => c.id === Number(target.dataset.id)));
      break;
    case "category-delete":
      confirmDelete("danh mục này", async () => {
        await api.categories.remove(target.dataset.id);
        await loadCategories();
      }, renderCategories);
      break;

    case "alert-check":
      api.alerts.check().then((r) => {
        toast(r.message);
        renderAlerts();
        refreshBadge();
      }).catch((e) => toast(e.message, "error"));
      break;
    case "alert-read-all":
      api.alerts.markAllRead().then((r) => {
        toast(r.message);
        renderAlerts();
        refreshBadge();
      }).catch((e) => toast(e.message, "error"));
      break;
    case "alert-read":
      api.alerts.markRead(target.dataset.id).then(() => {
        renderAlerts();
        refreshBadge();
      }).catch((e) => toast(e.message, "error"));
      break;

    case "modal-close":
      closeModal();
      break;
    case "modal-save":
      saveModal();
      break;
  }
}

async function confirmDelete(what, fn, rerender) {
  if (!confirm(`Bạn có chắc muốn xóa ${what}?`)) return;
  try {
    await fn();
    toast("Đã xóa");
    refreshBadge();
    if (state.view === "dashboard") renderDashboard();
    else rerender();
  } catch (e) {
    toast(e.message, "error");
  }
}

/* ---------- init ---------- */

function init() {
  const now = new Date();
  $("#current-month").textContent = `Tháng ${now.getMonth() + 1}/${now.getFullYear()}`;

  $$(".tab").forEach((t) =>
    t.addEventListener("click", () => switchView(t.dataset.view))
  );

  document.addEventListener("click", (e) => {
    const el = e.target.closest("[data-action]");
    if (el) handleAction(el.dataset.action, el);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });

  Promise.all([loadCategories()])
    .then(() => renderDashboard())
    .catch((e) => toast(e.message, "error"));
}

document.addEventListener("DOMContentLoaded", init);

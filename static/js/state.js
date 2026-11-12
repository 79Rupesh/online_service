/**
 * MP Suvidha: State Management and Core UI Utilities
 */
const State = {
  token: localStorage.getItem("mpsuvidha_token") || "",
  user: null,
  services: [],
  categories: [],
  popularServices: [],
  stats: {},
  evaluations: [],
  evaluationGroups: [],
  feedbackSummary: {},
  page: 1,
  limit: 9,
  totalPages: 1,
  activeFilters: {
    q: "",
    category: "",
    department: "",
    sort: "az"
  },
  currentEvaluationScores: {},
  currentFeedbackRating: 0
};

// DOM query shortcuts
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

// Sanitize string to prevent XSS
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[ch]));
}

// Display Toast Alert Notification
function toast(message, type = "info") {
  const container = $("#toast-container");
  if (!container) return;

  const item = document.createElement("div");
  item.className = `toast ${type}`;
  
  let icon = "ℹ";
  if (type === "success") icon = "✓";
  if (type === "error") icon = "✕";
  if (type === "warning") icon = "⚠";

  item.innerHTML = `<span style="font-weight:800">${icon}</span><span>${escapeHtml(message)}</span>`;
  container.appendChild(item);

  setTimeout(() => {
    item.style.opacity = "0";
    item.style.transform = "translateY(8px)";
    item.style.transition = "all 0.25s ease";
    setTimeout(() => item.remove(), 250);
  }, 4200);
}

// Format ISO date strings
function formatDate(dateString) {
  if (!dateString) return "—";
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return escapeHtml(dateString);
  const locale = I18N.currentLang === "hi" ? "hi-IN" : "en-IN";
  return new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "short",
    day: "numeric"
  }).format(date);
}

// Modal open/close handlers
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  modal.classList.remove("hidden");
  document.body.style.overflow = "hidden";
  const firstInput = modal.querySelector("input:not([type=hidden]), select, textarea, button.btn-primary");
  if (firstInput) setTimeout(() => firstInput.focus(), 60);
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  modal.classList.add("hidden");
  if (!$$(".modal-overlay:not(.hidden)").length) {
    document.body.style.overflow = "";
  }
}


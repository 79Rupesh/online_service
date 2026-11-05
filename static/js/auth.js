/**
 * MP Suvidha: Authentication, Sessions, and Role Control
 * Bilingual user management
 */
const Auth = {
  openModal(mode = "login") {
    this.setMode(mode);
    openModal("auth-modal");
  },

  setMode(mode) {
    const isRegister = mode === "register";
    const form = $("#auth-form");
    if (!form) return;

    form.elements.mode.value = isRegister ? "register" : "login";

    $$(".register-field", form).forEach(el => {
      el.classList.toggle("hidden", !isRegister);
    });

    if (form.elements.name) form.elements.name.required = isRegister;
    if (form.elements.mobile) form.elements.mobile.required = isRegister;

    $$("[data-auth-tab]").forEach(tab => {
      tab.classList.toggle("active", tab.dataset.authTab === mode);
    });

    const titleEl = $("#auth-modal-title");
    if (titleEl) {
      titleEl.textContent = isRegister ? I18N.t("auth_register_title") : I18N.t("auth_login_title");
    }

    const submitBtn = $("#auth-submit-btn");
    if (submitBtn) {
      submitBtn.textContent = isRegister ? I18N.t("auth_btn_register") : I18N.t("auth_btn_login");
    }
  },

  async handleAuthSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const mode = form.elements.mode.value;
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    if (mode === "register") {
      if (payload.password.length < 8) {
        return toast(I18N.currentLang === "hi" ? "पासवर्ड कम से कम ८ अक्षरों का होना चाहिए।" : "Password must contain at least 8 characters.", "error");
      }
    }

    const submitBtn = $("#auth-submit-btn");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = I18N.currentLang === "hi" ? "सत्यापित किया जा रहा है..." : "Processing...";
    }

    try {
      const result = await api(`/auth/${mode}`, {
        method: "POST",
        body: JSON.stringify(payload)
      });

      State.token = result.token;
      State.user = result.user;
      localStorage.setItem("mpsuvidha_token", State.token);
      localStorage.setItem("janseva_token", State.token);

      closeModal("auth-modal");
      form.reset();
      this.updateUI();

      const welcomeMsg = I18N.currentLang === "hi" ? `स्वागत है, ${State.user.name}!` : `Welcome back, ${State.user.name}!`;
      toast(welcomeMsg, "success");

      // Load user personal dashboard data
      if (typeof Dashboard !== "undefined") {
        await Dashboard.loadDashboard();
      }
      if (window.Router) {
        window.Router.navigateTo("dashboard");
      }
    } catch (err) {
      toast(err.message, "error");
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = mode === "register" ? I18N.t("auth_btn_register") : I18N.t("auth_btn_login");
      }
    }
  },

  updateUI() {
    const isLoggedIn = Boolean(State.user);
    
    // Header controls
    const loginBtn = $("#header-login-btn");
    const registerBtn = $("#header-register-btn");
    const accountBtn = $("#header-account-btn");
    const notifBtn = $("#header-notif-btn");
    const navDashboardLink = $("#nav-dashboard-link");
    const mobileNavDashboardLink = $("#mobile-nav-dashboard-link");

    if (loginBtn) loginBtn.classList.toggle("hidden", isLoggedIn);
    if (registerBtn) registerBtn.classList.toggle("hidden", isLoggedIn);
    if (accountBtn) accountBtn.classList.toggle("hidden", !isLoggedIn);
    if (notifBtn) notifBtn.classList.toggle("hidden", !isLoggedIn);
    if (navDashboardLink) navDashboardLink.classList.toggle("hidden", !isLoggedIn);
    if (mobileNavDashboardLink) mobileNavDashboardLink.classList.toggle("hidden", !isLoggedIn);

    if (isLoggedIn && State.user) {
      const initials = State.user.name
        .split(/\s+/)
        .map(part => part[0])
        .slice(0, 2)
        .join("")
        .toUpperCase();
      const avatarText = $("#avatar-initials");
      if (avatarText) avatarText.textContent = initials || "U";
    }
  },

  async restoreSession() {
    State.token = localStorage.getItem("mpsuvidha_token") || localStorage.getItem("janseva_token") || "";
    if (!State.token) {
      this.updateUI();
      return;
    }
    try {
      State.user = await api("/auth/me");
      this.updateUI();
      if (typeof Dashboard !== "undefined") {
        await Dashboard.loadDashboard();
      }
    } catch (err) {
      // Token expired or invalid
      State.token = "";
      State.user = null;
      localStorage.removeItem("mpsuvidha_token");
      localStorage.removeItem("janseva_token");
      this.updateUI();
    }
  },

  logout() {
    State.token = "";
    State.user = null;
    localStorage.removeItem("mpsuvidha_token");
    localStorage.removeItem("janseva_token");
    this.updateUI();

    const dashSection = $("#dashboard-section");
    if (dashSection) dashSection.classList.add("hidden");

    toast(I18N.currentLang === "hi" ? "आप सफलतापूर्वक लॉग आउट हो गए हैं।" : "You have successfully signed out.", "info");
    if (window.Router) {
      window.Router.navigateTo("home");
    } else {
      window.location.hash = "#home";
    }
  },

  async handleProfileUpdate(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = Object.fromEntries(new FormData(form).entries());

    try {
      await api("/auth/profile", {
        method: "PATCH",
        body: JSON.stringify(payload)
      });
      State.user.name = payload.name;
      State.user.mobile = payload.mobile;
      State.user.address = payload.address;
      this.updateUI();
      if (typeof Dashboard !== "undefined") {
        Dashboard.renderProfile();
      }
      toast(I18N.currentLang === "hi" ? "प्रोफ़ाइल सफलतापूर्वक अद्यतन की गई।" : "Profile updated successfully.", "success");
      form.classList.add("hidden");
    } catch (err) {
      toast(err.message, "error");
    }
  }
};

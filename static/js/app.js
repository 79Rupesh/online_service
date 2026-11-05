/**
 * MP Suvidha: Main Application Bootstrapper, SPA Router & Event Handlers
 * Features:
 * - 1-Second Page Transition Loader (SPA view switcher without browser page refresh)
 * - Complete Bilingual Navigation & Content
 * - Event Delegation & API Integrations
 */
(() => {
  "use strict";

  let searchDebounceTimer = null;

  // =========================================================================
  // SPA ROUTER: 1-Second Page Transition System
  // =========================================================================
  const Router = {
    currentView: "home",
    isTransitioning: false,
    timerId: null,

    statusMessages: {
      en: {
        home: "Loading MP Suvidha Portal...",
        services: "Loading Citizen Services...",
        categories: "Loading Service Categories...",
        tracking: "Loading Application Tracker...",
        verify: "Loading Verification Portal...",
        about: "Loading About MP Suvidha...",
        help: "Loading Help & Support Centre...",
        dashboard: "Loading Your Dashboard..."
      },
      hi: {
        home: "एमपी सुविधा पोर्टल लोड हो रहा है...",
        services: "नागरिक सेवाएँ लोड हो रही हैं...",
        categories: "सेवा श्रेणियाँ लोड हो रही हैं...",
        tracking: "आवेदन ट्रैकिंग लोड हो रही है...",
        verify: "प्रमाण पत्र सत्यापन लोड हो रहा है...",
        about: "एमपी सुविधा के बारे में लोड हो रहा है...",
        help: "सहायता एवं सहायता केंद्र लोड हो रहा है...",
        dashboard: "आपका डैशबोर्ड लोड हो रहा है..."
      }
    },

    getStatusText(viewName) {
      const lang = (window.I18N && I18N.currentLang === "hi") ? "hi" : "en";
      const dict = this.statusMessages[lang] || this.statusMessages.en;
      return dict[viewName] || (lang === "hi" ? "कृपया प्रतीक्षा करें..." : "Loading page, please wait...");
    },

    /**
     * Navigate to a view with a 1-second simulated page load
     * @param {string} targetView - view name (e.g. 'home', 'services', 'tracking')
     * @param {boolean} immediate - if true, switches without 1s loader animation (used on initial load)
     * @param {function} callback - optional callback after DOM switch
     */
    navigateTo(targetView, immediate = false, callback = null) {
      if (!targetView) targetView = "home";
      targetView = targetView.replace(/^#/, "").trim();

      // Check if view container exists
      const targetEl = document.querySelector(`[data-view="${targetView}"]`);
      if (!targetEl) {
        targetView = "home";
      }

      if (this.isTransitioning) {
        return;
      }

      // Close mobile navigation drawer if open
      const mobileDrawer = document.getElementById("mobile-nav-drawer");
      const mobileToggle = document.getElementById("mobile-menu-toggle");
      if (mobileDrawer && mobileDrawer.classList.contains("open")) {
        mobileDrawer.classList.remove("open");
        if (mobileToggle) mobileToggle.setAttribute("aria-expanded", "false");
      }

      // Immediate switch (e.g. initial load or programmatic reset)
      if (immediate) {
        this.switchActiveDOM(targetView);
        if (typeof callback === "function") callback();
        return;
      }

      // 1-Second Page Transition Loader
      this.isTransitioning = true;
      const loader = document.getElementById("page-loader");
      const progressBar = document.getElementById("loader-progress-bar");
      const statusText = document.getElementById("loader-status-text");

      if (statusText) {
        statusText.textContent = this.getStatusText(targetView);
      }

      if (progressBar) {
        progressBar.style.transition = "none";
        progressBar.style.width = "0%";
        void progressBar.offsetWidth; // Force CSS reflow
        progressBar.style.transition = "width 0.85s cubic-bezier(0.4, 0, 0.2, 1)";
        progressBar.style.width = "100%";
      }

      if (loader) {
        loader.classList.remove("hidden");
      }

      clearTimeout(this.timerId);

      // Switch view DOM content at ~650ms while loader covers screen
      setTimeout(() => {
        this.switchActiveDOM(targetView);
        if (typeof callback === "function") {
          try {
            callback();
          } catch (err) {
            console.error("Router callback error:", err);
          }
        }
      }, 650);

      // Hide loader at 1000ms (1-second full transition)
      this.timerId = setTimeout(() => {
        if (loader) {
          loader.classList.add("hidden");
        }
        this.isTransitioning = false;
        if (progressBar) {
          progressBar.style.width = "0%";
        }
      }, 1000);
    },

    switchActiveDOM(targetView) {
      this.currentView = targetView;

      // 1. Toggle visibility of page views
      const allViews = document.querySelectorAll("[data-view]");
      allViews.forEach(view => {
        if (view.dataset.view === targetView) {
          view.classList.remove("hidden");
        } else {
          view.classList.add("hidden");
        }
      });

      // 2. Instant jump to top of the page (no smooth sliding)
      window.scrollTo({ top: 0, left: 0, behavior: "instant" });

      // 3. Update active nav link classes
      const allNavLinks = document.querySelectorAll(".nav-link[data-nav]");
      allNavLinks.forEach(link => {
        if (link.dataset.nav === targetView) {
          link.classList.add("active");
        } else {
          link.classList.remove("active");
        }
      });

      // 4. Update address bar hash without trigger loop
      if (window.history && window.history.pushState) {
        window.history.pushState(null, "", `#${targetView}`);
      } else {
        window.location.hash = `#${targetView}`;
      }
    }
  };

  // Expose Router globally
  window.Router = Router;

  // =========================================================================
  // EVENT BINDINGS
  // =========================================================================
  function bindEvents() {
    // 1. Accessibility font resizing
    const btnFontUp = $("#btn-font-increase");
    const btnFontDown = $("#btn-font-decrease");
    const btnFontReset = $("#btn-font-reset");

    if (btnFontUp) btnFontUp.addEventListener("click", () => document.body.classList.add("large-text"));
    if (btnFontDown) btnFontDown.addEventListener("click", () => document.body.classList.remove("large-text"));
    if (btnFontReset) btnFontReset.addEventListener("click", () => document.body.classList.remove("large-text"));

    // 2. Language switch
    const langSelect = $("#language-select");
    if (langSelect) {
      langSelect.addEventListener("change", (e) => {
        I18N.setLanguage(e.target.value);
        // Refresh dynamic components in current view
        if (Router.currentView === "services") {
          Services.loadServices(State.currentPage || 1);
        } else if (Router.currentView === "dashboard" && typeof Dashboard !== "undefined") {
          Dashboard.loadDashboard();
        }
      });
    }

    // 3. Mobile menu drawer toggle
    const mobileToggle = $("#mobile-menu-toggle");
    const mobileDrawer = $("#mobile-nav-drawer");
    if (mobileToggle && mobileDrawer) {
      mobileToggle.addEventListener("click", () => {
        const isOpen = mobileDrawer.classList.toggle("open");
        mobileToggle.setAttribute("aria-expanded", String(isOpen));
      });
    }

    // 4. Global Navigation clicks (All elements with data-nav)
    document.addEventListener("click", (e) => {
      const navItem = e.target.closest("[data-nav]");
      if (navItem) {
        e.preventDefault();
        const targetView = navItem.dataset.nav;
        Router.navigateTo(targetView);
      }
    });

    // 5. Header Account Button (opens dashboard)
    const accountBtn = $("#header-account-btn");
    if (accountBtn) {
      accountBtn.addEventListener("click", (e) => {
        e.preventDefault();
        Router.navigateTo("dashboard");
      });
    }

    // 6. Auth Modal & Tabs
    const loginBtn = $("#header-login-btn");
    const registerBtn = $("#header-register-btn");
    const logoutBtn = $("#dash-logout-btn");
    const authForm = $("#auth-form");

    if (loginBtn) loginBtn.addEventListener("click", () => Auth.openModal("login"));
    if (registerBtn) registerBtn.addEventListener("click", () => Auth.openModal("register"));
    if (logoutBtn) logoutBtn.addEventListener("click", () => Auth.logout());
    if (authForm) authForm.addEventListener("submit", (e) => Auth.handleAuthSubmit(e));

    $$("[data-auth-tab]").forEach(tab => {
      tab.addEventListener("click", () => Auth.setMode(tab.dataset.authTab));
    });

    // Quick-Fill Demo Logins
    $$("[data-demo-creds]").forEach(btn => {
      btn.addEventListener("click", () => {
        const [email, pwd] = btn.dataset.demoCreds.split("|");
        Auth.setMode("login");
        const form = $("#auth-form");
        if (form) {
          form.elements.email.value = email;
          form.elements.password.value = pwd;
          form.requestSubmit();
        }
      });
    });

    // Profile form
    const profileEditToggle = $("#btn-toggle-edit-profile");
    const profileEditForm = $("#profile-edit-form");
    if (profileEditToggle && profileEditForm) {
      profileEditToggle.addEventListener("click", () => {
        profileEditForm.classList.toggle("hidden");
      });
      profileEditForm.addEventListener("submit", (e) => Auth.handleProfileUpdate(e));
    }

    // 7. Hero Service Search Form
    const heroSearchForm = $("#hero-search-form");
    const heroSearchInput = $("#hero-search-input");
    if (heroSearchForm && heroSearchInput) {
      heroSearchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const query = heroSearchInput.value.trim();
        State.activeFilters.q = query;
        const directoryInput = $("#directory-search-input");
        if (directoryInput) directoryInput.value = query;

        // Navigate to services with 1-second transition
        Router.navigateTo("services", false, () => {
          Services.loadServices(1);
        });
      });
    }

    // Popular tag buttons
    $$("[data-popular-query]").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const query = btn.dataset.popularQuery;
        if (heroSearchInput) heroSearchInput.value = query;
        State.activeFilters.q = query;
        const directoryInput = $("#directory-search-input");
        if (directoryInput) directoryInput.value = query;

        Router.navigateTo("services", false, () => {
          Services.loadServices(1);
        });
      });
    });

    // 8. Service Directory Filtering & Search
    const dirSearchInput = $("#directory-search-input");
    if (dirSearchInput) {
      dirSearchInput.addEventListener("input", () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
          State.activeFilters.q = dirSearchInput.value.trim();
          Services.loadServices(1);
        }, 280);
      });
    }

    const catFilter = $("#category-filter-select");
    const filterChipsWrap = $("#service-filter-chips");

    if (filterChipsWrap) {
      filterChipsWrap.addEventListener("click", (e) => {
        const chip = e.target.closest("[data-filter-chip]");
        if (!chip) return;
        $$(".filter-chip", filterChipsWrap).forEach(c => c.classList.remove("active"));
        chip.classList.add("active");
        const cat = chip.dataset.filterChip;
        State.activeFilters.category = cat;
        if (catFilter) catFilter.value = cat;
        Services.loadServices(1);
      });
    }

    if (catFilter) {
      catFilter.addEventListener("change", () => {
        State.activeFilters.category = catFilter.value;
        if (filterChipsWrap) {
          $$(".filter-chip", filterChipsWrap).forEach(c => {
            c.classList.toggle("active", c.dataset.filterChip === catFilter.value);
          });
        }
        Services.loadServices(1);
      });
    }

    const deptFilter = $("#department-filter-select");
    if (deptFilter) {
      deptFilter.addEventListener("change", () => {
        State.activeFilters.department = deptFilter.value;
        Services.loadServices(1);
      });
    }

    const sortFilter = $("#services-sort-select");
    if (sortFilter) {
      sortFilter.addEventListener("change", () => {
        State.activeFilters.sort = sortFilter.value;
        Services.loadServices(1);
      });
    }

    // Category Grid click delegation (on Home or Categories view)
    const catGrid = $("#category-cards-grid");
    if (catGrid) {
      catGrid.addEventListener("click", (e) => {
        const card = e.target.closest("[data-category-click]");
        if (!card) return;
        const cat = card.dataset.categoryClick;
        State.activeFilters.category = cat;
        if (catFilter) catFilter.value = cat;

        Router.navigateTo("services", false, () => {
          Services.loadServices(1);
        });
      });
    }

    // Also handle categories view page grid
    const fullCatGrid = $("#all-categories-grid");
    if (fullCatGrid) {
      fullCatGrid.addEventListener("click", (e) => {
        const card = e.target.closest("[data-category-click]");
        if (!card) return;
        const cat = card.dataset.categoryClick;
        State.activeFilters.category = cat;
        if (catFilter) catFilter.value = cat;

        Router.navigateTo("services", false, () => {
          Services.loadServices(1);
        });
      });
    }

    // Services Grid click delegation (Apply & Details)
    const servicesGrid = $("#services-directory-grid");
    if (servicesGrid) {
      servicesGrid.addEventListener("click", (e) => {
        const applyBtn = e.target.closest("[data-apply-svc]");
        const detailsBtn = e.target.closest("[data-details-svc]");
        if (applyBtn) {
          Services.openApplicationModal(applyBtn.dataset.applySvc);
        } else if (detailsBtn) {
          Services.showDetailsModal(detailsBtn.dataset.detailsSvc);
        }
      });
    }

    // Popular Services Grid click delegation
    const popGrid = $("#popular-services-grid");
    if (popGrid) {
      popGrid.addEventListener("click", (e) => {
        const applyBtn = e.target.closest("[data-apply-svc]");
        const detailsBtn = e.target.closest("[data-details-svc]");
        if (applyBtn) {
          Services.openApplicationModal(applyBtn.dataset.applySvc);
        } else if (detailsBtn) {
          Services.showDetailsModal(detailsBtn.dataset.detailsSvc);
        }
      });
    }

    // Service details modal apply button
    document.addEventListener("click", (e) => {
      const applyFromModal = e.target.closest("[data-apply-from-modal]");
      if (applyFromModal) {
        const svcId = applyFromModal.dataset.applyFromModal;
        closeModal("service-details-modal");
        Services.openApplicationModal(svcId);
      }
    });

    // Pagination buttons click delegation
    const paginationWrap = $("#services-pagination");
    if (paginationWrap) {
      paginationWrap.addEventListener("click", (e) => {
        const pageBtn = e.target.closest("[data-page-btn]");
        if (!pageBtn || pageBtn.disabled) return;
        const targetPage = Number(pageBtn.dataset.pageBtn);
        Services.loadServices(targetPage);
        window.scrollTo({ top: 0, behavior: "instant" });
      });
    }

    // Application submission form
    const appSubmitForm = $("#application-submission-form");
    if (appSubmitForm) {
      appSubmitForm.addEventListener("submit", (e) => Services.handleApplicationSubmit(e));
    }

    // 9. Tracking form
    const trackForm = $("#tracking-lookup-form");
    if (trackForm) {
      trackForm.addEventListener("submit", (e) => Tracking.handleTrackSubmit(e));
    }

    // Quick track button from My Applications table
    document.addEventListener("click", (e) => {
      const quickTrackBtn = e.target.closest("[data-quick-track]");
      if (quickTrackBtn) {
        const appId = quickTrackBtn.dataset.quickTrack;
        const trackFormEl = $("#tracking-lookup-form");
        Router.navigateTo("tracking", false, () => {
          if (trackFormEl) {
            trackFormEl.elements.application_id.value = appId;
            if (State.user) {
              trackFormEl.elements.contact.value = State.user.email || State.user.mobile;
            }
            trackFormEl.requestSubmit();
          }
        });
      }
    });

    // 10. Certificate Verification form
    const verifyForm = $("#certificate-lookup-form");
    if (verifyForm) {
      verifyForm.addEventListener("submit", (e) => Verify.handleVerifySubmit(e));
    }

    // Sample certificate click
    $$("[data-sample-cert]").forEach(btn => {
      btn.addEventListener("click", () => {
        const certNum = btn.dataset.sampleCert;
        const certInput = $("#verify-certificate-input");
        if (certInput && verifyForm) {
          certInput.value = certNum;
          verifyForm.requestSubmit();
        }
      });
    });

    // 11. Feedback form
    const fbForm = $("#portal-feedback-form");
    if (fbForm) {
      fbForm.addEventListener("submit", (e) => Feedback.handleSubmit(e));
    }

    // 12. Officer review click delegation
    document.addEventListener("click", (e) => {
      const reviewBtn = e.target.closest("[data-officer-review-btn]");
      if (reviewBtn) Dashboard.openOfficerReviewModal(reviewBtn);
    });

    const officerReviewForm = $("#officer-review-form");
    if (officerReviewForm) {
      officerReviewForm.addEventListener("submit", (e) => Dashboard.handleOfficerReviewSubmit(e));
    }

    const officerFilterStatus = $("#officer-status-filter");
    if (officerFilterStatus) {
      officerFilterStatus.addEventListener("change", () => Dashboard.loadOfficerApplications());
    }

    // 13. Admin Controls delegation
    document.addEventListener("click", (e) => {
      // User role save
      const saveUserRole = e.target.closest("[data-save-user-role]");
      if (saveUserRole) {
        Dashboard.handleUserRoleSave(saveUserRole.dataset.saveUserRole);
      }

      // User active toggle
      const toggleUserActive = e.target.closest("[data-toggle-user-active]");
      if (toggleUserActive) {
        Dashboard.handleUserActiveToggle(
          toggleUserActive.dataset.toggleUserActive,
          toggleUserActive.dataset.currentActive
        );
      }

      // Service status toggle
      const toggleSvc = e.target.closest("[data-toggle-service-status]");
      if (toggleSvc) {
        Dashboard.handleServiceStatusToggle(
          toggleSvc.dataset.toggleServiceStatus,
          toggleSvc.dataset.currentAvail
        );
      }
    });

    // Admin Add Service form
    const adminSvcForm = $("#admin-add-service-form");
    if (adminSvcForm) {
      adminSvcForm.addEventListener("submit", (e) => Dashboard.handleAdminAddService(e));
    }

    // Admin Add Announcement form
    const adminNoticeForm = $("#admin-add-announcement-form");
    if (adminNoticeForm) {
      adminNoticeForm.addEventListener("submit", (e) => Dashboard.handleAdminAddAnnouncement(e));
    }

    // Admin Tab Navigation
    $$("[data-admin-tab]").forEach(tabBtn => {
      tabBtn.addEventListener("click", () => {
        const targetTab = tabBtn.dataset.adminTab;
        $$("[data-admin-tab]").forEach(btn => btn.classList.remove("active"));
        tabBtn.classList.add("active");

        $$(".admin-tab-panel").forEach(panel => {
          panel.classList.toggle("hidden", panel.id !== `admin-tab-panel-${targetTab}`);
        });
      });
    });

    // 14. Global Modal close listeners
    document.addEventListener("click", (e) => {
      const closeBtn = e.target.closest("[data-modal-close]");
      if (closeBtn) {
        closeModal(closeBtn.dataset.modalClose);
      } else if (e.target.classList.contains("modal-overlay")) {
        closeModal(e.target.id);
      }
    });

    // Close modals on Escape key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        $$(".modal-overlay:not(.hidden)").forEach(m => closeModal(m.id));
      }
    });

    // Reset filters button
    document.addEventListener("click", (e) => {
      if (e.target.id === "btn-reset-filters") {
        State.activeFilters = { q: "", category: "", department: "", sort: "az" };
        const dSearch = $("#directory-search-input");
        const cFilter = $("#category-filter-select");
        const deptFilter = $("#department-filter-select");
        if (dSearch) dSearch.value = "";
        if (cFilter) cFilter.value = "";
        if (deptFilter) deptFilter.value = "";
        Services.loadServices(1);
      }
    });

    // Browser back / forward button handling
    window.addEventListener("popstate", () => {
      const hash = window.location.hash.replace(/^#/, "").trim();
      if (hash && hash !== Router.currentView) {
        Router.navigateTo(hash, true);
      }
    });
  }

  // =========================================================================
  // APPLICATION BOOTSTRAPPER
  // =========================================================================
  async function initApp() {
    // Current year in footer
    const yearEl = $("#footer-current-year");
    if (yearEl) yearEl.textContent = new Date().getFullYear();

    // Setup Language
    I18N.setLanguage(I18N.currentLang);

    // Setup Event Listeners
    bindEvents();

    // Load initial essential data in parallel
    await Promise.all([
      Services.loadCategories(),
      Services.loadDepartments(),
      Services.loadServices(1),
      Dashboard.loadPublicStats(),
      Dashboard.loadAnnouncements(),
      Feedback.init()
    ]);

    // Restore existing authentication session
    await Auth.restoreSession();

    // Activate initial view based on URL hash or default to 'home'
    const initialHash = window.location.hash.replace(/^#/, "").trim();
    if (initialHash && document.querySelector(`[data-view="${initialHash}"]`)) {
      Router.navigateTo(initialHash, true);
    } else {
      Router.navigateTo("home", true);
    }
  }

  document.addEventListener("DOMContentLoaded", initApp);
})();

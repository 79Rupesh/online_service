/**
 * JanSeva Connect: Citizen, Officer, and Admin Dashboards & Analytics
 */
const Dashboard = {
  async loadPublicStats() {
    try {
      const data = await api("/dashboard/stats");
      State.stats = data.counts;
      State.popularServices = data.popular || [];

      // Hero / section counters
      const servEl = $("#stat-counter-services");
      const userEl = $("#stat-counter-users");
      const appEl = $("#stat-counter-applications");
      const apprvEl = $("#stat-counter-approved");

      if (servEl) servEl.textContent = data.counts.services;
      if (userEl) userEl.textContent = data.counts.users;
      if (appEl) appEl.textContent = data.counts.applications;
      if (apprvEl) apprvEl.textContent = data.counts.approved;

      // Render Popular Services on Homepage
      const popularGrid = $("#popular-services-grid");
      if (popularGrid && data.popular) {
        const isHi = I18N.currentLang === "hi";
        popularGrid.innerHTML = data.popular.map(svc => {
          const svcName = isHi && svc.name_hi ? svc.name_hi : svc.name;
          const svcDept = isHi && svc.department_hi ? svc.department_hi : I18N.translateDepartment(svc.department);
          const svcCat = I18N.translateCategory(svc.category);
          return `
          <div class="service-card">
            <div>
              <div class="service-card-top">
                <span class="service-dept-badge">${escapeHtml(svcDept)}</span>
                <span class="badge badge-saffron">★ ${isHi ? "लोकप्रिय" : "Popular"}</span>
              </div>
              <div class="service-card-title">${escapeHtml(svcName)}</div>
              <div class="service-card-desc">${isHi ? "त्वरित समीक्षा एवं डिजिटल प्रमाणन हेतु सर्वाधिक अनुरोध की जाने वाली सेवा।" : "Frequently requested citizen service with expedited review workflows."}</div>
            </div>
            <div>
              <div class="service-card-meta">
                <div>
                  <span class="meta-item-label">${I18N.t("nav_categories")}:</span>
                  <div class="meta-item-val">${escapeHtml(svcCat)}</div>
                </div>
                <div>
                  <span class="meta-item-label">${isHi ? "कुल आवेदन" : "Applications"}:</span>
                  <div class="meta-item-val">${svc.application_count} ${isHi ? "प्रस्तुत" : "Submitted"}</div>
                </div>
              </div>
              <div class="service-card-actions">
                <button class="btn btn-primary btn-sm" data-apply-svc="${escapeHtml(svc.id)}">${I18N.t("btn_apply_now")} ↗</button>
                <button class="btn btn-outline btn-sm" data-details-svc="${escapeHtml(svc.id)}">${I18N.t("btn_view_details")}</button>
              </div>
            </div>
          </div>
        `;
        }).join("");

        $$("[data-apply-svc]", popularGrid).forEach(btn => {
          btn.addEventListener("click", () => Services.openApplicationModal(btn.dataset.applySvc));
        });
        $$("[data-details-svc]", popularGrid).forEach(btn => {
          btn.addEventListener("click", () => Services.showDetailsModal(btn.dataset.detailsSvc));
        });
      }
    } catch {
      // Non-critical
    }
  },

  async loadAnnouncements() {
    const listWrap = $("#announcements-list-wrap");
    if (!listWrap) return;
    try {
      const notices = await api("/announcements");
      const isHi = I18N.currentLang === "hi";
      if (!notices.length) {
        listWrap.innerHTML = `<p style="color:var(--text-muted)">${isHi ? "फिलहाल कोई नई सूचना उपलब्ध नहीं है।" : "No current announcements posted."}</p>`;
        return;
      }

      listWrap.innerHTML = notices.map(n => {
        const title = isHi && n.title_hi ? n.title_hi : n.title;
        const body = isHi && n.body_hi ? n.body_hi : n.body;
        return `
        <div class="announcement-card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem">
            <span class="badge badge-saffron">${escapeHtml(n.kind || "Notice")}</span>
            <small style="color:var(--text-muted); font-size:11px">${formatDate(n.published_at)}</small>
          </div>
          <h4 style="margin:0 0 0.35rem; color:var(--primary-navy); font-size:1.15rem">${escapeHtml(title)}</h4>
          <p style="margin:0; font-size:var(--text-sm); color:var(--text-body); line-height:1.6">${escapeHtml(body)}</p>
        </div>
      `;
      }).join("");
    } catch {
      // Non-critical
    }
  },

  async loadDashboard() {
    if (!State.user) return;

    const dashSection = $("#dashboard-section");
    if (dashSection) dashSection.classList.remove("hidden");

    $("#dash-user-name").textContent = State.user.name;
    $("#dash-user-role-label").textContent = State.user.role.toUpperCase();

    try {
      const data = await api("/dashboard/me");

      // Update Metrics
      const total = $("#metric-total-apps");
      const pending = $("#metric-pending-apps");
      const approved = $("#metric-approved-apps");
      const rejected = $("#metric-rejected-apps");

      if (total) total.textContent = data.counts.total;
      if (pending) pending.textContent = data.counts.pending;
      if (approved) approved.textContent = data.counts.approved;
      if (rejected) rejected.textContent = data.counts.rejected;

      // Render My Applications Table
      const appsTable = $("#my-applications-tbody");
      if (appsTable) {
        if (!data.applications.length) {
          appsTable.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:2rem; color:var(--muted)">You haven't submitted any applications yet. Browse the Service Directory to apply!</td></tr>`;
        } else {
          appsTable.innerHTML = data.applications.map(app => `
            <tr>
              <td>
                <span class="table-app-id">${escapeHtml(app.id)}</span>
              </td>
              <td>
                <b>${escapeHtml(app.service?.name || "Service")}</b>
                <div style="font-size:11px; color:var(--muted)">${escapeHtml(app.department || "")}</div>
              </td>
              <td>${formatDate(app.submitted_at)}</td>
              <td>
                <span class="status-pill status-${(app.status || "").toLowerCase().replace(/\s+/g, '-')}">
                  ${escapeHtml(app.status)}
                </span>
              </td>
              <td>
                ${app.certificate ? `
                  <a href="/api/certificates/${encodeURIComponent(app.certificate.number)}/download" class="btn btn-teal btn-sm" target="_blank">
                    Download Certificate ↗
                  </a>
                ` : `<button class="btn btn-outline btn-sm" data-quick-track="${escapeHtml(app.id)}">Track Status</button>`}
              </td>
            </tr>
          `).join("");
        }
      }

      this.renderProfile();

      // Notifications feed
      const notifFeed = $("#dash-notifications-feed");
      const notifDot = $("#header-notif-dot");
      if (notifFeed) {
        const unread = data.notifications.filter(n => !n.read).length;
        if (notifDot) notifDot.classList.toggle("hidden", unread === 0);

        if (!data.notifications.length) {
          notifFeed.innerHTML = `<p style="color:var(--muted); font-size:var(--text-xs); text-align:center">No new notifications.</p>`;
        } else {
          notifFeed.innerHTML = data.notifications.map(n => `
            <div class="notification-item">
              <div class="notif-title">${escapeHtml(n.title)}</div>
              <div class="notif-body">${escapeHtml(n.body)}</div>
              <div class="notif-time">${formatDate(n.created_at)}</div>
            </div>
          `).join("");
        }
      }

      // Check officer & admin panel displays
      const isOfficerOrAdmin = ["officer", "admin"].includes(State.user.role);
      const isAdmin = State.user.role === "admin";

      const officerPanel = $("#officer-workflow-panel");
      const adminNavTabs = $("#admin-nav-tabs");
      const adminPanels = $("#admin-panels-container");

      if (officerPanel) officerPanel.classList.toggle("hidden", !isOfficerOrAdmin);
      if (adminNavTabs) adminNavTabs.classList.toggle("hidden", !isAdmin);
      if (adminPanels) adminPanels.classList.toggle("hidden", !isAdmin);

      if (isOfficerOrAdmin) {
        await this.loadOfficerApplications();
      }

      if (isAdmin) {
        await Promise.all([
          this.loadAdminUsers(),
          this.loadAdminServices(),
          this.loadAnalytics(),
          this.loadAdminFeedback()
        ]);
      }
    } catch (err) {
      toast(err.message, "error");
    }
  },

  renderProfile() {
    const profileView = $("#dash-profile-meta");
    if (!profileView || !State.user) return;

    profileView.innerHTML = `
      <div class="profile-meta-row">
        <label>Full Name</label>
        <span>${escapeHtml(State.user.name)}</span>
      </div>
      <div class="profile-meta-row">
        <label>Email Address</label>
        <span>${escapeHtml(State.user.email)}</span>
      </div>
      <div class="profile-meta-row">
        <label>Mobile Number</label>
        <span>${escapeHtml(State.user.mobile || "Not specified")}</span>
      </div>
      <div class="profile-meta-row">
        <label>Address</label>
        <span>${escapeHtml(State.user.address || "Not specified")}</span>
      </div>
      <div class="profile-meta-row">
        <label>Role</label>
        <span><span class="badge badge-blue">${escapeHtml(State.user.role.toUpperCase())}</span></span>
      </div>
    `;

    const editForm = $("#profile-edit-form");
    if (editForm) {
      editForm.elements.name.value = State.user.name || "";
      editForm.elements.mobile.value = State.user.mobile || "";
      editForm.elements.address.value = State.user.address || "";
    }
  },

  // --- Department Officer Workflow ---

  async loadOfficerApplications() {
    const tbody = $("#officer-applications-tbody");
    if (!tbody) return;

    const q = $("#officer-search-input") ? $("#officer-search-input").value.trim() : "";
    const status = $("#officer-status-filter") ? $("#officer-status-filter").value : "";

    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (status) params.set("status", status);

    try {
      const apps = await api(`/applications?${params}`);
      if (!apps.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem; color:var(--muted)">No matching applications in queue.</td></tr>`;
        return;
      }

      tbody.innerHTML = apps.map(app => `
        <tr>
          <td><span class="table-app-id">${escapeHtml(app.id)}</span></td>
          <td>
            <b>${escapeHtml(app.applicant?.name || "Citizen")}</b>
            <div style="font-size:11px; color:var(--muted)">${escapeHtml(app.applicant?.mobile || "")}</div>
          </td>
          <td>${escapeHtml(app.service?.name || "Service")}</td>
          <td>${formatDate(app.submitted_at)}</td>
          <td>
            <span class="status-pill status-${(app.status || "").toLowerCase().replace(/\s+/g, '-')}">
              ${escapeHtml(app.status)}
            </span>
          </td>
          <td>
            <button class="btn btn-navy btn-sm" data-officer-review-btn="${escapeHtml(app.id)}" data-current-status="${escapeHtml(app.status)}" data-applicant-name="${escapeHtml(app.applicant?.name || '')}" data-service-name="${escapeHtml(app.service?.name || '')}" data-docs='${JSON.stringify(app.documents || [])}'>
              Review & Update Status ✎
            </button>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" class="error-msg">${escapeHtml(err.message)}</td></tr>`;
    }
  },

  openOfficerReviewModal(button) {
    const appId = button.dataset.officerReviewBtn;
    const currentStatus = button.dataset.currentStatus;
    const applicantName = button.dataset.applicantName;
    const serviceName = button.dataset.serviceName;
    let docs = [];
    try { docs = JSON.parse(button.dataset.docs || "[]"); } catch { }

    $("#review-modal-app-id").textContent = appId;
    $("#review-modal-applicant").textContent = applicantName;
    $("#review-modal-service").textContent = serviceName;
    $("#review-form-app-id").value = appId;

    const statusSelect = $("#review-form-status");
    if (statusSelect) statusSelect.value = currentStatus;

    const docsContainer = $("#review-modal-docs-list");
    if (docsContainer) {
      if (!docs.length) {
        docsContainer.innerHTML = `<span style="color:var(--muted); font-size:12px">No document files attached to this application.</span>`;
      } else {
        docsContainer.innerHTML = docs.map(d => `
          <a href="/api/applications/${encodeURIComponent(appId)}/documents/${encodeURIComponent(d.stored)}" class="btn btn-outline btn-sm" target="_blank" style="margin-right:6px; margin-bottom:6px">
            📥 ${escapeHtml(d.name)} (${(d.size / 1024).toFixed(1)} KB)
          </a>
        `).join("");
      }
    }

    openModal("officer-review-modal");
  },

  async handleOfficerReviewSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const appId = form.elements.application_id.value;
    const payload = {
      status: form.elements.status.value,
      remarks: form.elements.remarks.value.trim()
    };

    try {
      const res = await api(`/applications/${encodeURIComponent(appId)}/status`, {
        method: "PATCH",
        body: JSON.stringify(payload)
      });
      closeModal("officer-review-modal");
      form.reset();
      toast(res.message || "Application updated successfully!", "success");
      await this.loadOfficerApplications();
      await this.loadDashboard();
      this.loadPublicStats();
    } catch (err) {
      toast(err.message, "error");
    }
  },

  // --- Admin User Management ---

  async loadAdminUsers() {
    const tbody = $("#admin-users-tbody");
    if (!tbody) return;

    const q = $("#admin-user-search") ? $("#admin-user-search").value.trim() : "";
    const role = $("#admin-user-role-filter") ? $("#admin-user-role-filter").value : "";

    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (role) params.set("role", role);

    try {
      const users = await api(`/admin/users?${params}`);
      if (!users.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem; color:var(--muted)">No accounts found.</td></tr>`;
        return;
      }

      tbody.innerHTML = users.map(u => {
        const isSelf = u.id === State.user.id;
        return `
          <tr>
            <td><b>${escapeHtml(u.name)}</b></td>
            <td>${escapeHtml(u.email)}</td>
            <td>${escapeHtml(u.mobile || "—")}</td>
            <td>
              <select class="form-control" style="padding:4px 8px; font-size:12px; width:auto" data-user-role-select="${u.id}" ${isSelf ? "disabled" : ""}>
                <option value="citizen" ${u.role === "citizen" ? "selected" : ""}>Citizen</option>
                <option value="officer" ${u.role === "officer" ? "selected" : ""}>Officer</option>
                <option value="admin" ${u.role === "admin" ? "selected" : ""}>Administrator</option>
              </select>
            </td>
            <td>
              <span class="badge ${u.active ? 'badge-teal' : 'badge-saffron'}">
                ${u.active ? "Active" : "Disabled"}
              </span>
            </td>
            <td>
              <button class="btn btn-outline btn-sm" data-save-user-role="${u.id}" ${isSelf ? "disabled" : ""}>Save Role</button>
              <button class="btn btn-outline btn-sm" data-toggle-user-active="${u.id}" data-current-active="${u.active ? 1 : 0}" ${isSelf ? "disabled" : ""}>
                ${u.active ? "Deactivate" : "Activate"}
              </button>
            </td>
          </tr>
        `;
      }).join("");
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" class="error-msg">${escapeHtml(err.message)}</td></tr>`;
    }
  },

  async handleUserRoleSave(userId) {
    const select = $(`[data-user-role-select="${userId}"]`);
    if (!select) return;
    try {
      await api(`/admin/users/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({ role: select.value })
      });
      toast("User account role updated successfully.", "success");
      await this.loadAdminUsers();
    } catch (err) {
      toast(err.message, "error");
    }
  },

  async handleUserActiveToggle(userId, currentActive) {
    try {
      await api(`/admin/users/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({ active: currentActive === "0" })
      });
      toast(`User account ${currentActive === "0" ? "activated" : "deactivated"} successfully.`, "success");
      await this.loadAdminUsers();
    } catch (err) {
      toast(err.message, "error");
    }
  },

  // --- Admin Services Management ---

  async loadAdminServices() {
    const tbody = $("#admin-services-tbody");
    if (!tbody) return;

    try {
      const data = await api("/services?limit=100");
      tbody.innerHTML = data.items.map(svc => `
        <tr>
          <td>
            <b>${escapeHtml(svc.name)}</b>
            <div style="font-size:11px; font-family:monospace; color:var(--muted)">${escapeHtml(svc.id)}</div>
          </td>
          <td>${escapeHtml(svc.department)}</td>
          <td>${escapeHtml(svc.category)}</td>
          <td>
            <span class="badge ${svc.availability === 'Available' ? 'badge-teal' : 'badge-saffron'}">
              ${escapeHtml(svc.availability)}
            </span>
          </td>
          <td>
            <button class="btn btn-outline btn-sm" data-toggle-service-status="${escapeHtml(svc.id)}" data-current-avail="${escapeHtml(svc.availability)}">
              ${svc.availability === "Available" ? "Pause Service" : "Restore Service"}
            </button>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="5" class="error-msg">${escapeHtml(err.message)}</td></tr>`;
    }
  },

  async handleServiceStatusToggle(serviceId, currentAvail) {
    const newAvail = currentAvail === "Available" ? "Unavailable" : "Available";
    try {
      await api(`/services/${encodeURIComponent(serviceId)}`, {
        method: "PUT",
        body: JSON.stringify({ availability: newAvail })
      });
      toast(`Service availability updated to: ${newAvail}`, "success");
      await this.loadAdminServices();
      Services.loadServices(State.page);
      Services.loadCategories();
    } catch (err) {
      toast(err.message, "error");
    }
  },

  async handleAdminAddService(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    data.documents = data.documents.split(/\r?\n/).map(s => s.trim()).filter(Boolean);

    try {
      await api("/services", {
        method: "POST",
        body: JSON.stringify(data)
      });
      form.reset();
      toast("New service published to the directory!", "success");
      await this.loadAdminServices();
      Services.loadServices();
      Services.loadCategories();
    } catch (err) {
      toast(err.message, "error");
    }
  },

  // --- Admin Announcements ---

  async handleAdminAddAnnouncement(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = Object.fromEntries(new FormData(form).entries());

    try {
      await api("/announcements", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      form.reset();
      toast("Announcement published on homepage notice board!", "success");
      this.loadAnnouncements();
    } catch (err) {
      toast(err.message, "error");
    }
  },

  // --- Admin Feedback Review ---

  async loadAdminFeedback() {
    const tbody = $("#admin-feedback-tbody");
    if (!tbody) return;
    try {
      const items = await api("/admin/feedback");
      if (!items.length) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:2rem; color:var(--muted)">No citizen feedback submitted yet.</td></tr>`;
        return;
      }

      tbody.innerHTML = items.map(fb => `
        <tr>
          <td>
            <b>${escapeHtml(fb.name)}</b>
            <div style="font-size:11px; color:var(--muted)">${escapeHtml(fb.stakeholder)}</div>
          </td>
          <td>${escapeHtml(fb.portal_name)}</td>
          <td><b style="color:#D97706">${fb.rating} ★</b> (Ease: ${fb.ease_rating}, Quality: ${fb.service_rating})</td>
          <td style="max-width:300px; font-size:13px">${escapeHtml(fb.suggestions)}</td>
          <td>${formatDate(fb.created_at)}</td>
        </tr>
      `).join("");
    } catch {
      // Non-critical
    }
  },

  // --- Admin Analytics ---

  async loadAnalytics() {
    const catAnalytics = $("#analytics-categories-bars");
    const statusAnalytics = $("#analytics-status-bars");
    if (!catAnalytics || !statusAnalytics) return;

    try {
      const data = await api("/admin/analytics");

      const maxApps = Math.max(...data.categories.map(c => c.applications), 1);
      catAnalytics.innerHTML = data.categories.map(cat => {
        const pct = Math.round((cat.applications / maxApps) * 100);
        return `
          <div class="analytics-metric-row">
            <div class="analytics-bar-label">
              <span>${escapeHtml(cat.name)}</span>
              <span>${cat.applications} applications (${cat.services} services)</span>
            </div>
            <div class="analytics-bar-bg">
              <div class="analytics-bar-fill" style="width:${pct}%"></div>
            </div>
          </div>
        `;
      }).join("");

      const totalStatus = data.statuses.reduce((a, b) => a + b.count, 0) || 1;
      statusAnalytics.innerHTML = data.statuses.map(st => {
        const pct = Math.round((st.count / totalStatus) * 100);
        return `
          <div class="analytics-metric-row">
            <div class="analytics-bar-label">
              <span>${escapeHtml(st.status)}</span>
              <span>${st.count} (${pct}%)</span>
            </div>
            <div class="analytics-bar-bg">
              <div class="analytics-bar-fill" style="width:${pct}%; background:#168C83"></div>
            </div>
          </div>
        `;
      }).join("");
    } catch {
      // Non-critical
    }
  }
};

window.addEventListener("languageChanged", () => {
  if (typeof Dashboard !== "undefined") {
    Dashboard.loadPublicStats();
    Dashboard.loadAnnouncements();
    if (State.user) Dashboard.loadDashboard();
  }
});


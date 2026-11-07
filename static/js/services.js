/**
 * MP Suvidha: Service Catalogue, Categories, and Application Submission
 * Fully localized bilingual interface (English & Hindi)
 */
const Services = {
  getCategoryIcon(category) {
    if (/Education|Scholarship|शिक्षण|छात्रवृत्ति/i.test(category)) return "🎓";
    if (/Health|Welfare|स्वास्थ्य|कल्याण/i.test(category)) return "🏥";
    if (/Certificate|Document|प्रमाणपत्र|दस्तावेज़/i.test(category)) return "📜";
    if (/Employment|Skill|रोज़गार|कौशल/i.test(category)) return "💼";
    if (/Agriculture|Farmer|कृषि|किसान/i.test(category)) return "🌾";
    if (/Pension|Social|पेंशन|सामाजिक/i.test(category)) return "🛡️";
    if (/Revenue|Land|राजस्व|भू-अभिलेख/i.test(category)) return "🏛️";
    if (/Transport|परिवहन/i.test(category)) return "🚗";
    if (/Municipal|नगर निगम/i.test(category)) return "🏘️";
    if (/Business|Entrepreneurship|व्यापार|उद्योग/i.test(category)) return "🏢";
    if (/Rural|ग्रामीण/i.test(category)) return "🏡";
    return "📋";
  },

  async loadCategories() {
    const grid = $("#category-cards-grid");
    const filterSelect = $("#category-filter-select");
    const adminCategorySelect = $("#admin-service-category");

    try {
      const categories = await api("/categories");
      State.categories = categories;

      if (grid) {
        grid.innerHTML = categories.map(cat => {
          const isHi = I18N.currentLang === "hi";
          const catName = isHi && cat.name_hi ? cat.name_hi : (I18N.categories[cat.name] || cat.name);
          const catDesc = isHi && cat.description_hi ? cat.description_hi : cat.description;
          const serviceCountText = isHi
            ? `${cat.service_count} सेवाएँ उपलब्ध`
            : `${cat.service_count} ${cat.service_count === 1 ? "Service" : "Services"} Available`;

          return `
            <div class="cat-card" data-category-click="${escapeHtml(cat.name)}">
              <div class="cat-card-header">
                <div class="cat-icon-badge">${cat.icon || this.getCategoryIcon(cat.name)}</div>
                <div>
                  <div class="cat-card-title">${escapeHtml(catName)}</div>
                  <div style="font-size:11px; font-weight:700; color:var(--royal-blue); margin-top:2px">${serviceCountText}</div>
                </div>
              </div>
              <div class="cat-card-desc">${escapeHtml(catDesc)}</div>
              <div class="cat-card-footer">
                <span style="font-size:11px; color:var(--text-muted); font-weight:600">MP Digital Cluster</span>
                <span style="display:inline-flex; align-items:center; gap:0.35rem; color:var(--royal-blue); font-weight:700; font-size:12px">
                  ${isHi ? "सेवाएँ देखें" : "Explore Services"} &rarr;
                </span>
              </div>
            </div>
          `;
        }).join("");

        // Bind clicks on category cards (opens dedicated Services page pre-filtered)
        $$("[data-category-click]", grid).forEach(card => {
          card.addEventListener("click", () => {
            const catName = card.dataset.categoryClick;
            State.activeFilters.category = catName;
            if (filterSelect) filterSelect.value = catName;
            if (typeof Router !== "undefined") {
              Router.navigateTo("services", false, () => {
                Services.loadServices(1);
              });
            } else {
              this.loadServices(1);
            }
          });
        });
      }

      if (filterSelect) {
        const currentVal = filterSelect.value;
        const allOptionLabel = I18N.t("serv_filter_all_cat");
        filterSelect.innerHTML = `<option value="">${allOptionLabel}</option>` +
          categories.map(c => {
            const label = I18N.currentLang === "hi" && c.name_hi ? c.name_hi : (I18N.categories[c.name] || c.name);
            return `<option value="${escapeHtml(c.name)}">${escapeHtml(label)}</option>`;
          }).join("");
        filterSelect.value = currentVal;
      }

      if (adminCategorySelect) {
        adminCategorySelect.innerHTML = `<option value="">Choose category</option>` +
          categories.map(c => `<option value="${escapeHtml(c.name)}">${escapeHtml(c.name)}</option>`).join("");
      }
    } catch (err) {
      if (grid) grid.innerHTML = `<div class="error-msg">Failed to load service categories.</div>`;
    }
  },

  async loadDepartments() {
    const deptSelect = $("#department-filter-select");
    if (!deptSelect) return;
    try {
      const departments = await api("/departments");
      const currentVal = deptSelect.value;
      const allDeptLabel = I18N.t("serv_filter_all_dept");
      deptSelect.innerHTML = `<option value="">${allDeptLabel}</option>` +
        departments.map(d => {
          const label = I18N.translateDepartment(d);
          return `<option value="${escapeHtml(d)}">${escapeHtml(label)}</option>`;
        }).join("");
      deptSelect.value = currentVal;
    } catch {
      // Non-critical
    }
  },

  async loadServices(page = 1) {
    State.page = page;
    const grid = $("#services-directory-grid");
    const countLabel = $("#services-count-label");

    if (grid) {
      grid.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:3rem; color:var(--text-muted)">Loading services catalogue...</div>`;
    }

    const params = new URLSearchParams({
      page: String(State.page),
      limit: String(State.limit),
      sort: State.activeFilters.sort || "az"
    });

    if (State.activeFilters.q) params.set("q", State.activeFilters.q);
    if (State.activeFilters.category) params.set("category", State.activeFilters.category);
    if (State.activeFilters.department) params.set("department", State.activeFilters.department);

    try {
      const data = await api(`/services?${params}`);
      State.services = data.items;
      State.totalPages = data.pages;

      const isHi = I18N.currentLang === "hi";

      if (countLabel) {
        countLabel.textContent = isHi
          ? `${data.total} सेवाएँ उपलब्ध`
          : `Showing ${data.total} ${data.total === 1 ? "Service" : "Services"}`;
      }

      if (grid) {
        if (!data.items.length) {
          grid.innerHTML = `
            <div style="grid-column:1/-1; text-align:center; padding:3.5rem 1.5rem; background:var(--white); border-radius:var(--radius-lg); border:1px dashed var(--border)">
              <div style="font-size:2.5rem; margin-bottom:0.75rem">🔍</div>
              <h4 style="margin-bottom:0.5rem; color:var(--primary-navy)">${I18N.t("serv_no_results")}</h4>
              <p style="color:var(--text-muted); font-size:var(--text-sm)">Try clearing filters or searching for different keywords.</p>
              <button class="btn btn-outline btn-sm" id="btn-reset-filters">${I18N.t("btn_reset")}</button>
            </div>
          `;
          const resetBtn = $("#btn-reset-filters", grid);
          if (resetBtn) {
            resetBtn.addEventListener("click", () => {
              State.activeFilters = { q: "", category: "", department: "", sort: "az" };
              const qInput = $("#directory-search-input");
              const catSel = $("#category-filter-select");
              const deptSel = $("#department-filter-select");
              if (qInput) qInput.value = "";
              if (catSel) catSel.value = "";
              if (deptSel) deptSel.value = "";
              this.loadServices(1);
            });
          }
        } else {
          grid.innerHTML = data.items.map(svc => {
            const svcName = isHi && svc.name_hi ? svc.name_hi : svc.name;
            const svcDesc = isHi && svc.description_hi ? svc.description_hi : svc.description;
            const svcDept = isHi && svc.department_hi ? svc.department_hi : I18N.translateDepartment(svc.department);
            const svcCat = I18N.translateCategory(svc.category);
            const svcFee = isHi && svc.fee_hi ? svc.fee_hi : svc.fee;
            const svcTime = isHi && svc.processing_time_hi ? svc.processing_time_hi : svc.processing_time;

            return `
              <div class="service-card">
                <div>
                  <div class="service-card-top">
                    <span class="service-dept-badge">🏛️ ${escapeHtml(svcDept)}</span>
                    <span class="service-fee-badge">₹ ${escapeHtml(svcFee)}</span>
                  </div>
                  <div class="service-card-title">${escapeHtml(svcName)}</div>
                  <div class="service-card-desc">${escapeHtml(svcDesc)}</div>
                </div>

                <div>
                  <div class="service-card-meta">
                    <div>
                      <span class="meta-item-label">⏱️ ${I18N.t("serv_time_label")}</span>
                      <div class="meta-item-val">${escapeHtml(svcTime)}</div>
                    </div>
                    <div>
                      <span class="meta-item-label">📁 ${I18N.t("nav_categories")}</span>
                      <div class="meta-item-val">${escapeHtml(svcCat)}</div>
                    </div>
                  </div>

                  <div class="service-card-actions">
                    <button class="btn btn-primary btn-sm" data-apply-svc="${escapeHtml(svc.id)}">${I18N.t("btn_apply_now")} &rarr;</button>
                    <button class="btn btn-outline btn-sm" data-details-svc="${escapeHtml(svc.id)}">${I18N.t("btn_view_details")}</button>
                  </div>
                </div>
              </div>
            `;
          }).join("");

          // Bind apply & details buttons
          $$("[data-apply-svc]", grid).forEach(btn => {
            btn.addEventListener("click", () => this.openApplicationModal(btn.dataset.applySvc));
          });
          $$("[data-details-svc]", grid).forEach(btn => {
            btn.addEventListener("click", () => this.showDetailsModal(btn.dataset.detailsSvc));
          });
        }
      }

      this.renderPagination(data.total, data.pages, data.page);
    } catch (err) {
      if (grid) {
        grid.innerHTML = `<div class="error-msg" style="grid-column:1/-1">Failed to load services: ${escapeHtml(err.message)}</div>`;
      }
    }
  },

  renderPagination(total, pages, current) {
    const wrap = $("#services-pagination");
    if (!wrap) return;

    if (pages <= 1) {
      wrap.innerHTML = "";
      return;
    }

    const buttons = [];
    buttons.push(`
      <button class="page-btn" data-page-btn="${current - 1}" ${current <= 1 ? "disabled" : ""} aria-label="Previous Page">‹</button>
    `);

    for (let p = 1; p <= pages; p++) {
      buttons.push(`
        <button class="page-btn ${p === current ? "active" : ""}" data-page-btn="${p}">${p}</button>
      `);
    }

    buttons.push(`
      <button class="page-btn" data-page-btn="${current + 1}" ${current >= pages ? "disabled" : ""} aria-label="Next Page">›</button>
    `);

    wrap.innerHTML = buttons.join("");
    $$("[data-page-btn]", wrap).forEach(btn => {
      btn.addEventListener("click", () => {
        const p = parseInt(btn.dataset.pageBtn, 10);
        if (p >= 1 && p <= pages && p !== current) {
          this.loadServices(p);
          window.scrollTo({ top: 0, behavior: "instant" });
        }
      });
    });
  },

  async showDetailsModal(serviceId) {
    try {
      const svc = await api(`/services/${encodeURIComponent(serviceId)}`);
      const modalContent = $("#service-details-modal-content");
      if (!modalContent) return;

      const isHi = I18N.currentLang === "hi";
      const svcName = isHi && svc.name_hi ? svc.name_hi : svc.name;
      const svcDesc = isHi && svc.description_hi ? svc.description_hi : svc.description;
      const svcDept = isHi && svc.department_hi ? svc.department_hi : I18N.translateDepartment(svc.department);
      const svcCat = I18N.translateCategory(svc.category);
      const svcElig = isHi && svc.eligibility_hi ? svc.eligibility_hi : svc.eligibility;
      const svcFee = isHi && svc.fee_hi ? svc.fee_hi : svc.fee;
      const svcTime = isHi && svc.processing_time_hi ? svc.processing_time_hi : svc.processing_time;
      const svcDocs = isHi && svc.documents_hi && svc.documents_hi.length ? svc.documents_hi : (svc.documents || []);
      const svcInst = isHi && svc.instructions_hi ? svc.instructions_hi : svc.instructions;

      modalContent.innerHTML = `
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.75rem; flex-wrap:wrap">
          <span class="service-dept-badge">${escapeHtml(svcDept)}</span>
          <span class="badge badge-teal">${escapeHtml(svcCat)}</span>
        </div>
        <h2 style="font-size:1.5rem; color:var(--primary-navy); margin-bottom:0.75rem">${escapeHtml(svcName)}</h2>
        <p style="color:var(--text-body); font-size:var(--text-sm); line-height:1.7">${escapeHtml(svcDesc)}</p>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.25rem; margin:1.5rem 0">
          <div style="background:var(--bg-main); padding:1rem; border-radius:var(--radius-md); border:1px solid var(--border)">
            <b style="display:block; font-size:12px; color:var(--royal-blue); margin-bottom:0.35rem; text-transform:uppercase; letter-spacing:0.04em">${I18N.t("serv_eligibility_label")}</b>
            <p style="font-size:var(--text-xs); margin:0; color:var(--text-body); line-height:1.5">${escapeHtml(svcElig)}</p>
          </div>
          <div style="background:var(--bg-main); padding:1rem; border-radius:var(--radius-md); border:1px solid var(--border)">
            <b style="display:block; font-size:12px; color:var(--saffron-hover); margin-bottom:0.35rem; text-transform:uppercase; letter-spacing:0.04em">${I18N.t("serv_fee_label")} & ${I18N.t("serv_time_label")}</b>
            <p style="font-size:var(--text-xs); margin:0; color:var(--text-body); line-height:1.6">
              ${I18N.t("serv_time_label")} <b>${escapeHtml(svcTime)}</b><br>
              ${I18N.t("serv_fee_label")} <b>${escapeHtml(svcFee)}</b>
            </p>
          </div>
        </div>

        <div style="margin-bottom:1.5rem">
          <b style="display:block; font-size:13px; color:var(--primary-navy); margin-bottom:0.5rem">${I18N.t("serv_docs_label")}</b>
          <ul style="padding-left:1.25rem; margin:0; font-size:var(--text-xs); color:var(--text-body); line-height:1.7">
            ${svcDocs.map(doc => `<li>${escapeHtml(doc)}</li>`).join("")}
          </ul>
        </div>

        ${svcInst ? `
          <div style="background:var(--saffron-light); border-left:4px solid var(--saffron); padding:0.85rem 1rem; border-radius:0 var(--radius-sm) var(--radius-sm) 0; font-size:var(--text-xs); color:#78350F; margin-bottom:1.5rem">
            <b>${I18N.t("serv_instructions_label")}</b> ${escapeHtml(svcInst)}
          </div>
        ` : ""}

        <div style="display:flex; gap:0.75rem; justify-content:flex-end">
          <button class="btn btn-outline" data-modal-close="service-details-modal">${I18N.t("btn_close")}</button>
          <button class="btn btn-primary" data-apply-from-modal="${escapeHtml(svc.id)}">${I18N.t("btn_apply_now")} ↗</button>
        </div>
      `;

      const applyBtn = $("[data-apply-from-modal]", modalContent);
      if (applyBtn) {
        applyBtn.addEventListener("click", () => {
          closeModal("service-details-modal");
          this.openApplicationModal(svc.id);
        });
      }

      openModal("service-details-modal");
    } catch (err) {
      toast(err.message, "error");
    }
  },

  openApplicationModal(serviceId) {
    if (!State.user) {
      toast("Please sign in or register to submit an online service application.", "info");
      Auth.openModal("login");
      return;
    }

    const svc = State.services.find(s => s.id === serviceId);
    const form = $("#application-submission-form");
    const titleEl = $("#app-modal-service-name");
    const deptEl = $("#app-modal-service-dept");
    const docsNote = $("#app-modal-docs-note");
    const successBox = $("#application-success-box");

    if (successBox) successBox.classList.add("hidden");
    if (form) {
      form.classList.remove("hidden");
      form.reset();
      form.elements.service_id.value = serviceId;
      if (form.elements.name) form.elements.name.value = State.user.name || "";
      if (form.elements.email) form.elements.email.value = State.user.email || "";
      if (form.elements.mobile) form.elements.mobile.value = State.user.mobile || "";
      if (form.elements.address) form.elements.address.value = State.user.address || "";
    }

    const isHi = I18N.currentLang === "hi";
    const svcName = svc ? (isHi && svc.name_hi ? svc.name_hi : svc.name) : "Apply for Service";
    const svcDept = svc ? (isHi && svc.department_hi ? svc.department_hi : I18N.translateDepartment(svc.department)) : "";
    const svcTime = svc ? (isHi && svc.processing_time_hi ? svc.processing_time_hi : svc.processing_time) : "";
    const svcDocs = svc ? (isHi && svc.documents_hi && svc.documents_hi.length ? svc.documents_hi : (svc.documents || [])) : [];

    if (titleEl) titleEl.textContent = `${I18N.t("apply_modal_title")} ${svcName}`;
    if (deptEl) deptEl.textContent = svc ? `${svcDept} · ${I18N.t("serv_time_label")} ${svcTime}` : "";
    if (docsNote && svc) {
      docsNote.innerHTML = `<b>${I18N.t("serv_docs_label")}</b> ${svcDocs.join(", ") || "Aadhaar Card, Address Proof"}`;
    }

    openModal("application-submission-modal");
  },

  async handleApplicationSubmit(event) {
    event.preventDefault();
    if (!State.user) {
      toast("Please sign in to proceed.", "error");
      return;
    }

    const form = event.currentTarget;
    const submitBtn = $("#app-form-submit-btn");
    const files = [...form.elements.documents.files];

    // Check size limit: 5 MB per file
    const oversize = files.find(f => f.size > 5 * 1024 * 1024);
    if (oversize) {
      return toast(`File '${oversize.name}' exceeds the 5 MB limit.`, "error");
    }

    const payload = {
      service_id: form.elements.service_id.value,
      applicant: {
        name: form.elements.name.value,
        email: form.elements.email.value,
        mobile: form.elements.mobile.value,
        address: form.elements.address.value
      }
    };

    const formData = new FormData();
    formData.append("application", JSON.stringify(payload));
    files.forEach(f => formData.append("documents", f));

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = I18N.currentLang === "hi" ? "आवेदन जमा किया जा रहा है..." : "Uploading & Submitting Application...";
    }

    try {
      const result = await api("/applications", {
        method: "POST",
        body: formData
      });

      form.classList.add("hidden");
      const successBox = $("#application-success-box");
      if (successBox) {
        const isHi = I18N.currentLang === "hi";
        successBox.innerHTML = `
          <div style="font-size:3rem; margin-bottom:0.5rem">🎉</div>
          <h3 style="color:var(--primary-navy); margin-bottom:0.5rem">
            ${isHi ? "आवेदन सफलतापूर्वक जमा हुआ!" : "Application Submitted Successfully!"}
          </h3>
          <p style="color:var(--text-body); font-size:var(--text-sm)">
            ${isHi ? "आपका प्रदर्शन आवेदन डेटाबेस में सफलतापूर्वक दर्ज हो गया है।" : "Your demonstration application has been registered in the database."}
          </p>
          
          <div style="background:var(--teal-light); border:2px dashed var(--teal); border-radius:var(--radius-md); padding:1.25rem; margin:1.25rem 0">
            <span style="font-size:12px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em">
              ${isHi ? "आपका विशिष्ट आवेदन क्रमांक" : "Your Unique Application ID"}
            </span>
            <div style="font-family:monospace; font-size:1.75rem; font-weight:800; color:var(--teal); margin-top:4px">${escapeHtml(result.application_id)}</div>
          </div>

          <p style="font-size:var(--text-xs); color:var(--text-muted); margin-bottom:1.5rem">
            ${isHi 
              ? "कृपया इस आवेदन क्रमांक को सुरक्षित रखें। आप कभी भी ट्रैकिंग मॉड्यूल अथवा अपने नागरिक डैशबोर्ड से आवेदन स्थिति देख सकते हैं।"
              : "Keep this Application ID handy. You can track live stages anytime from the Track Application module or in your Citizen Dashboard."}
          </p>

          <div style="display:flex; gap:0.75rem; justify-content:center">
            <button class="btn btn-primary" onclick="closeModal('application-submission-modal'); window.location.hash='#dashboard-section'">
              ${isHi ? "डैशबोर्ड पर जाएँ" : "Go to My Dashboard"}
            </button>
            <button class="btn btn-outline" onclick="closeModal('application-submission-modal')">
              ${isHi ? "बंद करें" : "Close"}
            </button>
          </div>
        `;
        successBox.classList.remove("hidden");
      }

      toast(I18N.currentLang === "hi" ? "आवेदन सफलतापूर्वक जमा हुआ!" : "Application registered successfully!", "success");

      // Refresh public stats and dashboard applications
      if (typeof Dashboard !== "undefined") {
        Dashboard.loadPublicStats();
        Dashboard.loadDashboard();
      }
    } catch (err) {
      toast(err.message, "error");
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = I18N.t("btn_submit");
      }
    }
  }
};

// Re-render categories & services on language change
window.addEventListener("languageChanged", () => {
  Services.loadCategories();
  Services.loadDepartments();
  Services.loadServices(State.page || 1);
});

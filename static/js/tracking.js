/**
 * MP Suvidha: Public Application Tracking & Visual Stage Timeline
 * Fully localized bilingual interface
 */
const Tracking = {
  async handleTrackSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const resultBox = $("#tracking-result-container");
    const submitBtn = $("#track-submit-btn");

    const payload = {
      application_id: form.elements.application_id.value.trim().toUpperCase(),
      contact: form.elements.contact.value.trim().toLowerCase()
    };

    if (resultBox) {
      resultBox.classList.remove("hidden");
      resultBox.innerHTML = `<div style="text-align:center; padding:2.5rem; color:var(--text-muted)">Querying records...</div>`;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = I18N.currentLang === "hi" ? "जाँच जारी है..." : "Checking...";
    }

    try {
      const data = await api("/applications/track", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      this.renderTimeline(data);
    } catch (err) {
      if (resultBox) {
        const isHi = I18N.currentLang === "hi";
        resultBox.innerHTML = `
          <div class="tracking-timeline-box" style="border:1px solid rgba(220, 38, 38, 0.3); border-left:4px solid var(--error); background:var(--error-bg)">
            <h4 style="color:var(--error); margin-bottom:0.35rem">
              ${isHi ? "आवेदन विवरण प्राप्त नहीं हुआ" : "Unable to Locate Application"}
            </h4>
            <p style="font-size:var(--text-sm); color:var(--error); margin:0">${escapeHtml(err.message)}</p>
          </div>
        `;
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = I18N.t("track_btn_submit");
      }
    }
  },

  renderTimeline(data) {
    const resultBox = $("#tracking-result-container");
    if (!resultBox) return;

    const isHi = I18N.currentLang === "hi";
    const stages = [
      { id: "Submitted", label: I18N.t("track_stage_1"), desc: isHi ? "ऑनलाइन आवेदन प्राप्त" : "Online receipt logged" },
      { id: "Under Review", label: I18N.t("track_stage_2"), desc: isHi ? "विभागीय अधिकारी अधिकृत" : "Officer assigned" },
      { id: "Verification", label: I18N.t("track_stage_3"), desc: isHi ? "दस्तावेज़ एवं पात्रता जाँच" : "Scrutiny of attachments" },
      { 
        id: "Final", 
        label: data.status === "Rejected" ? (isHi ? "आवेदन अस्वीकृत" : "Application Rejected") : I18N.t("track_stage_4"), 
        desc: data.status === "Rejected" ? (isHi ? "कारण सहित अस्वीकृत" : "Disapproved with remarks") : (isHi ? "प्रमाणपत्र जारी" : "Certificate generated") 
      }
    ];

    let currentStepIndex = 0;
    if (data.status === "Submitted") currentStepIndex = 0;
    else if (data.status === "Under Review") currentStepIndex = 1;
    else if (data.status === "Documents Required") currentStepIndex = 2;
    else if (data.status === "Approved" || data.status === "Completed") currentStepIndex = 3;
    else if (data.status === "Rejected") currentStepIndex = 3;

    const stepsHtml = stages.map((st, idx) => {
      let stateClass = "";
      if (idx < currentStepIndex) stateClass = "completed";
      else if (idx === currentStepIndex) {
        stateClass = data.status === "Rejected" ? "rejected-step" : "current";
      }

      let icon = idx + 1;
      if (idx < currentStepIndex) icon = "✓";
      if (data.status === "Rejected" && idx === 3) icon = "✕";

      return `
        <div class="timeline-step-node ${stateClass}">
          <div class="timeline-step-circle">${icon}</div>
          <div class="timeline-step-title">${escapeHtml(st.label)}</div>
          <div class="timeline-step-desc">${escapeHtml(st.desc)}</div>
        </div>
      `;
    }).join("");

    const svcName = isHi && data.service?.name_hi ? data.service.name_hi : (data.service?.name || "Citizen Service");
    const deptName = isHi && data.service?.department_hi ? data.service.department_hi : I18N.translateDepartment(data.department || "");
    const statusLabel = I18N.translateStatus(data.status);

    resultBox.innerHTML = `
      <div class="tracking-timeline-box">
        <div class="tracking-header-row">
          <div>
            <div style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em">
              ${isHi ? "लाइव स्थिति रिपोर्ट" : "Live Status Report"}
            </div>
            <h3 style="font-size:1.35rem; color:var(--primary-navy); margin:0.25rem 0">${escapeHtml(svcName)}</h3>
            <div style="font-family:monospace; font-size:var(--text-sm); font-weight:700; color:var(--royal-blue)">
              ${isHi ? "आवेदन क्रमांक" : "Application ID"}: ${escapeHtml(data.id)}
            </div>
          </div>
          <div>
            <span class="status-pill status-${(data.status || "").toLowerCase().replace(/\s+/g, '-')}">
              ${escapeHtml(statusLabel)}
            </span>
          </div>
        </div>

        <div class="tracking-timeline-steps">
          ${stepsHtml}
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:1rem; padding:1.25rem; background:var(--bg-main); border-radius:var(--radius-md); border:1px solid var(--border)">
          <div>
            <small style="color:var(--text-muted); font-size:11px; text-transform:uppercase">${isHi ? "आवेदक का नाम" : "Applicant Name"}</small>
            <div style="font-weight:700; color:var(--text-heading)">${escapeHtml(data.applicant_name || data.applicant?.name || "Citizen")}</div>
          </div>
          <div>
            <small style="color:var(--text-muted); font-size:11px; text-transform:uppercase">${isHi ? "संबंधित विभाग" : "Department"}</small>
            <div style="font-weight:700; color:var(--text-heading)">${escapeHtml(deptName)}</div>
          </div>
          <div>
            <small style="color:var(--text-muted); font-size:11px; text-transform:uppercase">${isHi ? "जमा करने का दिनांक" : "Date Submitted"}</small>
            <div style="font-weight:700; color:var(--text-heading)">${formatDate(data.submitted_at)}</div>
          </div>
        </div>

        ${data.officer_remarks ? `
          <div style="margin-top:1.25rem; background:var(--info-bg); border:1px solid rgba(23, 105, 170, 0.2); border-left:4px solid var(--royal-blue); padding:1rem; border-radius:0 var(--radius-sm) var(--radius-sm) 0">
            <b style="display:block; font-size:var(--text-xs); color:var(--royal-blue); margin-bottom:0.25rem">${I18N.t("track_officer_remarks")}</b>
            <p style="margin:0; font-size:var(--text-sm); color:var(--text-body)">${escapeHtml(data.officer_remarks)}</p>
          </div>
        ` : ""}

        ${data.certificate ? `
          <div style="margin-top:1.25rem; display:flex; align-items:center; justify-content:space-between; background:var(--teal-light); border:1px solid rgba(22, 140, 131, 0.35); padding:1rem 1.25rem; border-radius:var(--radius-md); flex-wrap:wrap; gap:1rem">
            <div>
              <b style="color:var(--teal); font-size:var(--text-sm); display:block">
                ★ ${isHi ? "प्रदर्शन प्रमाणपत्र जारी हो चुका है!" : "Demonstration Certificate Issued!"}
              </b>
              <div style="font-size:12px; color:var(--text-body); margin-top:2px">
                ${isHi ? "प्रमाणपत्र क्रमांक" : "Certificate Number"}: 
                <span style="font-family:monospace; font-weight:700; color:var(--primary-navy)">${escapeHtml(data.certificate.number)}</span>
              </div>
            </div>
            <a href="/api/certificates/${encodeURIComponent(data.certificate.number)}/download" class="btn btn-teal btn-sm" target="_blank">
              ${I18N.t("btn_download_pdf")} ↗
            </a>
          </div>
        ` : ""}
      </div>
    `;
  }
};

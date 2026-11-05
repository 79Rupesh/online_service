/**
 * MP Suvidha: Simulated Certificate Verification & PDF Download
 * Fully localized bilingual interface
 */
const Verify = {
  async handleVerifySubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const certNumber = form.elements.certificate_number.value.trim().toUpperCase();
    const resultBox = $("#certificate-result-container");
    const submitBtn = $("#verify-submit-btn");

    if (!certNumber) {
      return toast(I18N.currentLang === "hi" ? "कृपया प्रमाणपत्र क्रमांक दर्ज करें।" : "Please enter a Certificate Number.", "error");
    }

    if (resultBox) {
      resultBox.classList.remove("hidden");
      resultBox.innerHTML = `<div style="text-align:center; padding:2.5rem; color:var(--text-muted)">Verifying certificate records...</div>`;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = I18N.currentLang === "hi" ? "सत्यापित किया जा रहा है..." : "Verifying...";
    }

    try {
      const cert = await api(`/certificates/verify/${encodeURIComponent(certNumber)}`);
      this.renderResult(cert);
      toast(I18N.currentLang === "hi" ? "मान्य प्रदर्शन प्रमाणपत्र रिकॉर्ड प्राप्त हुआ!" : "Valid demonstration certificate record found!", "success");
    } catch (err) {
      if (resultBox) {
        const isHi = I18N.currentLang === "hi";
        resultBox.innerHTML = `
          <div class="certificate-view-card" style="border:1px solid rgba(220, 38, 38, 0.3); background:var(--error-bg)">
            <h4 style="color:var(--error); margin-bottom:0.35rem">
              ${isHi ? "प्रमाणपत्र रिकॉर्ड प्राप्त नहीं हुआ" : "Certificate Record Not Found"}
            </h4>
            <p style="font-size:var(--text-sm); color:var(--error); margin-bottom:0.75rem">${escapeHtml(err.message)}</p>
            <p style="font-size:var(--text-xs); color:var(--text-muted); margin:0">
              ${isHi 
                ? "सूचना: यह टूल एमपी सुविधा पोर्टल द्वारा जारी डेमो प्रमाणपत्रों का सत्यापन करता है। उदाहरण क्रमांक: "
                : "Note: This tool verifies demonstration certificates issued on MP Suvidha. Sample certificate number: "}
              <b style="color:var(--royal-blue)">MPS-CERT-2026-09831</b>.
            </p>
          </div>
        `;
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = I18N.t("verify_btn_submit");
      }
    }
  },

  renderResult(cert) {
    const resultBox = $("#certificate-result-container");
    if (!resultBox) return;

    const isHi = I18N.currentLang === "hi";
    const statusLabel = I18N.translateStatus(cert.status);
    const deptLabel = isHi ? I18N.translateDepartment(cert.department) : cert.department;

    resultBox.innerHTML = `
      <div class="certificate-view-card">
        <div class="certificate-seal-badge">✓</div>
        
        <div style="font-size:11px; font-weight:800; color:var(--teal); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.35rem">
          ★ ${isHi ? "सत्यापित प्रदर्शन अभिलेख" : "Verified Demonstration Record"} ★
        </div>
        <h3 style="font-size:1.4rem; color:var(--primary-navy); margin-bottom:1rem">${escapeHtml(cert.service_name)}</h3>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:1rem; margin-bottom:1.5rem">
          <div>
            <small style="color:var(--text-muted); font-size:11px; text-transform:uppercase">${isHi ? "प्रमाणपत्र क्रमांक" : "Certificate Number"}</small>
            <div style="font-family:monospace; font-weight:800; font-size:15px; color:var(--royal-blue)">${escapeHtml(cert.number)}</div>
          </div>
          <div>
            <small style="color:var(--text-muted); font-size:11px; text-transform:uppercase">${isHi ? "आवेदक का नाम" : "Applicant Name"}</small>
            <div style="font-weight:700; color:var(--text-heading)">${escapeHtml(cert.applicant_name)}</div>
          </div>
          <div>
            <small style="color:var(--text-muted); font-size:11px; text-transform:uppercase">${isHi ? "जारी दिनांक" : "Issue Date"}</small>
            <div style="font-weight:700; color:var(--text-heading)">${formatDate(cert.issue_date)}</div>
          </div>
          <div>
            <small style="color:var(--text-muted); font-size:11px; text-transform:uppercase">${isHi ? "जारीकर्ता विभाग" : "Issuing Department"}</small>
            <div style="font-weight:700; color:var(--text-heading)">${escapeHtml(deptLabel)}</div>
          </div>
          <div>
            <small style="color:var(--text-muted); font-size:11px; text-transform:uppercase">${isHi ? "प्रमाणपत्र स्थिति" : "Status"}</small>
            <div><span class="status-pill status-approved">${escapeHtml(statusLabel)}</span></div>
          </div>
        </div>

        <div style="border-top:1px solid var(--border); padding-top:1.25rem; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem">
          <a href="/api/certificates/${encodeURIComponent(cert.number)}/download" class="btn btn-primary btn-sm" target="_blank">
            ${I18N.t("btn_download_pdf")} ↗
          </a>
          <span style="font-size:11px; color:var(--text-muted); max-width:360px; line-height:1.4">
            ${I18N.t("verify_demo_notice")}
          </span>
        </div>
      </div>
    `;
  }
};

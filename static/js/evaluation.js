/**
 * JanSeva Connect: College Syllabus Unit 5 - Evaluation of Local E-Governance Portals
 */
const Evaluation = {
  criteria: [
    "User Friendliness", "Navigation and Interface", "Accessibility", "Service Availability",
    "Application Process", "Application Tracking", "Information Accuracy", "Security and Privacy",
    "Mobile Responsiveness", "Overall User Experience"
  ],

  init() {
    this.renderCriteriaForm();
    this.loadEvaluations();
  },

  renderCriteriaForm() {
    const container = $("#evaluation-criteria-container");
    if (!container) return;

    container.innerHTML = this.criteria.map((crit, idx) => `
      <div class="criterion-item">
        <span class="criterion-title">${idx + 1}. ${escapeHtml(crit)}</span>
        <div class="criterion-ratings" role="group" aria-label="${escapeHtml(crit)} rating">
          ${[1, 2, 3, 4, 5].map(score => `
            <button type="button" class="crit-btn" data-criterion="${escapeHtml(crit)}" data-score="${score}" aria-label="${score} out of 5">
              ${score}
            </button>
          `).join("")}
        </div>
      </div>
    `).join("");

    const dateField = $("#eval-form-date");
    if (dateField && !dateField.value) {
      dateField.value = new Date().toISOString().slice(0, 10);
    }
  },

  handleScoreClick(button) {
    const crit = button.dataset.criterion;
    const score = Number(button.dataset.score);
    State.currentEvaluationScores[crit] = score;

    $$(`[data-criterion="${CSS.escape(crit)}"]`).forEach(btn => {
      btn.classList.toggle("selected", Number(btn.dataset.score) === score);
    });
  },

  async handleEvaluationSubmit(event) {
    event.preventDefault();
    if (!State.user) {
      toast("Please sign in to save your portal evaluation and download the structured report.", "info");
      Auth.openModal("login");
      return;
    }

    const form = event.currentTarget;
    const payload = Object.fromEntries(new FormData(form).entries());
    payload.scores = { ...State.currentEvaluationScores };

    // Check that all 10 criteria have been rated
    const unrated = this.criteria.filter(c => !payload.scores[c]);
    if (unrated.length > 0) {
      return toast(`Please rate all 10 evaluation parameters. Missing: ${unrated[0]}.`, "error");
    }

    const submitBtn = $("#eval-submit-btn");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = "Saving Evaluation & Compiling PDF...";
    }

    try {
      const result = await api("/evaluations", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      toast("Portal Evaluation saved successfully! Downloading your Unit 5 PDF report...", "success");
      form.reset();
      State.currentEvaluationScores = {};
      this.renderCriteriaForm();
      await this.loadEvaluations();

      // Trigger automatic download of the 13-point structured report
      window.open(`/api/evaluations/${encodeURIComponent(result.id)}/report.pdf`, "_blank", "noopener");
    } catch (err) {
      toast(err.message, "error");
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Save Evaluation & Download Report (PDF) →";
      }
    }
  },

  async loadEvaluations() {
    const listWrap = $("#evaluation-cards-list");
    if (!listWrap) return;

    try {
      const items = await api("/evaluations");
      State.evaluations = items;

      if (!items.length) {
        listWrap.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:2rem; color:var(--muted)">No portal evaluations recorded yet.</div>`;
        return;
      }

      listWrap.innerHTML = items.map(item => {
        const scores = Object.values(item.scores || {}).map(Number);
        const avg = scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : "—";

        return `
          <div class="saved-eval-card">
            <div class="saved-eval-head">
              <span class="badge badge-blue">${escapeHtml(item.evaluator_group || "Student Group")}</span>
              <span class="eval-score-chip">${avg} / 5</span>
            </div>
            <h4>${escapeHtml(item.portal_name)}</h4>
            <p>${escapeHtml(item.description || item.strengths || "Student evaluation study.")}</p>
            
            <div style="font-size:11px; color:var(--muted); margin-bottom:0.75rem">
              Evaluated: <b>${formatDate(item.evaluation_date)}</b> by ${escapeHtml(item.evaluator || "Student Team")}
            </div>

            <div style="border-top:1px solid var(--border); padding-top:0.75rem; display:flex; justify-content:space-between; align-items:center">
              <a href="/api/evaluations/${encodeURIComponent(item.id)}/report.pdf" class="btn btn-outline btn-sm" target="_blank">
                Download PDF ↗
              </a>
              <span style="font-size:11px; color:var(--teal); font-weight:700">Unit 5 Report Ready</span>
            </div>
          </div>
        `;
      }).join("");
    } catch (err) {
      listWrap.innerHTML = `<div style="grid-column:1/-1; color:var(--error)">Failed to load evaluations: ${escapeHtml(err.message)}</div>`;
    }
  },

  // --- Student Groups & Discussion Collaboration ---

  async loadGroups() {
    const container = $("#student-groups-container");
    if (!container) return;

    if (!State.user) {
      container.innerHTML = `<p style="color:var(--muted); font-size:var(--text-sm)">Sign in to view your research groups and tasks.</p>`;
      return;
    }

    try {
      const groups = await api("/evaluation-groups");
      State.evaluationGroups = groups;

      if (!groups.length) {
        container.innerHTML = `
          <div style="text-align:center; padding:1.5rem; background:rgba(255, 255, 255, 0.03); border-radius:var(--radius-md); border:1px dashed var(--border)">
            <p style="color:var(--text-muted); font-size:var(--text-sm); margin-bottom:0.75rem">No evaluation teams created yet.</p>
            <button class="btn btn-primary btn-sm" onclick="openModal('create-group-modal')">＋ Create New Student Group</button>
          </div>
        `;
        return;
      }

      container.innerHTML = groups.map(g => `
        <div class="group-card-item">
          <div style="display:flex; justify-content:space-between; align-items:flex-start">
            <div>
              <h4 style="margin:0; font-size:1.15rem; color:var(--text-heading)">${escapeHtml(g.name)}</h4>
              <small style="color:var(--text-muted)">Leader: <b>${escapeHtml(g.leader)}</b> · ${(g.members || []).length} Members</small>
            </div>
            <button class="btn btn-outline btn-sm" data-group-discuss="${escapeHtml(g.id)}">Team Workspace 💬</button>
          </div>

          <div class="group-progress-bar">
            <div class="group-progress-fill" style="width:${g.progress || 0}%"></div>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:11px; color:var(--muted)">
            <span>Evaluation Tasks: ${(g.tasks || []).length}</span>
            <span>Progress: <b>${g.progress || 0}%</b></span>
          </div>
        </div>
      `).join("");
    } catch (err) {
      container.innerHTML = `<div class="error-msg">Could not load groups.</div>`;
    }
  },

  async handleGroupCreate(event) {
    event.preventDefault();
    if (!State.user) {
      toast("Please sign in first.", "error");
      return;
    }

    const form = event.currentTarget;
    const rawMembers = form.elements.members.value.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
    const rawTasks = form.elements.tasks.value.split(/\r?\n/).map(s => s.trim()).filter(Boolean);

    const payload = {
      name: form.elements.name.value.trim(),
      leader: form.elements.leader.value.trim() || State.user.name,
      members: rawMembers,
      tasks: rawTasks
    };

    try {
      await api("/evaluation-groups", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      closeModal("create-group-modal");
      form.reset();
      toast("Student Evaluation Team created successfully!", "success");
      await this.loadGroups();
    } catch (err) {
      toast(err.message, "error");
    }
  },

  async openGroupWorkspace(groupId) {
    const group = State.evaluationGroups.find(g => g.id === groupId);
    if (!group) return;

    $("#workspace-group-name").textContent = group.name;
    $("#workspace-group-leader").textContent = `Leader: ${group.leader}`;
    $("#workspace-group-id").value = group.id;

    // Load discussions
    await this.loadDiscussions(groupId);
    // Load presentation notes
    await this.loadPresentationNotes(groupId);

    openModal("group-workspace-modal");
  },

  async loadDiscussions(groupId) {
    const feed = $("#workspace-discussions-feed");
    if (!feed) return;
    try {
      const messages = await api(`/evaluation-groups/${encodeURIComponent(groupId)}/discussions`);
      if (!messages.length) {
        feed.innerHTML = `<p style="color:var(--muted); font-size:12px; text-align:center; padding:1rem">No team discussion posts yet. Add observations or findings below!</p>`;
      } else {
        feed.innerHTML = messages.map(m => `
          <div class="discussion-message">
            <div class="discussion-meta">
              <b>${escapeHtml(m.user_name)} (${escapeHtml(m.topic)})</b>
              <span>${formatDate(m.created_at)}</span>
            </div>
            <p>${escapeHtml(m.message)}</p>
          </div>
        `).join("");
      }
    } catch (err) {
      feed.innerHTML = `<div class="error-msg">Could not load discussions.</div>`;
    }
  },

  async handleAddDiscussion(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const groupId = $("#workspace-group-id").value;
    const payload = {
      topic: form.elements.topic.value.trim(),
      message: form.elements.message.value.trim()
    };

    try {
      await api(`/evaluation-groups/${encodeURIComponent(groupId)}/discussions`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      form.elements.message.value = "";
      toast("Observation posted to group discussion board.", "success");
      await this.loadDiscussions(groupId);
    } catch (err) {
      toast(err.message, "error");
    }
  },

  async loadPresentationNotes(groupId) {
    const form = $("#workspace-presentation-form");
    if (!form) return;
    try {
      const pres = await api(`/evaluation-groups/${encodeURIComponent(groupId)}/presentation`);
      if (pres && pres.title) {
        form.elements.title.value = pres.title || "";
        form.elements.team_members.value = pres.team_members || "";
        form.elements.summary.value = pres.summary || "";
        form.elements.key_findings.value = pres.key_findings || "";
        form.elements.recommendations.value = pres.recommendations || "";
      } else {
        form.reset();
      }
    } catch {
      // Non-critical
    }
  },

  async handleSavePresentation(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const groupId = $("#workspace-group-id").value;
    const payload = {
      title: form.elements.title.value.trim(),
      team_members: form.elements.team_members.value.trim(),
      summary: form.elements.summary.value.trim(),
      key_findings: form.elements.key_findings.value.trim(),
      recommendations: form.elements.recommendations.value.trim()
    };

    try {
      await api(`/evaluation-groups/${encodeURIComponent(groupId)}/presentation`, {
        method: "PUT",
        body: JSON.stringify(payload)
      });
      toast("Unit 5 Presentation Notes saved successfully!", "success");
    } catch (err) {
      toast(err.message, "error");
    }
  }
};


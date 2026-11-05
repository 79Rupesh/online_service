/**
 * JanSeva Connect: Citizen and Stakeholder Feedback & Ratings Module
 */
const Feedback = {
  selectedRating: 0,

  init() {
    this.bindStars();
    this.loadSummary();
  },

  bindStars() {
    const starBox = $("#feedback-stars-box");
    if (!starBox) return;

    $$(".star-btn", starBox).forEach(btn => {
      btn.addEventListener("click", () => {
        const val = Number(btn.dataset.ratingVal);
        this.selectedRating = val;
        this.updateStarUI(val);
      });

      btn.addEventListener("mouseenter", () => {
        const val = Number(btn.dataset.ratingVal);
        this.highlightStars(val);
      });
    });

    starBox.addEventListener("mouseleave", () => {
      this.updateStarUI(this.selectedRating);
    });
  },

  highlightStars(val) {
    $$("#feedback-stars-box .star-btn").forEach(btn => {
      const btnVal = Number(btn.dataset.ratingVal);
      btn.classList.toggle("hovered", btnVal <= val);
    });
  },

  updateStarUI(val) {
    const label = $("#feedback-rating-label");
    if (label) {
      label.textContent = val > 0 ? `${val} of 5 Stars` : "Select a rating (1-5)";
    }
    $$("#feedback-stars-box .star-btn").forEach(btn => {
      const btnVal = Number(btn.dataset.ratingVal);
      btn.classList.toggle("selected", btnVal <= val);
      btn.classList.remove("hovered");
    });
  },

  async handleSubmit(event) {
    event.preventDefault();
    if (!this.selectedRating) {
      return toast("Please select an overall star rating (1 to 5).", "error");
    }

    const form = event.currentTarget;
    const payload = Object.fromEntries(new FormData(form).entries());
    payload.rating = this.selectedRating;
    payload.ease_rating = Number(payload.ease_rating || 3);
    payload.service_rating = Number(payload.service_rating || 3);

    const submitBtn = $("#feedback-submit-btn");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = "Submitting Feedback...";
    }

    try {
      await api("/feedback", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      toast("Thank you! Your feedback has been recorded.", "success");
      form.reset();
      this.selectedRating = 0;
      this.updateStarUI(0);
      await this.loadSummary();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Feedback →";
      }
    }
  },

  async loadSummary() {
    try {
      const data = await api("/feedback");
      State.feedbackSummary = data.summary;

      const avgEl = $("#feedback-avg-score");
      const totalEl = $("#feedback-total-count");
      const recentBox = $("#feedback-recent-quote");

      if (avgEl) avgEl.textContent = data.summary?.average ? `${data.summary.average} ★` : "4.8 ★";
      if (totalEl) totalEl.textContent = `${data.summary?.total || 0} reviews`;

      if (recentBox && data.items && data.items.length) {
        const top = data.items[0];
        recentBox.innerHTML = `
          <blockquote style="margin:0; border-left:3px solid var(--saffron); padding-left:1rem; font-style:italic; font-size:var(--text-sm); color:var(--text-body)">
            “${escapeHtml(top.suggestions)}”
          </blockquote>
          <div style="font-size:var(--text-xs); color:var(--text-muted); margin-top:0.5rem">
            — <b style="color:var(--text-heading)">${escapeHtml(top.name)}</b> (${escapeHtml(top.stakeholder)}) on ${escapeHtml(top.portal_name)}
          </div>
        `;
      }
    } catch {
      // Non-critical
    }
  }
};


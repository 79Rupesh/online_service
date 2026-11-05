"""Citizen and Stakeholder feedback and rating system routes."""
from flask import Blueprint, jsonify, request
from backend.auth import auth_required, error
from backend.database import connect_db, now_iso, row_dict

feedback_bp = Blueprint("feedback", __name__, url_prefix="/api")

@feedback_bp.post("/feedback")
def submit_feedback():
    data = request.get_json(silent=True) or {}
    try:
        rating = int(data.get("rating", 0))
        ease_rating = int(data.get("ease_rating", 0))
        service_rating = int(data.get("service_rating", 0))
    except (TypeError, ValueError):
        return error("Rating parameters must be integers from 1 to 5.")

    if any(r < 1 or r > 5 for r in (rating, ease_rating, service_rating)):
        return error("Please select a valid rating from 1 to 5 stars.")

    suggestions = str(data.get("suggestions", "")).strip()
    if len(suggestions) < 3:
        return error("Please provide a brief constructive feedback or suggestion.")

    name = str(data.get("name") or "Anonymous")[:100]
    stakeholder = str(data.get("stakeholder") or "Citizen")[:50]
    portal_name = str(data.get("portal_name") or "MP Suvidha")[:100]
    complaint = str(data.get("complaint", ""))[:1000]

    with connect_db() as db:
        db.execute(
            """INSERT INTO feedback
            (name, stakeholder, portal_name, rating, ease_rating, service_rating, suggestions, complaint, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, stakeholder, portal_name, rating, ease_rating, service_rating, suggestions[:2000], complaint, now_iso())
        )

    return jsonify({"message": "Thank you! Your feedback has been recorded successfully."}), 201

@feedback_bp.get("/feedback")
def feedback_summary():
    with connect_db() as db:
        summary_row = db.execute(
            """SELECT
                COUNT(*) AS total,
                ROUND(AVG(rating), 1) AS average,
                ROUND(AVG(ease_rating), 1) AS ease,
                ROUND(AVG(service_rating), 1) AS service
            FROM feedback"""
        ).fetchone()
        summary = row_dict(summary_row)

        recent_rows = db.execute(
            """SELECT id, name, stakeholder, portal_name, rating, ease_rating, service_rating, suggestions, complaint, created_at
            FROM feedback ORDER BY id DESC LIMIT 8"""
        ).fetchall()

    return jsonify({
        "summary": summary,
        "items": [row_dict(r) for r in recent_rows]
    })

@feedback_bp.get("/admin/feedback")
@auth_required("admin")
def admin_feedback_list():
    with connect_db() as db:
        rows = db.execute("SELECT * FROM feedback ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify([row_dict(r) for r in rows])


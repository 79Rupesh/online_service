"""Announcements, notices, and citizen alerts management."""
from flask import Blueprint, jsonify, request
from backend.auth import auth_required, error
from backend.database import connect_db, now_iso, row_dict

announcement_bp = Blueprint("announcements", __name__, url_prefix="/api/announcements")

@announcement_bp.get("")
def list_announcements():
    with connect_db() as db:
        rows = db.execute(
            "SELECT id, title, title_hi, body, body_hi, kind, published_at FROM announcements WHERE active=1 ORDER BY id DESC LIMIT 15"
        ).fetchall()
    return jsonify([row_dict(r) for r in rows])

@announcement_bp.post("")
@auth_required("admin")
def create_announcement():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()[:180]
    body = str(data.get("body", "")).strip()[:3000]
    kind = str(data.get("kind", "Notice")).strip()[:40]

    if len(title) < 3 or len(body) < 5:
        return error("Announcement title and detailed body text are required.")

    with connect_db() as db:
        cur = db.execute(
            "INSERT INTO announcements (title, body, kind, published_at) VALUES (?, ?, ?, ?)",
            (title, body, kind, now_iso())
        )
        row = db.execute("SELECT * FROM announcements WHERE id=?", (cur.lastrowid,)).fetchone()

    return jsonify(row_dict(row)), 201

@announcement_bp.delete("/<int:notice_id>")
@auth_required("admin")
def delete_announcement(notice_id):
    with connect_db() as db:
        cur = db.execute("UPDATE announcements SET active=0 WHERE id=?", (notice_id,))
        if cur.rowcount == 0:
            return error("Announcement not found.", 404)
    return jsonify({"message": "Announcement removed."})


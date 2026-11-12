"""Announcements, notices, and citizen alerts management."""
from flask import Blueprint, jsonify, request
from backend.auth import auth_required, error
from backend.database import connect_db, now_iso, row_dict

announcement_bp = Blueprint("announcements", __name__, url_prefix="/api/announcements")

@announcement_bp.get("")
def list_announcements():
    """Returns active announcements for the citizen view, or all if requested by an admin."""
    all_notices = request.args.get("all", "0") == "1"
    with connect_db() as db:
        if all_notices:
            rows = db.execute(
                "SELECT id, title, title_hi, body, body_hi, kind, published_at, active FROM announcements ORDER BY id DESC LIMIT 50"
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT id, title, title_hi, body, body_hi, kind, published_at, active FROM announcements WHERE active=1 ORDER BY id DESC LIMIT 15"
            ).fetchall()
    return jsonify([row_dict(r) for r in rows])

@announcement_bp.post("")
@auth_required("admin")
def create_announcement():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()[:180]
    title_hi = str(data.get("title_hi", "")).strip()[:180] or title
    body = str(data.get("body", "")).strip()[:3000]
    body_hi = str(data.get("body_hi", "")).strip()[:3000] or body
    kind = str(data.get("kind", "Notice")).strip()[:40]

    if len(title) < 3 or len(body) < 5:
        return error("Announcement title and detailed body text are required.")

    with connect_db() as db:
        cur = db.execute(
            "INSERT INTO announcements (title, title_hi, body, body_hi, kind, published_at, active) VALUES (?, ?, ?, ?, ?, ?, 1)",
            (title, title_hi, body, body_hi, kind, now_iso())
        )
        row = db.execute("SELECT * FROM announcements WHERE id=?", (cur.lastrowid,)).fetchone()

    return jsonify(row_dict(row)), 201

@announcement_bp.put("/<int:notice_id>")
@auth_required("admin")
def update_announcement(notice_id):
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()[:180]
    title_hi = str(data.get("title_hi", "")).strip()[:180]
    body = str(data.get("body", "")).strip()[:3000]
    body_hi = str(data.get("body_hi", "")).strip()[:3000]
    kind = str(data.get("kind", "")).strip()[:40]
    active = data.get("active")

    with connect_db() as db:
        existing = db.execute("SELECT * FROM announcements WHERE id=?", (notice_id,)).fetchone()
        if not existing:
            return error("Announcement not found.", 404)

        new_title = title or existing["title"]
        new_title_hi = title_hi or existing["title_hi"] or new_title
        new_body = body or existing["body"]
        new_body_hi = body_hi or existing["body_hi"] or new_body
        new_kind = kind or existing["kind"]
        new_active = int(active) if active is not None else existing["active"]

        db.execute(
            """UPDATE announcements SET
            title=?, title_hi=?, body=?, body_hi=?, kind=?, active=?
            WHERE id=?""",
            (new_title, new_title_hi, new_body, new_body_hi, new_kind, new_active, notice_id)
        )
        updated = db.execute("SELECT * FROM announcements WHERE id=?", (notice_id,)).fetchone()
    return jsonify(row_dict(updated))

@announcement_bp.delete("/<int:notice_id>")
@auth_required("admin")
def delete_announcement(notice_id):
    with connect_db() as db:
        cur = db.execute("DELETE FROM announcements WHERE id=?", (notice_id,))
        if cur.rowcount == 0:
            return error("Announcement not found.", 404)
    return jsonify({"message": "Announcement removed successfully."})

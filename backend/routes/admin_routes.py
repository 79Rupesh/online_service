"""Administrator operations, user account control, and analytics routes."""
from flask import Blueprint, g, jsonify, request
from backend.auth import auth_required, error
from backend.database import connect_db, row_dict

admin_bp = Blueprint("admin", __name__, url_prefix="/api")

@admin_bp.get("/dashboard/stats")
def public_stats():
    with connect_db() as db:
        stats = {
            "services": db.execute("SELECT COUNT(*) FROM services WHERE availability='Available'").fetchone()[0],
            "users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "applications": db.execute("SELECT COUNT(*) FROM applications").fetchone()[0],
            "approved": db.execute("SELECT COUNT(*) FROM applications WHERE status IN ('Approved', 'Completed')").fetchone()[0],
            "pending": db.execute("SELECT COUNT(*) FROM applications WHERE status IN ('Submitted', 'Under Review', 'Documents Required')").fetchone()[0],
            "rejected": db.execute("SELECT COUNT(*) FROM applications WHERE status='Rejected'").fetchone()[0],
        }
        popular = [
            row_dict(r) for r in db.execute(
                """SELECT s.id, s.name, s.name_hi, s.category, s.department, s.department_hi, COUNT(a.id) AS application_count
                FROM services s
                LEFT JOIN applications a ON a.service_id = s.id
                GROUP BY s.id
                ORDER BY application_count DESC, s.name ASC
                LIMIT 6"""
            ).fetchall()
        ]
    return jsonify({"counts": stats, "popular": popular})

@admin_bp.get("/dashboard/me")
@auth_required()
def personal_stats():
    user_id = g.user["id"]
    with connect_db() as db:
        status_counts = db.execute(
            "SELECT status, COUNT(*) AS total FROM applications WHERE citizen_id=? GROUP BY status",
            (user_id,)
        ).fetchall()

        from backend.routes.application_routes import build_application_view
        app_rows = db.execute(
            "SELECT * FROM applications WHERE citizen_id=? ORDER BY submitted_at DESC",
            (user_id,)
        ).fetchall()
        apps = [build_application_view(db, r, include_private=True) for r in app_rows]

        notif_rows = db.execute(
            "SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 10",
            (user_id,)
        ).fetchall()
        notifications = [row_dict(r) for r in notif_rows]

    counts = {"total": sum(r["total"] for r in status_counts), "pending": 0, "approved": 0, "rejected": 0}
    for r in status_counts:
        st = r["status"]
        if st in ("Submitted", "Under Review", "Documents Required"):
            counts["pending"] += r["total"]
        elif st in ("Approved", "Completed"):
            counts["approved"] += r["total"]
        elif st == "Rejected":
            counts["rejected"] += r["total"]

    return jsonify({
        "counts": counts,
        "applications": apps,
        "notifications": notifications
    })

@admin_bp.get("/admin/users")
@auth_required("admin")
def list_users():
    q = request.args.get("q", "").strip()
    role = request.args.get("role", "").strip()

    clauses = []
    params = []
    if q:
        clauses.append("(name LIKE ? OR email LIKE ? OR mobile LIKE ?)")
        params.extend([f"%{q}%"] * 3)
    if role in ("citizen", "officer", "admin"):
        clauses.append("role = ?")
        params.append(role)

    where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    with connect_db() as db:
        rows = db.execute(
            f"SELECT id, name, email, mobile, address, role, active, created_at FROM users{where_sql} ORDER BY created_at DESC LIMIT 100",
            params
        ).fetchall()
    return jsonify([row_dict(r) for r in rows])

@admin_bp.patch("/admin/users/<int:user_id>")
@auth_required("admin")
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    role = str(data.get("role", "")).strip()
    active = data.get("active")

    if role and role not in ("citizen", "officer", "admin"):
        return error("Choose a valid role: citizen, officer, or admin.")
    if active is not None and not isinstance(active, bool):
        return error("Active flag must be true or false.")

    if user_id == g.user["id"] and (role and role != "admin" or active is False):
        return error("You cannot revoke your own administrator role or deactivate your own account.")

    with connect_db() as db:
        user = db.execute("SELECT id FROM users WHERE id=?", (user_id,)).fetchone()
        if not user:
            return error("User not found.", 404)
        if role:
            db.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
        if active is not None:
            db.execute("UPDATE users SET active=? WHERE id=?", (int(active), user_id))
        updated = db.execute(
            "SELECT id, name, email, mobile, address, role, active, created_at FROM users WHERE id=?",
            (user_id,)
        ).fetchone()

    return jsonify(row_dict(updated))

@admin_bp.get("/admin/analytics")
@auth_required("admin")
def portal_analytics():
    with connect_db() as db:
        # Category breakdown
        cat_data = db.execute(
            """SELECT c.name, COUNT(s.id) AS services, COUNT(a.id) AS applications
            FROM categories c
            LEFT JOIN services s ON s.category = c.name
            LEFT JOIN applications a ON a.service_id = s.id
            GROUP BY c.name
            ORDER BY applications DESC"""
        ).fetchall()

        # Status breakdown
        status_data = db.execute(
            "SELECT status, COUNT(*) AS count FROM applications GROUP BY status"
        ).fetchall()

        # Feedback distribution
        feedback_data = db.execute(
            "SELECT rating, COUNT(*) AS count FROM feedback GROUP BY rating ORDER BY rating ASC"
        ).fetchall()

    return jsonify({
        "categories": [row_dict(r) for r in cat_data],
        "statuses": [row_dict(r) for r in status_data],
        "ratings": [row_dict(r) for r in feedback_data]
    })

@admin_bp.patch("/notifications/<int:notif_id>/read")
@auth_required()
def mark_notification_read(notif_id):
    with connect_db() as db:
        db.execute("UPDATE notifications SET read=1 WHERE id=? AND user_id=?", (notif_id, g.user["id"]))
    return jsonify({"message": "Notification marked as read."})


"""Service catalogue, category management, and service directory routes."""
import json
import uuid
import sqlite3
from flask import Blueprint, jsonify, request
from backend.auth import auth_required, error
from backend.database import connect_db, now_iso, row_dict

service_bp = Blueprint("services", __name__, url_prefix="/api")

def format_service_row(row: sqlite3.Row | None) -> dict | None:
    if not row:
        return None
    item = row_dict(row)
    try:
        item["documents"] = json.loads(item["documents"])
    except (json.JSONDecodeError, TypeError):
        item["documents"] = []
    if "documents_hi" in item and isinstance(item["documents_hi"], str):
        try:
            item["documents_hi"] = json.loads(item["documents_hi"])
        except (json.JSONDecodeError, TypeError):
            item["documents_hi"] = []
    return item

@service_bp.get("/services")
def list_services():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    department = request.args.get("department", "").strip()
    availability = request.args.get("availability", "").strip()
    app_type = request.args.get("application_type", "").strip()
    sort_by = request.args.get("sort", "az").strip()
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(100, max(1, request.args.get("limit", 12, type=int)))

    clauses = []
    params = []

    if q:
        clauses.append("(name LIKE ? OR department LIKE ? OR category LIKE ? OR description LIKE ?)")
        params.extend([f"%{q}%"] * 4)
    if category:
        clauses.append("category = ?")
        params.append(category)
    if department:
        clauses.append("department = ?")
        params.append(department)
    if availability:
        clauses.append("availability = ?")
        params.append(availability)
    if app_type:
        clauses.append("application_type = ?")
        params.append(app_type)

    where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    order_sql = " ORDER BY name DESC" if sort_by == "za" else " ORDER BY name ASC"

    with connect_db() as db:
        total = db.execute("SELECT COUNT(*) FROM services" + where_sql, params).fetchone()[0]
        offset = (page - 1) * limit
        rows = db.execute("SELECT * FROM services" + where_sql + order_sql + " LIMIT ? OFFSET ?", (*params, limit, offset)).fetchall()

    return jsonify({
        "items": [format_service_row(r) for r in rows],
        "page": page,
        "limit": limit,
        "total": total,
        "pages": max(1, (total + limit - 1) // limit)
    })

@service_bp.get("/services/<service_id>")
def get_service(service_id):
    with connect_db() as db:
        row = db.execute("SELECT * FROM services WHERE id=?", (service_id,)).fetchone()
    item = format_service_row(row)
    return (jsonify(item), 200) if item else error("Service not found.", 404)

@service_bp.get("/categories")
def list_categories():
    with connect_db() as db:
        rows = db.execute(
            """SELECT c.name, c.name_hi, c.icon, c.description, c.description_hi, COUNT(s.id) AS service_count
            FROM categories c
            LEFT JOIN services s ON s.category = c.name AND s.availability = 'Available'
            GROUP BY c.name
            ORDER BY c.name ASC"""
        ).fetchall()
    return jsonify([row_dict(r) for r in rows])

@service_bp.get("/departments")
def list_departments():
    with connect_db() as db:
        rows = db.execute("SELECT DISTINCT department FROM services ORDER BY department ASC").fetchall()
    return jsonify([r["department"] for r in rows])

def parse_service_payload(data: dict, existing=None):
    fields = {k: str(data.get(k, existing[k] if existing else "")).strip() for k in (
        "name", "department", "category", "description", "eligibility",
        "fee", "processing_time", "instructions", "availability", "application_type"
    )}
    raw_docs = data.get("documents", json.loads(existing["documents"]) if existing else [])
    if isinstance(raw_docs, str):
        raw_docs = [line.strip() for line in raw_docs.splitlines() if line.strip()]
    if not isinstance(raw_docs, list) or len(raw_docs) > 30:
        return None, "Documents must be a list with no more than 30 items."
    clean_docs = [str(d).strip()[:200] for d in raw_docs if str(d).strip()]

    if any(not fields[k] for k in ("name", "department", "category", "description")):
        return None, "Service name, department, category, and description are required."

    if fields["availability"] not in ("Available", "Unavailable"):
        fields["availability"] = "Available"
    if fields["application_type"] not in ("Online", "In-person", "Hybrid"):
        fields["application_type"] = "Online"

    fields["eligibility"] = fields["eligibility"] or "See detailed service instructions."
    fields["fee"] = fields["fee"] or "No fee"
    fields["processing_time"] = fields["processing_time"] or "Varies by department"
    fields["instructions"] = fields["instructions"] or "Review prerequisites and upload required documents."
    fields["documents"] = json.dumps(clean_docs)
    return fields, None

@service_bp.post("/services")
@auth_required("admin")
def create_service():
    data = request.get_json(silent=True) or {}
    fields, validation_err = parse_service_payload(data)
    if validation_err:
        return error(validation_err)

    service_id = str(data.get("id") or f"SVC-{uuid.uuid4().hex[:8].upper()}")[:40]
    stamp = now_iso()

    with connect_db() as db:
        if not db.execute("SELECT 1 FROM categories WHERE name=?", (fields["category"],)).fetchone():
            return error("Selected category does not exist.")
        try:
            db.execute(
                """INSERT INTO services
                (id, name, department, category, description, eligibility, documents, fee, processing_time, instructions, availability, application_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (service_id, fields["name"], fields["department"], fields["category"], fields["description"],
                 fields["eligibility"], fields["documents"], fields["fee"], fields["processing_time"],
                 fields["instructions"], fields["availability"], fields["application_type"], stamp)
            )
            created = format_service_row(db.execute("SELECT * FROM services WHERE id=?", (service_id,)).fetchone())
            return jsonify(created), 201
        except sqlite3.IntegrityError:
            return error("A service with that ID already exists.", 409)

@service_bp.put("/services/<service_id>")
@auth_required("admin")
def update_service(service_id):
    data = request.get_json(silent=True) or {}
    with connect_db() as db:
        existing = db.execute("SELECT * FROM services WHERE id=?", (service_id,)).fetchone()
        if not existing:
            return error("Service not found.", 404)

        fields, validation_err = parse_service_payload(data, existing)
        if validation_err:
            return error(validation_err)

        if not db.execute("SELECT 1 FROM categories WHERE name=?", (fields["category"],)).fetchone():
            return error("Selected category does not exist.")

        db.execute(
            """UPDATE services SET
            name=?, department=?, category=?, description=?, eligibility=?, documents=?,
            fee=?, processing_time=?, instructions=?, availability=?, application_type=?
            WHERE id=?""",
            (fields["name"], fields["department"], fields["category"], fields["description"],
             fields["eligibility"], fields["documents"], fields["fee"], fields["processing_time"],
             fields["instructions"], fields["availability"], fields["application_type"], service_id)
        )
        updated = format_service_row(db.execute("SELECT * FROM services WHERE id=?", (service_id,)).fetchone())
    return jsonify(updated)

@service_bp.delete("/services/<service_id>")
@auth_required("admin")
def delete_service(service_id):
    with connect_db() as db:
        existing = db.execute("SELECT id FROM services WHERE id=?", (service_id,)).fetchone()
        if not existing:
            return error("Service not found.", 404)
        has_apps = db.execute("SELECT COUNT(*) FROM applications WHERE service_id=?", (service_id,)).fetchone()[0]
        if has_apps:
            db.execute("UPDATE services SET availability='Unavailable' WHERE id=?", (service_id,))
            return jsonify({"message": "Service has existing applications; marked as Unavailable instead of deleting."})
        db.execute("DELETE FROM services WHERE id=?", (service_id,))
    return jsonify({"message": "Service deleted successfully."})


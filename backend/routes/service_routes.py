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

    # Comprehensive English and Hindi Search (Phase 6)
    if q:
        clauses.append(
            """(s.name LIKE ? OR s.name_hi LIKE ? OR
                s.department LIKE ? OR s.department_hi LIKE ? OR
                s.category LIKE ? OR c.name_hi LIKE ? OR
                s.description LIKE ? OR s.description_hi LIKE ?)"""
        )
        params.extend([f"%{q}%"] * 8)
    if category:
        clauses.append("(s.category = ? OR c.name_hi = ?)")
        params.extend([category, category])
    if department:
        clauses.append("(s.department = ? OR s.department_hi = ?)")
        params.extend([department, department])
    if availability:
        clauses.append("s.availability = ?")
        params.append(availability)
    if app_type:
        clauses.append("s.application_type = ?")
        params.append(app_type)

    where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    order_sql = " ORDER BY s.name DESC" if sort_by == "za" else " ORDER BY s.name ASC"

    with connect_db() as db:
        count_query = "SELECT COUNT(DISTINCT s.id) FROM services s LEFT JOIN categories c ON c.name = s.category" + where_sql
        total = db.execute(count_query, params).fetchone()[0]
        offset = (page - 1) * limit
        rows_query = "SELECT s.* FROM services s LEFT JOIN categories c ON c.name = s.category" + where_sql + order_sql + " LIMIT ? OFFSET ?"
        rows = db.execute(rows_query, (*params, limit, offset)).fetchall()

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
        "name", "name_hi", "department", "department_hi", "category", "description", "description_hi",
        "eligibility", "eligibility_hi", "fee", "fee_hi", "processing_time", "processing_time_hi",
        "instructions", "instructions_hi", "availability", "application_type"
    )}
    raw_docs = data.get("documents", json.loads(existing["documents"]) if existing else [])
    if isinstance(raw_docs, str):
        raw_docs = [line.strip() for line in raw_docs.splitlines() if line.strip()]
    if not isinstance(raw_docs, list) or len(raw_docs) > 30:
        return None, "Documents must be a list with no more than 30 items."
    clean_docs = [str(d).strip()[:200] for d in raw_docs if str(d).strip()]

    raw_docs_hi = data.get("documents_hi", json.loads(existing["documents_hi"]) if (existing and "documents_hi" in existing and existing["documents_hi"]) else [])
    if isinstance(raw_docs_hi, str):
        raw_docs_hi = [line.strip() for line in raw_docs_hi.splitlines() if line.strip()]
    clean_docs_hi = [str(d).strip()[:200] for d in raw_docs_hi if str(d).strip()] if isinstance(raw_docs_hi, list) else []

    if any(not fields[k] for k in ("name", "department", "category", "description")):
        return None, "English service name, department, category, and description are required."

    # Validate Hindi fields if adding or updating (Phase 6 requirement: Never save incomplete Hindi data silently)
    if not fields["name_hi"]:
        fields["name_hi"] = fields["name"]
    if not fields["department_hi"]:
        fields["department_hi"] = fields["department"]
    if not fields["description_hi"]:
        fields["description_hi"] = fields["description"]
    if not fields["eligibility_hi"]:
        fields["eligibility_hi"] = fields["eligibility"]
    if not fields["fee_hi"]:
        fields["fee_hi"] = fields["fee"]
    if not fields["processing_time_hi"]:
        fields["processing_time_hi"] = fields["processing_time"]
    if not fields["instructions_hi"]:
        fields["instructions_hi"] = fields["instructions"]

    if fields["availability"] not in ("Available", "Unavailable"):
        fields["availability"] = "Available"
    if fields["application_type"] not in ("Online", "In-person", "Hybrid"):
        fields["application_type"] = "Online"

    fields["eligibility"] = fields["eligibility"] or "See detailed service instructions."
    fields["fee"] = fields["fee"] or "Free"
    fields["processing_time"] = fields["processing_time"] or "Varies by department"
    fields["instructions"] = fields["instructions"] or "Review prerequisites and upload required documents."
    fields["documents"] = json.dumps(clean_docs)
    fields["documents_hi"] = json.dumps(clean_docs_hi or clean_docs)
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
                (id, name, name_hi, department, department_hi, category, description, description_hi,
                 eligibility, eligibility_hi, documents, documents_hi, fee, fee_hi,
                 processing_time, processing_time_hi, instructions, instructions_hi,
                 availability, application_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (service_id, fields["name"], fields["name_hi"], fields["department"], fields["department_hi"],
                 fields["category"], fields["description"], fields["description_hi"],
                 fields["eligibility"], fields["eligibility_hi"], fields["documents"], fields["documents_hi"],
                 fields["fee"], fields["fee_hi"], fields["processing_time"], fields["processing_time_hi"],
                 fields["instructions"], fields["instructions_hi"], fields["availability"], fields["application_type"], stamp)
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
            name=?, name_hi=?, department=?, department_hi=?, category=?, description=?, description_hi=?,
            eligibility=?, eligibility_hi=?, documents=?, documents_hi=?, fee=?, fee_hi=?,
            processing_time=?, processing_time_hi=?, instructions=?, instructions_hi=?,
            availability=?, application_type=?
            WHERE id=?""",
            (fields["name"], fields["name_hi"], fields["department"], fields["department_hi"],
             fields["category"], fields["description"], fields["description_hi"],
             fields["eligibility"], fields["eligibility_hi"], fields["documents"], fields["documents_hi"],
             fields["fee"], fields["fee_hi"], fields["processing_time"], fields["processing_time_hi"],
             fields["instructions"], fields["instructions_hi"], fields["availability"], fields["application_type"], service_id)
        )
        updated = format_service_row(db.execute("SELECT * FROM services WHERE id=?", (service_id,)).fetchone())
    return jsonify(updated)

@service_bp.patch("/services/<service_id>/status")
@auth_required("admin")
def toggle_service_status(service_id):
    data = request.get_json(silent=True) or {}
    status = str(data.get("availability", "")).strip()
    if status not in ("Available", "Unavailable"):
        return error("Status must be 'Available' or 'Unavailable'.")
    with connect_db() as db:
        existing = db.execute("SELECT id FROM services WHERE id=?", (service_id,)).fetchone()
        if not existing:
            return error("Service not found.", 404)
        db.execute("UPDATE services SET availability=? WHERE id=?", (status, service_id))
    return jsonify({"message": f"Service availability updated to {status}.", "availability": status})

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

# --- Category Management (Phase 8) ---

@service_bp.post("/categories")
@auth_required("admin")
def create_category():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    name_hi = str(data.get("name_hi", "")).strip()
    icon = str(data.get("icon", "📁")).strip() or "📁"
    description = str(data.get("description", "")).strip()
    description_hi = str(data.get("description_hi", "")).strip()

    if not name or len(name) < 2:
        return error("Category name in English is required.")

    with connect_db() as db:
        try:
            db.execute(
                """INSERT INTO categories (name, name_hi, icon, description, description_hi)
                VALUES (?, ?, ?, ?, ?)""",
                (name, name_hi or name, icon, description, description_hi or description)
            )
            created = db.execute("SELECT * FROM categories WHERE name=?", (name,)).fetchone()
            return jsonify(row_dict(created)), 201
        except sqlite3.IntegrityError:
            return error("A category with that name already exists.", 409)

@service_bp.put("/categories/<cat_name>")
@auth_required("admin")
def update_category(cat_name):
    data = request.get_json(silent=True) or {}
    name_hi = str(data.get("name_hi", "")).strip()
    icon = str(data.get("icon", "📁")).strip()
    description = str(data.get("description", "")).strip()
    description_hi = str(data.get("description_hi", "")).strip()

    with connect_db() as db:
        existing = db.execute("SELECT * FROM categories WHERE name=?", (cat_name,)).fetchone()
        if not existing:
            return error("Category not found.", 404)
        db.execute(
            """UPDATE categories SET
            name_hi=?, icon=?, description=?, description_hi=?
            WHERE name=?""",
            (name_hi or existing["name_hi"], icon or existing["icon"],
             description or existing["description"], description_hi or existing["description_hi"],
             cat_name)
        )
        updated = db.execute("SELECT * FROM categories WHERE name=?", (cat_name,)).fetchone()
    return jsonify(row_dict(updated))

@service_bp.delete("/categories/<cat_name>")
@auth_required("admin")
def delete_category(cat_name):
    with connect_db() as db:
        existing = db.execute("SELECT name FROM categories WHERE name=?", (cat_name,)).fetchone()
        if not existing:
            return error("Category not found.", 404)
        
        # Check if services use this category (Phase 8 Requirement: Prevent deletion of categories currently used by services)
        in_use_count = db.execute("SELECT COUNT(*) FROM services WHERE category=?", (cat_name,)).fetchone()[0]
        if in_use_count > 0:
            return error(f"Cannot delete category '{cat_name}' because it is assigned to {in_use_count} active services. Please reassign those services before deleting.", 400)

        db.execute("DELETE FROM categories WHERE name=?", (cat_name,))
    return jsonify({"message": f"Category '{cat_name}' deleted successfully."})


"""Online application lifecycle, tracking timeline, and document handling."""
import json
import secrets
import uuid
from datetime import datetime
from flask import Blueprint, g, jsonify, request, send_file
from werkzeug.utils import secure_filename
from backend.auth import auth_required, error
from backend.config import Config
from backend.database import connect_db, now_iso, row_dict

application_bp = Blueprint("applications", __name__, url_prefix="/api/applications")

def build_application_view(db, row, include_private: bool = False) -> dict:
    item = row_dict(row)
    try:
        item["applicant"] = json.loads(item["applicant"])
    except (json.JSONDecodeError, TypeError):
        item["applicant"] = {}
    try:
        item["documents"] = json.loads(item["documents"])
    except (json.JSONDecodeError, TypeError):
        item["documents"] = []

    svc = db.execute("SELECT id, name, category, department FROM services WHERE id=?", (item["service_id"],)).fetchone()
    item["service"] = row_dict(svc) if svc else {"id": item["service_id"], "name": "Service", "category": "", "department": item.get("department", "")}

    cert = db.execute("SELECT number, issue_date FROM certificates WHERE application_id=?", (item["id"],)).fetchone()
    item["certificate"] = row_dict(cert) if cert else None

    history_rows = db.execute("SELECT status, remarks, created_at FROM application_history WHERE application_id=? ORDER BY id ASC", (item["id"],)).fetchall()
    item["history"] = [row_dict(h) for h in history_rows]

    if not include_private:
        item.pop("citizen_id", None)
        item.pop("documents", None)
        applicant_name = item.get("applicant", {}).get("name", "")
        item["applicant"] = {"name": applicant_name}
    return item

@application_bp.post("")
@auth_required("citizen", "admin", "officer")
def submit_application():
    if request.content_type and request.content_type.startswith("multipart/form-data"):
        raw_app = request.form.get("application", "{}")
        try:
            data = json.loads(raw_app)
        except json.JSONDecodeError:
            return error("Invalid application payload JSON.")
        uploaded_files = request.files.getlist("documents")
    else:
        data = request.get_json(silent=True) or {}
        uploaded_files = []

    service_id = str(data.get("service_id", "")).strip()
    applicant = data.get("applicant") if isinstance(data.get("applicant"), dict) else {}

    with connect_db() as db:
        service = db.execute("SELECT * FROM services WHERE id=? AND availability='Available'", (service_id,)).fetchone()
    if not service:
        return error("The selected service is currently not available for applications.")

    name = str(applicant.get("name", "")).strip()
    email = str(applicant.get("email", "")).strip().lower()
    mobile = str(applicant.get("mobile", "")).strip()
    address = str(applicant.get("address", "")).strip()

    if len(name) < 2 or not email or not mobile:
        return error("Applicant full name, email address, and mobile number are required.")

    if g.user["role"] == "citizen" and email != g.user["email"].lower():
        return error("Please use the email address associated with your logged-in account.")

    saved_documents = []
    for file in uploaded_files:
        filename = secure_filename(file.filename or "")
        if not filename:
            continue
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in Config.ALLOWED_EXTENSIONS:
            return error(f"Invalid file format for '{filename}'. Allowed formats: PDF, JPG, PNG.")
        raw_bytes = file.stream.read(Config.MAX_FILE_BYTES + 1)
        if len(raw_bytes) > Config.MAX_FILE_BYTES:
            return error(f"File '{filename}' exceeds maximum allowed size of 5 MB.")
        if not raw_bytes:
            continue
        stored_name = f"{uuid.uuid4().hex}.{ext}"
        (Config.UPLOAD_DIR / stored_name).write_bytes(raw_bytes)
        saved_documents.append({
            "name": filename,
            "stored": stored_name,
            "size": len(raw_bytes),
            "type": ext
        })

    app_id = f"MPS-{datetime.now().year}-{secrets.randbelow(900000) + 100000}"
    stamp = now_iso()
    clean_applicant = {
        "name": name,
        "email": email,
        "mobile": mobile,
        "address": address[:300]
    }

    with connect_db() as db:
        db.execute(
            """INSERT INTO applications
            (id, citizen_id, service_id, applicant, documents, submitted_at, status, department, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Submitted', ?, ?)""",
            (app_id, g.user["id"], service_id, json.dumps(clean_applicant), json.dumps(saved_documents),
             stamp, service["department"], stamp)
        )
        db.execute(
            "INSERT INTO application_history (application_id, status, remarks, created_at) VALUES (?, 'Submitted', 'Application submitted successfully.', ?)",
            (app_id, stamp)
        )
        db.execute(
            "INSERT INTO notifications (user_id, title, body, created_at) VALUES (?, ?, ?, ?)",
            (g.user["id"], "Application Submitted", f"Your application {app_id} for {service['name']} has been submitted.", stamp)
        )

    return jsonify({
        "application_id": app_id,
        "status": "Submitted",
        "message": f"Your application for {service['name']} has been submitted successfully."
    }), 201

@application_bp.get("/my")
@auth_required()
def my_applications():
    with connect_db() as db:
        if g.user["role"] == "citizen":
            rows = db.execute("SELECT * FROM applications WHERE citizen_id=? ORDER BY submitted_at DESC", (g.user["id"],)).fetchall()
        else:
            rows = db.execute("SELECT * FROM applications ORDER BY submitted_at DESC LIMIT 100").fetchall()
        return jsonify([build_application_view(db, r, include_private=True) for r in rows])

@application_bp.post("/track")
def track_application():
    data = request.get_json(silent=True) or {}
    app_id = str(data.get("application_id", "")).strip().upper()
    contact = str(data.get("contact", "")).strip().lower()

    if not app_id or not contact:
        return error("Application ID and registered email or mobile number are required.")

    with connect_db() as db:
        row = db.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
        if not row:
            return error("No application found with the provided details. Please verify your Application ID and contact information.", 404)

        try:
            applicant_info = json.loads(row["applicant"])
        except (json.JSONDecodeError, TypeError):
            applicant_info = {}

        registered_email = str(applicant_info.get("email", "")).strip().lower()
        registered_mobile = str(applicant_info.get("mobile", "")).strip().lower()

        if contact not in (registered_email, registered_mobile):
            return error("Application ID and contact details do not match our demonstration records.", 404)

        item = build_application_view(db, row, include_private=False)
        item["applicant_name"] = applicant_info.get("name", "Applicant")
        item["submitted_at"] = row["submitted_at"]
        return jsonify(item)

@application_bp.get("")
@auth_required("admin", "officer")
def admin_applications_list():
    status = request.args.get("status", "").strip()
    q = request.args.get("q", "").strip()

    clauses = []
    params = []
    if status:
        clauses.append("status = ?")
        params.append(status)
    if q:
        clauses.append("(id LIKE ? OR department LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])

    where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    with connect_db() as db:
        rows = db.execute(f"SELECT * FROM applications{where_sql} ORDER BY submitted_at DESC LIMIT 100", params).fetchall()
        return jsonify([build_application_view(db, r, include_private=True) for r in rows])

@application_bp.patch("/<app_id>/status")
@auth_required("admin", "officer")
def update_application_status(app_id):
    data = request.get_json(silent=True) or {}
    new_status = str(data.get("status", "")).strip()
    remarks = str(data.get("remarks", "")).strip()[:1000]

    valid_statuses = {"Submitted", "Under Review", "Documents Required", "Approved", "Rejected", "Completed"}
    if new_status not in valid_statuses:
        return error("Select a valid application status.")

    stamp = now_iso()
    with connect_db() as db:
        row = db.execute(
            """SELECT a.*, s.name AS service_name
            FROM applications a
            JOIN services s ON s.id = a.service_id
            WHERE a.id=?""",
            (app_id,)
        ).fetchone()

        if not row:
            return error("Application not found.", 404)

        db.execute(
            "UPDATE applications SET status=?, officer_remarks=?, updated_at=? WHERE id=?",
            (new_status, remarks, stamp, app_id)
        )
        db.execute(
            "INSERT INTO application_history (application_id, status, remarks, created_at) VALUES (?, ?, ?, ?)",
            (app_id, new_status, remarks, stamp)
        )
        db.execute(
            "INSERT INTO notifications (user_id, title, body, created_at) VALUES (?, ?, ?, ?)",
            (row["citizen_id"], f"Application {new_status}", remarks or f"Status of your {row['service_name']} application was updated to '{new_status}'.", stamp)
        )

        cert_number = None
        if new_status == "Approved":
            existing_cert = db.execute("SELECT number FROM certificates WHERE application_id=?", (app_id,)).fetchone()
            if not existing_cert:
                cert_number = f"MPS-CERT-{datetime.now().year}-{secrets.randbelow(90000) + 10000}"
                try:
                    applicant_obj = json.loads(row["applicant"])
                    applicant_name = applicant_obj.get("name", "Applicant")
                except Exception:
                    applicant_name = "Applicant"

                db.execute(
                    """INSERT OR IGNORE INTO certificates
                    (number, application_id, applicant_name, service_name, issue_date, department, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Valid')""",
                    (cert_number, app_id, applicant_name, row["service_name"], stamp[:10], row["department"])
                )

    return jsonify({
        "message": f"Application status updated to '{new_status}'.",
        "status": new_status,
        "certificate_number": cert_number
    })

@application_bp.get("/<app_id>/documents/<stored_name>")
@auth_required("admin", "officer", "citizen")
def download_document(app_id, stored_name):
    with connect_db() as db:
        row = db.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
        if not row:
            return error("Application not found.", 404)
        if g.user["role"] == "citizen" and row["citizen_id"] != g.user["id"]:
            return error("You are not authorized to download this document.", 403)

        try:
            documents = json.loads(row["documents"])
        except Exception:
            documents = []

        found = next((d for d in documents if d.get("stored") == stored_name), None)
        if not found:
            return error("Document record not found.", 404)

        file_path = Config.UPLOAD_DIR / stored_name
        if not file_path.is_file():
            return error("Document file is missing from local storage.", 404)

        return send_file(file_path, as_attachment=True, download_name=found.get("name", "document"), conditional=True)


"""Certificate verification and PDF download routes for MP Suvidha."""
from io import BytesIO
from flask import Blueprint, jsonify, request, send_file
from backend.auth import error
from backend.database import connect_db, row_dict
from backend.pdf_service import build_certificate_pdf

certificate_bp = Blueprint("certificates", __name__, url_prefix="/api/certificates")

def mask_name(raw_name: str) -> str:
    """Protects citizen privacy by masking personal names: 'Aarav Sharma' -> 'A•••• S••••'."""
    parts = (raw_name or "").split()
    return " ".join([p[0] + "••••" if len(p) > 1 else p for p in parts]) or "Applicant"

@certificate_bp.get("/verify/<number>")
def verify_certificate_get(number):
    clean_num = number.strip().upper()
    with connect_db() as db:
        row = db.execute("SELECT * FROM certificates WHERE number=?", (clean_num,)).fetchone()

    if not row:
        return error("Certificate record not found. Please verify the Certificate Number.", 404)

    item = row_dict(row)
    raw_name = item.pop("applicant_name", "Applicant")
    item["applicant_name"] = mask_name(raw_name)
    item["is_demo"] = True
    item["valid"] = item.get("status", "").lower() == "valid"
    item["disclaimer"] = "This is an independent demonstration certificate issued by MP Suvidha and is not affiliated with the official Government of Madhya Pradesh."
    return jsonify(item)

@certificate_bp.post("/verify")
def verify_certificate_post():
    data = request.get_json(silent=True) or {}
    cert_num = str(data.get("certificate_number") or data.get("number") or "").strip().upper()
    app_id = str(data.get("application_id") or "").strip().upper()

    if not cert_num and not app_id:
        return error("Please provide a valid Certificate Number or Application ID.")

    with connect_db() as db:
        if cert_num:
            row = db.execute("SELECT * FROM certificates WHERE number=?", (cert_num,)).fetchone()
        else:
            row = db.execute("SELECT * FROM certificates WHERE application_id=?", (app_id,)).fetchone()

    if not row:
        return error("No matching certificate record was found. Please check your reference details.", 404)

    item = row_dict(row)
    raw_name = item.pop("applicant_name", "Applicant")
    item["applicant_name"] = mask_name(raw_name)
    item["is_demo"] = True
    item["valid"] = item.get("status", "").lower() == "valid"
    item["disclaimer"] = "This is an independent demonstration certificate issued by MP Suvidha and is not affiliated with the official Government of Madhya Pradesh."
    return jsonify(item)

@certificate_bp.get("/<number>/download")
def download_certificate(number):
    clean_num = number.strip().upper()
    with connect_db() as db:
        row = db.execute("SELECT * FROM certificates WHERE number=?", (clean_num,)).fetchone()

    if not row:
        return error("Certificate not found.", 404)

    cert_data = row_dict(row)
    pdf_bytes = build_certificate_pdf(cert_data)
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{clean_num}-demo-certificate.pdf"
    )

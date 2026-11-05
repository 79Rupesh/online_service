"""Simulated Certificate verification and PDF download routes."""
from io import BytesIO
from flask import Blueprint, jsonify, send_file
from backend.auth import error
from backend.database import connect_db, row_dict
from backend.pdf_service import build_certificate_pdf

certificate_bp = Blueprint("certificates", __name__, url_prefix="/api/certificates")

@certificate_bp.get("/verify/<number>")
def verify_certificate(number):
    clean_num = number.strip().upper()
    with connect_db() as db:
        row = db.execute("SELECT * FROM certificates WHERE number=?", (clean_num,)).fetchone()

    if not row:
        return error("Certificate record not found in this demonstration portal. Please check the Certificate Number.", 404)

    item = row_dict(row)
    # Mask applicant name for privacy: "Aarav Demo" -> "A•••• D••••"
    raw_name = item.pop("applicant_name", "Applicant")
    name_parts = raw_name.split()
    masked = " ".join([p[0] + "••••" if len(p) > 1 else p for p in name_parts])
    item["applicant_name"] = masked
    item["is_demo"] = True
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


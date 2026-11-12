"""MP Suvidha: Comprehensive Automated Audit & Test Suite.
Validates security, role permissions, department boundaries, bilingual search,
accurate statistics, certificate generation & QR verification, and privacy protections.
"""
import io
import json
import os
import pytest
from app import app
from backend.database import connect_db, init_db

@pytest.fixture(scope="module")
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def get_auth_token(client, email, password):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Login failed for {email}: {resp.json}"
    return resp.json["token"]

# ==============================================================================
# 1. AUTHENTICATION & SECURITY TESTS
# ==============================================================================

def test_login_success(client):
    resp = client.post("/api/auth/login", json={
        "email": "citizen@mpsuvidha.demo",
        "password": "Citizen@123"
    })
    assert resp.status_code == 200
    data = resp.json
    assert "token" in data
    assert data["user"]["email"] == "citizen@mpsuvidha.demo"
    assert data["user"]["role"] == "citizen"

def test_login_invalid_password(client):
    resp = client.post("/api/auth/login", json={
        "email": "citizen@mpsuvidha.demo",
        "password": "WrongPassword!999"
    })
    assert resp.status_code == 401
    assert "incorrect" in resp.json["error"].lower()

def test_registration_validation(client):
    resp = client.post("/api/auth/register", json={
        "name": "T",
        "email": "invalid-email",
        "mobile": "123",
        "password": "short"
    })
    assert resp.status_code == 400

# ==============================================================================
# 2. OFFICER DEPARTMENT PERMISSIONS & AUTHORIZATION BOUNDARIES (PHASE 4)
# ==============================================================================

def test_officer_revenue_department_isolation(client):
    """Officer A (Revenue) must ONLY see Revenue Department applications."""
    rev_token = get_auth_token(client, "officer@mpsuvidha.demo", "Officer@123")
    headers = {"Authorization": f"Bearer {rev_token}"}

    resp = client.get("/api/applications", headers=headers)
    assert resp.status_code == 200
    apps = resp.json
    assert len(apps) > 0
    for app_item in apps:
        assert app_item["department"] == "Revenue Department", f"Data leak! Revenue officer saw {app_item['department']}"

def test_officer_municipal_department_isolation(client):
    """Officer B (Municipal) must ONLY see Municipal Services applications."""
    mun_token = get_auth_token(client, "officer_municipal@mpsuvidha.demo", "Officer@123")
    headers = {"Authorization": f"Bearer {mun_token}"}

    resp = client.get("/api/applications", headers=headers)
    assert resp.status_code == 200
    apps = resp.json
    assert len(apps) > 0
    for app_item in apps:
        assert app_item["department"] == "Municipal Services", f"Data leak! Municipal officer saw {app_item['department']}"

def test_officer_cannot_update_cross_department_application(client):
    """Officer A (Revenue) CANNOT update applications belonging to Municipal Services."""
    rev_token = get_auth_token(client, "officer@mpsuvidha.demo", "Officer@123")
    headers = {"Authorization": f"Bearer {rev_token}"}

    # MPS-2026-10550 belongs to Municipal Services
    resp = client.patch("/api/applications/MPS-2026-10550/status", headers=headers, json={
        "status": "Under Review",
        "remarks": "Illegal cross-department attempt"
    })
    assert resp.status_code == 403, "Security vulnerability! Revenue officer was able to update Municipal application!"
    assert "access denied" in resp.json["error"].lower()

def test_officer_cannot_access_admin_user_management(client):
    """Officers cannot access admin user management APIs."""
    rev_token = get_auth_token(client, "officer@mpsuvidha.demo", "Officer@123")
    headers = {"Authorization": f"Bearer {rev_token}"}

    resp = client.get("/api/admin/users", headers=headers)
    assert resp.status_code == 403

def test_citizen_cannot_download_other_citizen_documents(client):
    """Citizens cannot access or download documents of other citizens."""
    cit_token = get_auth_token(client, "citizen@mpsuvidha.demo", "Citizen@123")
    headers = {"Authorization": f"Bearer {cit_token}"}

    # User 37 is a different citizen
    resp = client.get("/api/applications/MPS-2026-10482/documents/non_existent.pdf", headers=headers)
    # The application belongs to citizen_id 1 (Aarav Sharma), so Aarav can access (resulting in 404 for missing file, not 403)
    # If a different citizen tries:
    token_user37 = client.post("/api/auth/register", json={
        "name": "Other Citizen",
        "email": "other.citizen@mpsuvidha.demo",
        "mobile": "9876543210",
        "password": "OtherCitizen@123",
        "address": "Indore, MP"
    })
    if token_user37.status_code == 201:
        u37_token = token_user37.json["token"]
    else:
        u37_token = get_auth_token(client, "other.citizen@mpsuvidha.demo", "OtherCitizen@123")

    resp2 = client.get("/api/applications/MPS-2026-10482/documents/any_file.pdf", headers={"Authorization": f"Bearer {u37_token}"})
    assert resp2.status_code == 403, "Security vulnerability! Unauthorized citizen could access someone else's document!"

# ==============================================================================
# 3. ACCURATE WEBSITE STATISTICS & ANALYTICS (PHASE 7)
# ==============================================================================

def test_public_statistics_excludes_admins_and_officers(client):
    """Registered Citizens MUST count only active citizens, excluding admins and officers."""
    resp = client.get("/api/dashboard/stats")
    assert resp.status_code == 200
    counts = resp.json["counts"]

    with connect_db() as db:
        actual_citizens = db.execute("SELECT COUNT(*) FROM users WHERE role='citizen' AND active=1").fetchone()[0]
        actual_total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    assert counts["users"] == actual_citizens, f"Expected {actual_citizens} citizens, got {counts['users']}"
    assert counts["users"] < actual_total_users, "Bug: Registered citizens count includes admin or officer accounts!"
    assert counts["services"] >= 12
    assert counts["applications"] >= 4

# ==============================================================================
# 4. BILINGUAL ENGLISH & HINDI SEARCH (PHASE 6)
# ==============================================================================

def test_bilingual_service_search_english(client):
    resp = client.get("/api/services?q=Income")
    assert resp.status_code == 200
    items = resp.json["items"]
    assert any("Income Certificate" in item["name"] for item in items)

def test_bilingual_service_search_hindi(client):
    resp = client.get("/api/services?q=आय प्रमाण पत्र")
    assert resp.status_code == 200
    items = resp.json["items"]
    assert any(item["id"] == "SVC-001" for item in items)

def test_bilingual_service_search_hindi_department(client):
    resp = client.get("/api/services?q=राजस्व विभाग")
    assert resp.status_code == 200
    items = resp.json["items"]
    assert len(items) > 0
    assert any(item["department"] == "Revenue Department" for item in items)

# ==============================================================================
# 5. SERVICE MANAGEMENT & CATEGORY SAFE DELETION (PHASE 8)
# ==============================================================================

def test_admin_category_safe_deletion(client):
    """Deleting a category currently assigned to services must be rejected."""
    adm_token = get_auth_token(client, "admin@mpsuvidha.demo", "Admin@123")
    headers = {"Authorization": f"Bearer {adm_token}"}

    resp = client.delete("/api/categories/Revenue and Land Records", headers=headers)
    assert resp.status_code == 400
    assert "assigned to" in resp.json["error"].lower()

def test_service_status_toggle(client):
    adm_token = get_auth_token(client, "admin@mpsuvidha.demo", "Admin@123")
    headers = {"Authorization": f"Bearer {adm_token}"}

    resp = client.patch("/api/services/SVC-001/status", headers=headers, json={"availability": "Unavailable"})
    assert resp.status_code == 200
    assert resp.json["availability"] == "Unavailable"

    # Restore availability
    resp2 = client.patch("/api/services/SVC-001/status", headers=headers, json={"availability": "Available"})
    assert resp2.status_code == 200
    assert resp2.json["availability"] == "Available"

# ==============================================================================
# 6. APPLICATION STATUS HISTORY & TIMELINE WORKFLOW (PHASE 10)
# ==============================================================================

def test_application_status_update_records_officer_and_history(client):
    rev_token = get_auth_token(client, "officer@mpsuvidha.demo", "Officer@123")
    headers = {"Authorization": f"Bearer {rev_token}"}

    # MPS-2026-10482 is in Revenue Department
    resp = client.patch("/api/applications/MPS-2026-10482/status", headers=headers, json={
        "status": "Under Review",
        "remarks": "Document preliminary review completed."
    })
    assert resp.status_code == 200
    assert resp.json["status"] == "Under Review"

    # Verify history record
    with connect_db() as db:
        hist = db.execute("SELECT * FROM application_history WHERE application_id='MPS-2026-10482' ORDER BY id DESC LIMIT 1").fetchone()
        assert hist["status"] == "Under Review"
        assert hist["changed_by"] == 2  # Officer Priya Verma ID
        assert "preliminary review" in hist["remarks"]

# ==============================================================================
# 7. CERTIFICATE VERIFICATION & QR CODE GENERATION (PHASE 11 & 12)
# ==============================================================================

def test_certificate_verification_valid(client):
    resp = client.get("/api/certificates/verify/MPS-CERT-2026-09831")
    assert resp.status_code == 200
    data = resp.json
    assert data["valid"] is True
    assert data["status"] == "Valid"
    assert "A••••" in data["applicant_name"], "Applicant full name was not masked for privacy!"
    assert "independent demonstration" in data["disclaimer"].lower()

def test_certificate_verification_invalid(client):
    resp = client.get("/api/certificates/verify/NON-EXISTENT-CERT-99999")
    assert resp.status_code == 404

def test_certificate_pdf_download_generates_valid_content(client):
    resp = client.get("/api/certificates/MPS-CERT-2026-09831/download")
    assert resp.status_code == 200
    assert resp.mimetype == "application/pdf"
    assert len(resp.data) > 20000, "Generated PDF is too small or invalid!"
    assert resp.data.startswith(b"%PDF"), "Generated file does not have valid PDF header!"

# ==============================================================================
# 8. PRIVACY & FEEDBACK CONTROLS (PHASE 13)
# ==============================================================================

def test_feedback_public_summary_protects_privacy(client):
    """Public feedback endpoint must NOT expose submitter names or private complaints."""
    resp = client.get("/api/feedback")
    assert resp.status_code == 200
    data = resp.json
    assert "summary" in data
    assert "distribution" in data
    assert "items" not in data or len(data.get("items", [])) == 0, "Public feedback endpoint leaked private messages!"

def test_admin_feedback_requires_authorization(client):
    """Only administrators can review detailed feedback entries."""
    resp = client.get("/api/admin/feedback")
    assert resp.status_code == 401

    adm_token = get_auth_token(client, "admin@mpsuvidha.demo", "Admin@123")
    resp2 = client.get("/api/admin/feedback", headers={"Authorization": f"Bearer {adm_token}"})
    assert resp2.status_code == 200
    assert isinstance(resp2.json, list)

# ==============================================================================
# 9. STUDENT EVALUATION RESTRICTIONS (PHASE 14)
# ==============================================================================

def test_evaluation_restricted_from_public_and_citizens(client):
    """Public users and ordinary citizens cannot access internal evaluation data."""
    resp = client.get("/api/evaluations")
    assert resp.status_code == 401

    cit_token = get_auth_token(client, "citizen@mpsuvidha.demo", "Citizen@123")
    resp2 = client.get("/api/evaluations", headers={"Authorization": f"Bearer {cit_token}"})
    assert resp2.status_code == 403

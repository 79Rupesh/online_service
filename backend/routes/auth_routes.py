"""Authentication routes: registration, login, and profile management."""
import re
import sqlite3
import time
from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from backend.auth import auth_required, error, token_for
from backend.database import connect_db, now_iso, row_dict

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# In-memory rate limiting for login attempts (IP/Email -> list of failure timestamps)
_login_failures: dict[str, list[float]] = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 minutes

def is_rate_limited(key: str) -> bool:
    """Checks if an identifier has exceeded the maximum allowed failed attempts."""
    now = time.time()
    attempts = [t for t in _login_failures.get(key, []) if now - t < LOCKOUT_SECONDS]
    _login_failures[key] = attempts
    return len(attempts) >= MAX_FAILED_ATTEMPTS

def record_failure(key: str) -> None:
    """Records a failed authentication attempt."""
    now = time.time()
    attempts = [t for t in _login_failures.get(key, []) if now - t < LOCKOUT_SECONDS]
    attempts.append(now)
    _login_failures[key] = attempts

def clear_failures(key: str) -> None:
    """Resets failed attempt records upon successful login."""
    _login_failures.pop(key, None)

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    mobile = re.sub(r"\s+", "", str(data.get("mobile", "")))
    password = str(data.get("password", ""))
    address = str(data.get("address", "")).strip()

    if len(name) < 2 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return error("Enter your full name and a valid email address.")
    if not re.fullmatch(r"[0-9+() -]{8,18}", mobile):
        return error("Enter a valid mobile phone number.")
    if len(password) < 8:
        return error("Password must contain at least 8 characters.")

    try:
        with connect_db() as db:
            cursor = db.execute(
                "INSERT INTO users (name, email, mobile, password_hash, address, role, department, created_at) VALUES (?, ?, ?, ?, ?, 'citizen', '', ?)",
                (name, email, mobile, generate_password_hash(password), address, now_iso())
            )
            user = db.execute("SELECT * FROM users WHERE id=?", (cursor.lastrowid,)).fetchone()
            return jsonify({
                "token": token_for(user),
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "mobile": user["mobile"],
                    "address": user["address"],
                    "role": user["role"],
                    "department": user["department"]
                }
            }), 201
    except sqlite3.IntegrityError:
        return error("An account with that email address already exists.", 409)

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    client_ip = request.remote_addr or "127.0.0.1"
    rate_key = f"{client_ip}:{email}"

    if is_rate_limited(rate_key) or is_rate_limited(client_ip):
        return error("Too many failed sign-in attempts. Your access is temporarily restricted for 5 minutes. Please try again later.", 429)

    if not email or not password:
        return error("Email address and password are required.")

    with connect_db() as db:
        user = db.execute("SELECT * FROM users WHERE email=? AND active=1", (email,)).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        record_failure(rate_key)
        record_failure(client_ip)
        return error("Email or password is incorrect.", 401)

    clear_failures(rate_key)
    clear_failures(client_ip)

    return jsonify({
        "token": token_for(user),
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "mobile": user["mobile"],
            "address": user["address"],
            "role": user["role"],
            "department": user["department"]
        }
    })

@auth_bp.get("/me")
@auth_required()
def current_user():
    u = g.user
    return jsonify({
        "id": u["id"],
        "name": u["name"],
        "email": u["email"],
        "mobile": u["mobile"],
        "address": u["address"],
        "role": u["role"],
        "department": u.get("department", "")
    })

@auth_bp.patch("/profile")
@auth_required()
def update_profile():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    mobile = str(data.get("mobile", "")).strip()
    address = str(data.get("address", "")).strip()

    if len(name) < 2 or not re.fullmatch(r"[0-9+() -]{8,18}", mobile):
        return error("Enter a valid name and mobile phone number.")

    with connect_db() as db:
        db.execute("UPDATE users SET name=?, mobile=?, address=? WHERE id=?", (name, mobile, address, g.user["id"]))

    return jsonify({"message": "Profile updated successfully."})


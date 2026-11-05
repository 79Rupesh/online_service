"""Authentication routes: registration, login, and profile management."""
import re
import sqlite3
from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from backend.auth import auth_required, error, token_for
from backend.database import connect_db, now_iso, row_dict

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

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
                "INSERT INTO users (name, email, mobile, password_hash, address, role, created_at) VALUES (?, ?, ?, ?, ?, 'citizen', ?)",
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
                    "role": user["role"]
                }
            }), 201
    except sqlite3.IntegrityError:
        return error("An account with that email address already exists.", 409)

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return error("Email address and password are required.")

    with connect_db() as db:
        user = db.execute("SELECT * FROM users WHERE email=? AND active=1", (email,)).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return error("Email or password is incorrect.", 401)

    return jsonify({
        "token": token_for(user),
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "mobile": user["mobile"],
            "address": user["address"],
            "role": user["role"]
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
        "role": u["role"]
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


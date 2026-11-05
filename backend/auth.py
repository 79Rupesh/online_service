"""Authentication, password verification, and authorization middleware."""
import sqlite3
from functools import wraps
from flask import g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from backend.config import Config
from backend.database import connect_db, row_dict

serializer = URLSafeTimedSerializer(Config.SECRET_KEY, salt=Config.TOKEN_SALT)

def error(message: str, status: int = 400):
    """Returns a standardized JSON error response."""
    return jsonify({"error": message}), status

def token_for(user: dict | sqlite3.Row) -> str:
    """Generates a signed, time-limited bearer token for a verified user."""
    return serializer.dumps({"sub": user["id"], "role": user["role"]})

def auth_required(*roles):
    """Decorator to require a valid bearer token and optional role check."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            raw = request.headers.get("Authorization", "")
            if not raw.startswith("Bearer "):
                return error("Please sign in to continue.", 401)
            
            token = raw[7:].strip()
            try:
                payload = serializer.loads(token, max_age=Config.TOKEN_MAX_AGE_SECONDS)
            except SignatureExpired:
                return error("Your session has expired. Please sign in again.", 401)
            except BadSignature:
                return error("Invalid session token.", 401)
            
            user_id = payload.get("sub")
            with connect_db() as db:
                user = db.execute("SELECT * FROM users WHERE id=? AND active=1", (user_id,)).fetchone()
            
            if not user:
                return error("Account not found or has been disabled.", 401)
            
            g.user = row_dict(user)
            
            if roles and g.user["role"] not in roles:
                return error("You do not have permission to perform this action.", 403)
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


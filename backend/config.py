"""Configuration settings for MP Suvidha: Madhya Pradesh Digital Services Portal."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Config:
    ROOT_DIR = ROOT_DIR
    INSTANCE_DIR = ROOT_DIR / "instance"
    UPLOAD_DIR = ROOT_DIR / "uploads"
    
    # Ensure necessary folders exist
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / "documents").mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / "certificates").mkdir(parents=True, exist_ok=True)
    
    # Database path: supports MP_SUVIDHA_DB or defaults to instance/mpsuvidha.db
    _custom_db = os.environ.get("MP_SUVIDHA_DB")
    if _custom_db:
        DB_PATH = Path(_custom_db)
    else:
        DB_PATH = INSTANCE_DIR / "mpsuvidha.db"

    # Environment
    ENV = os.environ.get("FLASK_ENV", "development").lower()
    IS_PRODUCTION = ENV == "production"

    # Cryptographic secret key: Enforce explicit secret in production
    _env_secret = os.environ.get("SECRET_KEY")
    _dev_fallback = "mpsuvidha-portal-dev-only-secret-key-2026"

    if IS_PRODUCTION:
        if not _env_secret or _env_secret == _dev_fallback or "change-in-production" in _env_secret:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR:\n"
                "In production mode (FLASK_ENV=production), a strong, unique SECRET_KEY environment variable is mandatory.\n"
                "Please configure a 32+ character random secret key in your .env or server environment."
            )
        SECRET_KEY = _env_secret
    else:
        SECRET_KEY = _env_secret or _dev_fallback

    TOKEN_SALT = "mpsuvidha-session-salt-v3"
    TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24  # 24 hours
    
    # Strict upload restrictions
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx"}
    MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB per file
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB total request limit

    # Known file magic bytes/signatures for security inspection (Phase 3 D)
    MAGIC_SIGNATURES = {
        "pdf": [b"%PDF"],
        "jpg": [b"\xff\xd8\xff"],
        "jpeg": [b"\xff\xd8\xff"],
        "png": [b"\x89PNG\r\n\x1a\n"],
        "doc": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],
        "docx": [b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"],
    }

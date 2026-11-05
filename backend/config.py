"""Configuration settings for MP Suvidha: Madhya Pradesh Digital Services Portal."""
import os
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
    
    # Database path: supports MP_SUVIDHA_DB, JANSEVA_DB, or defaults to mpsuvidha.db
    _custom_db = os.environ.get("MP_SUVIDHA_DB") or os.environ.get("JANSEVA_DB")
    if _custom_db:
        DB_PATH = Path(_custom_db)
    else:
        DB_PATH = INSTANCE_DIR / "mpsuvidha.db"

    # Cryptographic secret key with secure fallback
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("MP_SUVIDHA_SECRET", "mpsuvidha-portal-secure-production-key-2026")
    TOKEN_SALT = "mpsuvidha-session-salt-v2"
    TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24  # 24 hours
    
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx"}
    MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB per file
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB total request limit

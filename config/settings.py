import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# LOAD .ENV
# ============================================================

ENV_FILE = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

# API key is loaded from .env
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


# IMPORTANT:
# Keep the model fixed here so an old GEMINI_MODEL value
# in .env cannot accidentally select gemini-2.0-flash.
GEMINI_MODEL = "gemini-2.5-flash"


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "recruiter_ai.db"
)


# ============================================================
# JUDGE0 CONFIGURATION
# ============================================================

JUDGE0_URL = os.getenv(
    "JUDGE0_URL",
    "http://localhost:2358"
).strip()


# ============================================================
# DEBUG
# ============================================================

DEBUG = (
    os.getenv(
        "DEBUG",
        "False"
    ).lower()
    == "true"
)


# ============================================================
# GEMINI CONFIGURATION CHECK
# ============================================================

def is_gemini_configured():
    """
    Returns True if GEMINI_API_KEY exists.
    """

    return bool(GEMINI_API_KEY)
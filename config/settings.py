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

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


# Current stable Gemini model
GEMINI_MODEL = "gemini-3.6-flash"


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

JUDGE0_API_URL = os.getenv(
    "JUDGE0_API_URL",
    "http://localhost:2358"
).strip()

# Backward compatibility
JUDGE0_URL = JUDGE0_API_URL


# ============================================================
# DEBUG
# ============================================================

DEBUG = (
    os.getenv(
        "DEBUG",
        "False"
    ).lower() == "true"
)


# ============================================================
# GEMINI STATUS
# ============================================================

def is_gemini_configured():
    """
    Check whether Gemini API key is configured.
    """
    return bool(GEMINI_API_KEY)
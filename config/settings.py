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
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()

# Use a currently supported model.
# If GEMINI_MODEL exists in .env, it will be used.
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
).strip()


# ============================================================
# DATABASE
# ============================================================

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "recruiter_ai.db"
)


# ============================================================
# JUDGE0
# ============================================================

JUDGE0_URL = os.getenv(
    "JUDGE0_URL",
    "http://localhost:2358"
).strip()


# ============================================================
# DEBUG
# ============================================================

DEBUG = os.getenv(
    "DEBUG",
    "False"
).lower() == "true"


# ============================================================
# GEMINI STATUS
# ============================================================

def is_gemini_configured():
    return bool(GEMINI_API_KEY)
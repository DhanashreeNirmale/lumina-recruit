import os
from pathlib import Path

from dotenv import load_dotenv


# =========================================================
# PROJECT PATHS
# =========================================================

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)


# =========================================================
# APPLICATION
# =========================================================

APP_NAME = os.getenv(
    "APP_NAME",
    "IndiaTech Recruiter AI"
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0"
)

DEBUG = os.getenv(
    "DEBUG",
    "False"
).lower() == "true"


# =========================================================
# GOOGLE GEMINI
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


# =========================================================
# ASSESSMENT APIs
# =========================================================

HACKEREARTH_API_KEY = os.getenv(
    "HACKEREARTH_API_KEY",
    ""
)

METTL_API_KEY = os.getenv(
    "METTL_API_KEY",
    ""
)


# =========================================================
# DATABASE
# =========================================================

DATABASE_DIR = BASE_DIR / "database"

DATABASE_PATH = DATABASE_DIR / "recruiter.db"


# =========================================================
# DATA DIRECTORIES
# =========================================================

DATA_DIR = BASE_DIR / "data"

SAMPLE_RESUMES_DIR = (
    DATA_DIR / "sample_resumes"
)

SAMPLE_JOBS_DIR = (
    DATA_DIR / "sample_jobs"
)


# =========================================================
# RESUME CONFIGURATION
# =========================================================

ALLOWED_RESUME_EXTENSIONS = [
    ".pdf",
    ".docx",
]

MAX_RESUME_SIZE_MB = int(
    os.getenv(
        "MAX_RESUME_SIZE_MB",
        "10"
    )
)


# =========================================================
# AI CONFIGURATION
# =========================================================

LLM_TEMPERATURE = float(
    os.getenv(
        "LLM_TEMPERATURE",
        "0"
    )
)

MAX_RESUME_TEXT_LENGTH = int(
    os.getenv(
        "MAX_RESUME_TEXT_LENGTH",
        "30000"
    )
)


# =========================================================
# MATCHING WEIGHTS
# =========================================================

SKILL_WEIGHT = 0.40

EXPERIENCE_WEIGHT = 0.20

EDUCATION_WEIGHT = 0.10

NOTICE_WEIGHT = 0.10

SALARY_WEIGHT = 0.10

LOCATION_WEIGHT = 0.10


# =========================================================
# MATCHING THRESHOLDS
# =========================================================

SHORTLIST_THRESHOLD = float(
    os.getenv(
        "SHORTLIST_THRESHOLD",
        "80"
    )
)

REVIEW_THRESHOLD = float(
    os.getenv(
        "REVIEW_THRESHOLD",
        "65"
    )
)


# =========================================================
# INTERVIEW
# =========================================================

DEFAULT_INTERVIEW_TYPE = "Technical"

SUPPORTED_INTERVIEW_TYPES = [
    "Technical",
    "HR",
    "Managerial",
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def ensure_directories():
    """
    Create required project directories.
    """

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    SAMPLE_RESUMES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    SAMPLE_JOBS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def is_gemini_configured():
    """
    Check whether Gemini API credentials exist.
    """

    return bool(
        GEMINI_API_KEY.strip()
    )


def is_hackerearth_configured():
    """
    Check whether HackerEarth API credentials exist.

    This only checks the key. It does not claim that
    a provider endpoint is available.
    """

    return bool(
        HACKEREARTH_API_KEY.strip()
    )


def is_mettl_configured():
    """
    Check whether Mettl API credentials exist.
    """

    return bool(
        METTL_API_KEY.strip()
    )
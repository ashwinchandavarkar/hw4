"""Runtime configuration and shared paths for the Campus Customs backend.

The Portkey API key is read from the course-root `.env`
(`AI for Managers/.env`) so no secret ever lives in source. A value already
present in the environment takes precedence.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# backend/config.py -> backend -> "HW 4"
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent                     # the "HW 4" folder
COURSE_ROOT = PROJECT_DIR.parents[2]                 # "AI for Managers"

DATA_DIR = PROJECT_DIR / "data"
DB_PATH = Path(os.getenv("CAMPUS_CUSTOMS_DB", DATA_DIR / "campus_customs.db"))
PRODUCTS_DIR = DATA_DIR / "products"

PROMPTS_DIR = BACKEND_DIR / "prompts"
PROMPT_PATH = PROMPTS_DIR / "prompt.md"

OUTPUT_DIR = PROJECT_DIR / "output"
AUDIT_PATH = OUTPUT_DIR / "audit_trail.json"

# Model / gateway configuration (matches the course standard).
DEFAULT_MODEL = os.getenv("CAMPUS_CUSTOMS_MODEL", "gpt-5.6-luna")
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")
PORTKEY_PROVIDER = os.getenv("PORTKEY_PROVIDER", "openai")

# Signed-session secret for the simple token auth.
SESSION_SECRET = os.getenv("CAMPUS_CUSTOMS_SESSION_SECRET", "dev-only-session-secret")


def load_root_env() -> None:
    """Load a `.env` without overriding real environment values.

    Checks, in order: the project root (`hw4/.env`, used by a cloned repo),
    `backend/.env`, and the course-root `.env` (used in the original course tree).
    """
    for env_file in (PROJECT_DIR / ".env", BACKEND_DIR / ".env", COURSE_ROOT / ".env"):
        if env_file.exists():
            load_dotenv(env_file, override=False)


def require_portkey_key() -> str:
    load_root_env()
    key = os.getenv("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError(
            "PORTKEY_API_KEY is not set in the course-root .env or the environment."
        )
    return key

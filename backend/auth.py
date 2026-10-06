"""Password hashing and lightweight signed-token sessions.

Passwords use PBKDF2-HMAC-SHA256, matching the format already stored in the
provided database: ``pbkdf2_sha256$<salt>$<hex-digest>``. We also accept a
Django-style four-part variant (``pbkdf2_sha256$<iterations>$<salt>$<digest>``)
so verification is robust. New accounts created through this app round-trip
cleanly through signup and login.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
from typing import Optional

from itsdangerous import BadSignature, URLSafeTimedSerializer

from config import SESSION_SECRET

ALGORITHM = "pbkdf2_sha256"
# The provided database hashes accounts at 120,000 iterations (the format is
# `pbkdf2_sha256$salt$hash`, which omits the count). New accounts use the same
# count so they match the existing scheme.
DEFAULT_ITERATIONS = int(os.getenv("CAMPUS_CUSTOMS_PBKDF2_ITERATIONS", "120000"))
# Fallback count tried when verifying a stored 3-part hash. The provided
# database uses 120,000 (DEFAULT_ITERATIONS); one extra value keeps the list
# short so a wrong password stays fast.
LEGACY_ITERATION_CANDIDATES = [100000]
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # one week

_serializer = URLSafeTimedSerializer(SESSION_SECRET, salt="campus-customs-session")


def hash_password(password: str, *, iterations: int = DEFAULT_ITERATIONS) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    ).hex()
    return f"{ALGORITHM}${salt}${digest}"


def _derive(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    ).hex()


def verify_password(password: str, stored: str) -> bool:
    """Constant-time verification against a stored PBKDF2 string."""
    if not stored:
        return False
    parts = stored.split("$")
    try:
        if len(parts) == 3:
            # Count not stored: try the known default plus fallbacks.
            algo, salt, digest = parts
            counts = list(dict.fromkeys([DEFAULT_ITERATIONS, *LEGACY_ITERATION_CANDIDATES]))
        elif len(parts) == 4:
            # Django-style: iteration count embedded.
            algo, iters, salt, digest = parts
            counts = [int(iters)]
        else:
            return False
    except (ValueError, TypeError):
        return False
    if algo != ALGORITHM:
        return False
    for iterations in counts:
        if hmac.compare_digest(_derive(password, salt, iterations), digest):
            return True
    return False


# ----- Session tokens -----

def issue_token(user_id: int) -> str:
    return _serializer.dumps({"uid": user_id, "ts": int(time.time())})


def read_token(token: str) -> Optional[int]:
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE)
        return int(data["uid"])
    except (BadSignature, KeyError, ValueError, TypeError):
        return None

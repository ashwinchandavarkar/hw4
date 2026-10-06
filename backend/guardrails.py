"""Lightweight pre-LLM safety guardrail for the chat endpoint.

Messages that try to extract credentials or other customers' data, or to
override the assistant's instructions (prompt injection), are caught here and
answered with a safe canned reply — before any model call. This protects
customer data deterministically and avoids spending tokens on abusive input.
"""
from __future__ import annotations

import re

# Patterns that should never be served by the shopping assistant.
_BLOCKED_PATTERNS = [
    # Credentials / secrets
    r"\bpassword(s)?\b",
    r"\bpassword[_\s-]?hash(es)?\b",
    r"\bhashe?s?\b",
    r"\bapi[_\s-]?key\b",
    r"\bcredential(s)?\b",
    # Other customers' / everyone's data
    r"\b(other|another|everyone'?s|all)\s+(user|customer|account|shopper)",
    r"\b(list|show|dump|export|give me)\s+(all|every)\s+(user|customer|account|email)",
    r"\bemail(s)?\s+of\s+(other|all|every)",
    # Prompt injection / instruction override
    r"ignore (all|your|previous|the) (instructions|rules|prompt)",
    r"\bsystem prompt\b",
    r"\bdeveloper (message|prompt)\b",
    r"reveal your (instructions|prompt|rules)",
    r"disregard (your|the|all) (instructions|rules)",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _BLOCKED_PATTERNS]

SAFE_REPLY = (
    "I'm sorry, but I can't help with that. I'm the Campus Customs shopping "
    "assistant — I can only help you find Yale apparel, prices, and sizes, and I "
    "never share account passwords or other customers' information. What can I "
    "help you find today?"
)


def check_message(message: str) -> str | None:
    """Return a safe canned reply if the message is disallowed, else None."""
    for pattern in _COMPILED:
        if pattern.search(message):
            return SAFE_REPLY
    return None

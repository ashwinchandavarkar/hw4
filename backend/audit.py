"""Append-only audit trail of agent-loop activity.

Every chat turn appends one record per tool call plus a final record (with the
stop reason) to `output/audit_trail.json`. The file is never overwritten between
runs: existing entries are loaded and new ones are appended, so the trail grows
and prior activity is preserved. Only tool names, brief arguments, and brief
result summaries are stored — never image data or secrets.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from pydantic_ai.messages import ToolCallPart, ToolReturnPart

from config import AUDIT_PATH

_MAX = 240  # characters kept for brief arguments/results


def _brief(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    text = " ".join(text.split())
    return text if len(text) <= _MAX else text[:_MAX] + "…"


def append_entries(entries: list[dict]) -> None:
    """Append records to the audit trail without discarding existing ones."""
    if not entries:
        return
    existing: list[dict] = []
    if AUDIT_PATH.exists():
        try:
            loaded = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                existing = loaded
        except (json.JSONDecodeError, OSError):
            existing = []
    existing.extend(entries)
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def entries_from_run(result: Any, customer: str, stop_reason: str = "completed") -> list[dict]:
    """Build audit records from a PydanticAI run result (one per tool call + final)."""
    now = datetime.now(timezone.utc).isoformat()
    # Collect tool results by call id so each call is paired with its output.
    returns: dict[str, Any] = {}
    for msg in result.all_messages():
        for part in getattr(msg, "parts", []):
            if isinstance(part, ToolReturnPart):
                returns[part.tool_call_id] = part.content

    entries: list[dict] = []
    step = 0
    for msg in result.all_messages():
        for part in getattr(msg, "parts", []):
            if isinstance(part, ToolCallPart):
                step += 1
                entries.append(
                    {
                        "timestamp": now,
                        "iteration": step,
                        "customer": customer,
                        "tool_name": part.tool_name,
                        "arguments": _brief(part.args),
                        "result_summary": _brief(returns.get(part.tool_call_id, "")),
                        "stop_reason": None,
                    }
                )
    # Final record: the loop ended and a reply was produced.
    entries.append(
        {
            "timestamp": now,
            "iteration": step + 1,
            "customer": customer,
            "tool_name": None,
            "arguments": "",
            "result_summary": _brief(getattr(result, "output", "")),
            "stop_reason": stop_reason,
        }
    )
    return entries


def log_simple(customer: str, note: str, stop_reason: str) -> None:
    """Append a single non-tool record (e.g. a guardrail block)."""
    append_entries(
        [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "iteration": 1,
                "customer": customer,
                "tool_name": None,
                "arguments": _brief(note),
                "result_summary": "",
                "stop_reason": stop_reason,
            }
        ]
    )

#!/usr/bin/env python3
"""
Format session-derived file change evidence for handoff artifacts.

Use this when git evidence is unavailable, clean, or incomplete but the current
session still has known touched files worth preserving in the handoff.
"""

from __future__ import annotations

import json
import sys


VALID_STATUSES = {
    "modified",
    "created",
    "deleted",
    "renamed",
    "untracked",
    "committed",
    "session-mentioned",
    "viewed",
    "unknown",
}

VALID_CONFIDENCE = {"high", "medium", "low"}


def emit(payload: dict, status: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return status


def normalize_file(item: dict) -> dict:
    path = str(item.get("path", "")).strip()
    status = str(item.get("status", "unknown")).strip().lower() or "unknown"
    confidence = str(item.get("confidence", "medium")).strip().lower() or "medium"
    summary = str(item.get("summary", "")).strip()

    if status not in VALID_STATUSES:
        status = "unknown"
    if confidence not in VALID_CONFIDENCE:
        confidence = "medium"
    if not summary:
        summary = "session-derived change evidence"

    line_ranges = [str(value).strip() for value in item.get("line_ranges", []) if str(value).strip()]
    snippets = [str(value).strip() for value in item.get("snippets", []) if str(value).strip()]

    normalized = {
        "path": path or "<unknown-path>",
        "status": status,
        "summary": summary,
        "confidence": confidence,
        "line_ranges": line_ranges,
        "snippets": snippets[:3],
    }

    old_path = str(item.get("old_path", "")).strip()
    if old_path:
        normalized["old_path"] = old_path

    return normalized


def build_markdown(files: list[dict]) -> str:
    lines = [
        "## Changed Files",
        "- Evidence source: `session-derived`",
    ]
    if not files:
        lines.append("- No session-derived file changes were captured.")
        return "\n".join(lines)

    for item in files:
        header = f'- `{item["path"]}` ({item["status"]})'
        if item.get("old_path"):
            header += f' from `{item["old_path"]}`'
        lines.append(header)
        lines.append(f'- Confidence: `{item["confidence"]}`')

        if item["line_ranges"]:
            joined = ", ".join(f"`{value}`" for value in item["line_ranges"])
            lines.append(f"- Line ranges: {joined}")
        else:
            lines.append("- Line ranges: session-derived / approximate")

        lines.append(f'- Summary: {item["summary"]}')

        if item["snippets"]:
            lines.append("- Snippets:")
            for snippet in item["snippets"]:
                lines.append(f"  - `{snippet}`")

    return "\n".join(lines)


def main() -> int:
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        return emit(
            {
                "evidence_source": "session-derived",
                "has_changes": False,
                "files": [],
                "markdown": "## Changed Files\n- Evidence source: `session-derived`\n- No session-derived file changes were captured.",
            }
        )

    payload = json.loads(raw_input)
    files = [normalize_file(item) for item in payload.get("files", [])]

    return emit(
        {
            "evidence_source": "session-derived",
            "has_changes": bool(files),
            "files": files,
            "markdown": build_markdown(files),
        }
    )


if __name__ == "__main__":
    sys.exit(main())

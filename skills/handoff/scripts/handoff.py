#!/usr/bin/env python3
"""
Deterministic handoff file resolver for long-running development sessions.

This helper intentionally decides only:
- where handoff files live
- whether write should create or update
- which file read should open by default
- and ensures the handoff directory exists for new writes
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_TOPIC = "handoff"
SCRIPT_PATH = Path(__file__).resolve()
SKILL_ROOT = SCRIPT_PATH.parents[1]

def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[\\/]+", "-", text)
    text = re.sub(r"[^a-z0-9._-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-._")
    return text or DEFAULT_TOPIC


def get_progress_dir(project_root: Path) -> Path:
    return project_root / "repo" / "progress"


def resolve_handoff_root(project_root: Path) -> tuple[Path, str]:
    project_root = project_root.resolve()

    if get_progress_dir(project_root).exists():
        return project_root, "project_root"

    for ancestor in project_root.parents:
        if get_progress_dir(ancestor).exists():
            return ancestor, "ancestor_repo_progress"

    return project_root, "project_root_fallback"


def get_handoff_dir(project_root: Path) -> Path:
    resolved_root, _ = resolve_handoff_root(project_root)
    return resolved_root / "repo" / "progress" / "handoffs"


def build_resolution_payload(project_root: Path) -> dict[str, str]:
    resolved_root, resolution = resolve_handoff_root(project_root)
    return {
        "requested_project_root": str(project_root.resolve()),
        "project_root": str(resolved_root),
        "project_root_resolution": resolution,
        "handoff_dir": str(get_handoff_dir(project_root).resolve()),
    }


def resolve_existing_file(project_root: Path, candidate: str | None) -> Path | None:
    if not candidate:
        return None

    raw = Path(candidate)
    attempts: list[Path] = []

    if raw.is_absolute():
        attempts.append(raw)
    else:
        attempts.append(project_root / raw)
        attempts.append(get_handoff_dir(project_root) / raw)

    for attempt in attempts:
        if attempt.exists() and attempt.is_file():
            return attempt.resolve()

    return None


def pick_latest_handoff(project_root: Path) -> Path | None:
    handoff_dir = get_handoff_dir(project_root)
    if not handoff_dir.exists():
        return None

    files = [path for path in handoff_dir.glob("*.md") if path.is_file()]
    if not files:
        return None

    return max(files, key=lambda path: path.stat().st_mtime).resolve()


def create_new_handoff(project_root: Path, topic: str | None) -> Path:
    handoff_dir = get_handoff_dir(project_root)
    handoff_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    slug = slugify(topic or DEFAULT_TOPIC)
    path = handoff_dir / f"{stamp}-{slug}.md"

    counter = 2
    while path.exists():
        path = handoff_dir / f"{stamp}-{slug}-{counter}.md"
        counter += 1

    return path.resolve()


def looks_like_skill_root(project_root: Path) -> bool:
    project_root = project_root.resolve()
    if project_root == SKILL_ROOT or SKILL_ROOT in project_root.parents:
        return True

    parts = [part.lower() for part in project_root.parts]
    if len(parts) >= 3 and parts[-3:] == [".claude", "skills", "handoff"]:
        return True

    return False


def emit(payload: dict, status: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return status


def handle_write(project_root: Path, target: str | None) -> int:
    if not target:
        return emit(
            {
                "mode": "write",
                "error": "topic_required",
                **build_resolution_payload(project_root),
                "message": (
                    "A topic slug is required for write mode."
                    " Example: python scripts/handoff.py write auth-refactor --project-root ."
                ),
            },
            status=1,
        )

    existing = resolve_existing_file(project_root, target)
    if existing is not None:
        return emit(
            {
                "mode": "write",
                "action": "update",
                **build_resolution_payload(project_root),
                "path": str(existing),
            }
        )

    created = create_new_handoff(project_root, target)
    return emit(
        {
            "mode": "write",
            "action": "create",
            **build_resolution_payload(project_root),
            "path": str(created),
        }
    )


def handle_read(project_root: Path, target: str | None) -> int:
    if target:
        existing = resolve_existing_file(project_root, target)
        if existing is None:
            return emit(
                {
                    "mode": "read",
                    "error": "specified_handoff_not_found",
                    **build_resolution_payload(project_root),
                    "requested": target,
                },
                status=2,
            )

        return emit(
            {
                "mode": "read",
                "source": "specified",
                **build_resolution_payload(project_root),
                "path": str(existing),
            }
        )

    latest = pick_latest_handoff(project_root)
    if latest is None:
        return emit(
            {
                "mode": "read",
                "error": "no_handoff_found",
                **build_resolution_payload(project_root),
            },
            status=3,
        )

    return emit(
        {
            "mode": "read",
            "source": "latest",
            **build_resolution_payload(project_root),
            "path": str(latest),
        }
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve handoff files deterministically for write/read flows."
    )
    parser.add_argument("mode", choices=("write", "read"))
    parser.add_argument("target", nargs="?", help="Topic slug or handoff file path.")
    parser.add_argument(
        "--project-root",
        default=".",
        help=(
            "Active project path used for handoff resolution. If repo/progress "
            "exists only in an ancestor directory, the resolver will use the "
            "nearest matching ancestor."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()

    if looks_like_skill_root(project_root):
        return emit(
            {
                "mode": args.mode,
                "error": "invalid_project_root",
                "project_root": str(project_root),
                "skill_root": str(SKILL_ROOT),
                "message": (
                    "Project root points at the installed handoff skill directory. "
                    "Pass --project-root with the active repository root instead."
                ),
            },
            status=4,
        )

    if args.mode == "write":
        return handle_write(project_root, args.target)
    return handle_read(project_root, args.target)


if __name__ == "__main__":
    sys.exit(main())

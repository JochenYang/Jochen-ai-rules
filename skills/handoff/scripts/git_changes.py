#!/usr/bin/env python3
"""
Summarize working tree changes for handoff documents.

This helper produces deterministic JSON so handoff writing can include:
- changed file paths
- line ranges for each diff hunk
- short code/content snippets from the current working tree diff
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


HUNK_RE = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? "
    r"\+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)


def emit(payload: dict, status: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize git working tree changes for handoff artifacts."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Active project path used to locate the current git repository.",
    )
    return parser.parse_args()


def run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def get_git_root(project_root: Path) -> Path | None:
    result = run_git(project_root, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def has_head(git_root: Path) -> bool:
    result = run_git(git_root, "rev-parse", "--verify", "HEAD")
    return result.returncode == 0


def get_status_map(git_root: Path) -> dict[str, dict[str, str]]:
    result = run_git(git_root, "status", "--porcelain=v1", "--untracked-files=all")
    status_map: dict[str, dict[str, str]] = {}

    for raw_line in result.stdout.splitlines():
        if not raw_line:
            continue

        code = raw_line[:2]
        path_info = raw_line[3:]
        old_path = None

        if code.startswith("??"):
            status = "untracked"
            path = path_info
        elif "R" in code or "C" in code:
            status = "renamed" if "R" in code else "copied"
            if " -> " in path_info:
                old_path, path = path_info.split(" -> ", 1)
            else:
                path = path_info
        elif "D" in code:
            status = "deleted"
            path = path_info
        elif "A" in code:
            status = "added"
            path = path_info
        else:
            status = "modified"
            path = path_info

        status_map[path] = {"status": status}
        if old_path:
            status_map[path]["old_path"] = old_path

    return status_map


def get_diff_text(git_root: Path) -> str:
    if has_head(git_root):
        result = run_git(git_root, "diff", "--unified=0", "--no-color", "HEAD", "--")
        return result.stdout

    cached = run_git(git_root, "diff", "--cached", "--unified=0", "--no-color", "--")
    unstaged = run_git(git_root, "diff", "--unified=0", "--no-color", "--")
    return cached.stdout + unstaged.stdout


def shorten(text: str, limit: int = 120) -> str:
    compact = " ".join(text.strip().split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def format_range(label: str, start: int, count: int) -> str:
    if count <= 1:
        return f"{label} {start}"
    return f"{label} {start}-{start + count - 1}"


def summarize_hunk(snippets: list[str], fallback: str) -> str:
    if snippets:
        return "; ".join(snippets[:2])
    return fallback


def parse_patch(diff_text: str, status_map: dict[str, dict[str, str]]) -> list[dict]:
    if not diff_text.strip():
        return []

    files: list[dict] = []
    current: dict | None = None
    current_hunk_snippets: list[str] = []

    def flush_hunk() -> None:
        nonlocal current_hunk_snippets
        if current is None or not current_hunk_snippets:
            current_hunk_snippets = []
            return

        current["hunk_summaries"].append(
            summarize_hunk(current_hunk_snippets, "change detected")
        )
        current_hunk_snippets = []

    def flush_file() -> None:
        flush_hunk()
        if current is None:
            return

        current["line_ranges"] = list(dict.fromkeys(current["line_ranges"]))
        current["snippets"] = current["snippets"][:4]
        current["summary"] = "; ".join(current["hunk_summaries"][:3]) or "change detected"
        current.pop("hunk_summaries", None)
        files.append(current.copy())

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            if current is not None:
                flush_file()

            parts = line.split()
            old_path = parts[2][2:]
            new_path = parts[3][2:]
            path = new_path if new_path != "/dev/null" else old_path
            status_info = status_map.get(path, {})
            current = {
                "path": path,
                "status": status_info.get("status", "modified"),
                "old_path": status_info.get("old_path", old_path if old_path != path else ""),
                "line_ranges": [],
                "snippets": [],
                "hunk_summaries": [],
            }
            current_hunk_snippets = []
            continue

        if current is None:
            continue

        if line.startswith("rename from "):
            current["old_path"] = line[len("rename from ") :]
            continue

        if line.startswith("rename to "):
            current["path"] = line[len("rename to ") :]
            continue

        if line.startswith("@@ "):
            flush_hunk()
            match = HUNK_RE.match(line)
            if not match:
                continue

            old_start = int(match.group("old_start"))
            old_count = int(match.group("old_count") or "1")
            new_start = int(match.group("new_start"))
            new_count = int(match.group("new_count") or "1")

            if current["status"] == "deleted" or new_count == 0:
                current["line_ranges"].append(format_range("old", old_start, old_count))
            else:
                current["line_ranges"].append(format_range("new", new_start, new_count))
            continue

        if line.startswith("+++") or line.startswith("---"):
            continue

        if line.startswith("+"):
            snippet = f'+ {shorten(line[1:])}'
            if snippet != "+ ":
                current["snippets"].append(snippet)
                current_hunk_snippets.append(f'add "{shorten(line[1:], 60)}"')
            continue

        if line.startswith("-"):
            snippet = f'- {shorten(line[1:])}'
            if snippet != "- ":
                current["snippets"].append(snippet)
                current_hunk_snippets.append(f'remove "{shorten(line[1:], 60)}"')
            continue

    if current is not None:
        flush_file()

    return files


def summarize_untracked_file(git_root: Path, relative_path: str) -> dict:
    file_path = git_root / relative_path
    snippets: list[str] = []

    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return {
            "path": relative_path,
            "status": "untracked",
            "line_ranges": ["binary or non-utf8"],
            "snippets": ["binary or non-utf8 file"],
            "summary": "new untracked binary or non-utf8 file",
        }

    for line in lines:
        stripped = shorten(line)
        if stripped:
            snippets.append(stripped)
        if len(snippets) >= 3:
            break

    total_lines = max(len(lines), 1)
    return {
        "path": relative_path,
        "status": "untracked",
        "line_ranges": [format_range("new", 1, total_lines)],
        "snippets": snippets,
        "summary": f"new file with {len(lines)} lines",
    }


def merge_changes(git_root: Path, files_from_patch: list[dict], status_map: dict[str, dict[str, str]]) -> list[dict]:
    merged: dict[str, dict] = {item["path"]: item for item in files_from_patch}

    for path, info in status_map.items():
        if info["status"] == "untracked":
            merged[path] = summarize_untracked_file(git_root, path)
            continue

        if path not in merged:
            entry = {
                "path": path,
                "status": info["status"],
                "line_ranges": [],
                "snippets": [],
                "summary": f'{info["status"]} without textual diff',
            }
            if "old_path" in info:
                entry["old_path"] = info["old_path"]
            merged[path] = entry

    return [merged[key] for key in sorted(merged)]


def build_markdown(files: list[dict]) -> str:
    lines = ["## Changed Files", "- Evidence source: `git`"]
    if not files:
        lines.append("- No working tree changes detected.")
        return "\n".join(lines)

    for item in files:
        header = f'- `{item["path"]}` ({item["status"]})'
        if item.get("old_path"):
            header += f' from `{item["old_path"]}`'
        lines.append(header)

        if item["line_ranges"]:
            joined_ranges = ", ".join(f"`{value}`" for value in item["line_ranges"])
            lines.append(f"  - Line ranges: {joined_ranges}")
        else:
            lines.append("  - Line ranges: not available")

        lines.append(f'  - Summary: {item["summary"]}')

        if item["snippets"]:
            lines.append("  - Snippets:")
            for snippet in item["snippets"][:3]:
                lines.append(f"    - `{snippet}`")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    git_root = get_git_root(project_root)

    if git_root is None:
        return emit(
            {
                "requested_project_root": str(project_root),
                "error": "not_git_repository",
                "evidence_source": "git-unavailable",
                "message": "Project root is not inside a git repository.",
                "has_changes": False,
                "files": [],
                "markdown": (
                    "## Changed Files\n"
                    "- Evidence source: `git-unavailable`\n"
                    "- Git repository not detected."
                ),
            },
            status=2,
        )

    status_map = get_status_map(git_root)
    files = merge_changes(git_root, parse_patch(get_diff_text(git_root), status_map), status_map)

    return emit(
        {
            "requested_project_root": str(project_root),
            "git_root": str(git_root),
            "evidence_source": "git",
            "has_changes": bool(files),
            "files": files,
            "markdown": build_markdown(files),
        }
    )


if __name__ == "__main__":
    sys.exit(main())

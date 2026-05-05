from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "handoff.py"
CHANGES_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "git_changes.py"
SESSION_CHANGES_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "session_changes.py"
)


def run_handoff(*args: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stdout)
    return result.returncode, payload


def run_change_report(project_root: Path) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(CHANGES_SCRIPT_PATH), "--project-root", str(project_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stdout)
    return result.returncode, payload


def run_session_change_report(payload: dict) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SESSION_CHANGES_SCRIPT_PATH)],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        check=False,
    )
    response = json.loads(result.stdout)
    return result.returncode, response


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


class HandoffPathResolutionTests(unittest.TestCase):
    def test_write_uses_nearest_ancestor_with_repo_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "HealthExcel"
            project = workspace / "health-tracker"
            (workspace / "repo" / "progress").mkdir(parents=True)
            project.mkdir(parents=True)

            code, payload = run_handoff(
                "write",
                "session",
                "--project-root",
                str(project),
            )

            self.assertEqual(code, 0)
            self.assertEqual(payload["requested_project_root"], str(project.resolve()))
            self.assertEqual(payload["project_root"], str(workspace.resolve()))
            self.assertEqual(
                payload["project_root_resolution"],
                "ancestor_repo_progress",
            )
            self.assertTrue(
                payload["path"].startswith(
                    str((workspace / "repo" / "progress" / "handoffs").resolve())
                )
            )

    def test_write_keeps_current_project_when_it_owns_repo_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "health-tracker"
            (project / "repo" / "progress").mkdir(parents=True)

            code, payload = run_handoff(
                "write",
                "session",
                "--project-root",
                str(project),
            )

            self.assertEqual(code, 0)
            self.assertEqual(payload["requested_project_root"], str(project.resolve()))
            self.assertEqual(payload["project_root"], str(project.resolve()))
            self.assertEqual(payload["project_root_resolution"], "project_root")
            self.assertTrue(
                payload["path"].startswith(
                    str((project / "repo" / "progress" / "handoffs").resolve())
                )
            )

    def test_read_picks_latest_handoff_from_ancestor_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "HealthExcel"
            project = workspace / "health-tracker"
            handoff_dir = workspace / "repo" / "progress" / "handoffs"
            handoff_dir.mkdir(parents=True)
            project.mkdir(parents=True)

            older = handoff_dir / "2026-04-14-0900-old.md"
            newer = handoff_dir / "2026-04-15-1000-new.md"
            older.write_text("old", encoding="utf-8")
            newer.write_text("new", encoding="utf-8")
            os.utime(older, (1_700_000_000, 1_700_000_000))
            os.utime(newer, (1_700_000_100, 1_700_000_100))

            code, payload = run_handoff(
                "read",
                "--project-root",
                str(project),
            )

            self.assertEqual(code, 0)
            self.assertEqual(payload["source"], "latest")
            self.assertEqual(payload["project_root"], str(workspace.resolve()))
            self.assertEqual(payload["project_root_resolution"], "ancestor_repo_progress")
            self.assertEqual(payload["path"], str(newer.resolve()))


    def test_write_without_topic_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "health-tracker"
            (project / "repo" / "progress").mkdir(parents=True)

            code, payload = run_handoff(
                "write",
                "--project-root",
                str(project),
            )

            self.assertNotEqual(code, 0)
            self.assertEqual(payload["error"], "topic_required")
            self.assertIn("mode", payload)
            self.assertEqual(payload["mode"], "write")


class HandoffChangeSummaryTests(unittest.TestCase):
    def test_change_report_includes_modified_file_ranges_and_content_snippets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()

            git(repo, "init")
            git(repo, "config", "user.name", "Test User")
            git(repo, "config", "user.email", "test@example.com")

            tracked = repo / "src" / "app.py"
            tracked.parent.mkdir(parents=True)
            tracked.write_text(
                "def greet(name):\n"
                "    return f'Hello, {name}'\n"
                "\n"
                "def main():\n"
                "    print(greet('world'))\n",
                encoding="utf-8",
            )
            git(repo, "add", ".")
            git(repo, "commit", "-m", "init")

            tracked.write_text(
                "def greet(name):\n"
                "    if not name:\n"
                "        return 'Hello, stranger'\n"
                "    return f'Hello, {name}'\n"
                "\n"
                "def main():\n"
                "    print(greet('codex'))\n",
                encoding="utf-8",
            )

            untracked = repo / "notes.md"
            untracked.write_text(
                "# Notes\n"
                "- capture pending release tasks\n"
                "- confirm handoff behavior\n",
                encoding="utf-8",
            )

            code, payload = run_change_report(repo)

            self.assertEqual(code, 0)
            self.assertTrue(payload["has_changes"])
            files = {item["path"]: item for item in payload["files"]}

            tracked_payload = files["src/app.py"]
            self.assertEqual(tracked_payload["status"], "modified")
            self.assertIn("new 2-3", tracked_payload["line_ranges"])
            self.assertTrue(
                any("if not name" in snippet for snippet in tracked_payload["snippets"])
            )
            self.assertIn("src/app.py", payload["markdown"])
            self.assertIn("new 2-3", payload["markdown"])

            untracked_payload = files["notes.md"]
            self.assertEqual(untracked_payload["status"], "untracked")
            self.assertIn("new 1-3", untracked_payload["line_ranges"])
            self.assertTrue(
                any("capture pending release tasks" in snippet for snippet in untracked_payload["snippets"])
            )

    def test_change_report_handles_clean_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()

            git(repo, "init")
            git(repo, "config", "user.name", "Test User")
            git(repo, "config", "user.email", "test@example.com")

            tracked = repo / "README.md"
            tracked.write_text("# Demo\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "init")

            code, payload = run_change_report(repo)

            self.assertEqual(code, 0)
            # With committed-today detection, the init commit (made just now)
            # is within the 24-hour window and appears as a committed-today file.
            # Working tree is clean, so the only files are committed-today.
            self.assertTrue(payload["has_changes"])
            files = {item["path"]: item for item in payload["files"]}
            self.assertIn("README.md", files)
            self.assertEqual(files["README.md"]["status"], "committed-today")

    def test_change_report_includes_committed_today_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()

            git(repo, "init")
            git(repo, "config", "user.name", "Test User")
            git(repo, "config", "user.email", "test@example.com")

            # Initial commit
            initial_file = repo / "README.md"
            initial_file.write_text("# Project\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "initial commit")

            # Second commit (both commits are within 24 hours of test runtime)
            committed_file = repo / "src" / "utils.py"
            committed_file.parent.mkdir(parents=True)
            committed_file.write_text(
                "def helper():\n    return True\n", encoding="utf-8"
            )
            git(repo, "add", ".")
            git(repo, "commit", "-m", "add utils module")

            # Working tree is clean — all changes are committed
            code, payload = run_change_report(repo)

            self.assertEqual(code, 0)
            self.assertTrue(payload["has_changes"])
            files = {item["path"]: item for item in payload["files"]}

            # The newly added file should appear as committed-today
            self.assertIn("src/utils.py", files)
            self.assertEqual(files["src/utils.py"]["status"], "committed-today")
            self.assertIn("committed-today", payload["markdown"])
            self.assertIn("src/utils.py", payload["markdown"])

    def test_change_report_handles_non_ascii_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()

            git(repo, "init")
            git(repo, "config", "user.name", "Test User")
            git(repo, "config", "user.email", "test@example.com")

            tracked = repo / "notes.txt"
            tracked.write_text("第一行\n第二行\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "init")

            tracked.write_text("第一行\n第二行-已修改\n第三行-新增\n", encoding="utf-8")

            code, payload = run_change_report(repo)

            self.assertEqual(code, 0)
            self.assertTrue(payload["has_changes"])
            tracked_payload = {item["path"]: item for item in payload["files"]}["notes.txt"]
            self.assertTrue(
                any("第二行-已修改" in snippet or "第三行-新增" in snippet for snippet in tracked_payload["snippets"])
            )


class HandoffSessionChangeSummaryTests(unittest.TestCase):
    def test_session_change_report_formats_current_session_file_edits(self) -> None:
        code, payload = run_session_change_report(
            {
                "files": [
                    {
                        "path": "src/auth/oauth.ts",
                        "status": "modified",
                        "line_ranges": ["new 44-58"],
                        "summary": "补上 callback 参数校验并统一错误返回",
                        "snippets": [
                            "if (!code) {",
                            "return reply.status(400).send({ error: 'missing code' })",
                        ],
                        "confidence": "high",
                    },
                    {
                        "path": "docs/oauth-notes.md",
                        "status": "session-mentioned",
                        "summary": "记录了为什么暂时不接 ngrok",
                        "confidence": "medium",
                    },
                ]
            }
        )

        self.assertEqual(code, 0)
        self.assertTrue(payload["has_changes"])
        self.assertEqual(payload["evidence_source"], "session-derived")
        self.assertIn("`src/auth/oauth.ts`", payload["markdown"])
        self.assertIn("Confidence: `high`", payload["markdown"])
        self.assertIn("`new 44-58`", payload["markdown"])
        self.assertIn("callback 参数校验", payload["markdown"])
        self.assertIn("`docs/oauth-notes.md`", payload["markdown"])
        self.assertIn("Confidence: `medium`", payload["markdown"])

    def test_session_change_report_handles_empty_payload(self) -> None:
        code, payload = run_session_change_report({"files": []})

        self.assertEqual(code, 0)
        self.assertFalse(payload["has_changes"])
        self.assertEqual(payload["files"], [])
        self.assertIn(
            "No session-derived file changes were captured.",
            payload["markdown"],
        )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "handoff.py"


def run_handoff(*args: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stdout)
    return result.returncode, payload


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


if __name__ == "__main__":
    unittest.main()

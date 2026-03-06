import sys
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.git_workflow import (
    build_cycle_commit_message,
    commit_all_changes,
    ensure_clean_git,
    get_changed_paths,
    has_code_changes,
)


class GitWorkflowTests(unittest.TestCase):
    def test_ensure_clean_git_raises_for_dirty_worktree(self) -> None:
        with patch(
            "app.git_workflow._run_git",
            return_value=CompletedProcess(
                args=["git", "status", "--short"],
                returncode=0,
                stdout=" M app/main.py\n?? tests/test_git_workflow.py\n",
                stderr="",
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "Git worktree is dirty"):
                ensure_clean_git(Path("."))

    def test_get_changed_paths_parses_renames_and_untracked_files(self) -> None:
        with patch(
            "app.git_workflow._run_git",
            return_value=CompletedProcess(
                args=["git", "status", "--short"],
                returncode=0,
                stdout="R  tasks/009-old.md -> completed_tasks/009-add-commit-system.md\n?? app/git_workflow.py\n",
                stderr="",
            ),
        ):
            changed_paths = get_changed_paths(Path("."))

        self.assertEqual(
            changed_paths,
            ["app/git_workflow.py", "completed_tasks/009-add-commit-system.md"],
        )

    def test_has_code_changes_only_counts_python_code_paths(self) -> None:
        self.assertTrue(has_code_changes(["app/main.py"]))
        self.assertTrue(has_code_changes(["tests/test_git_workflow.py"]))
        self.assertFalse(has_code_changes(["tasks/009-add-commit-system.md"]))

    def test_build_cycle_commit_message_uses_completed_task_slug_when_available(self) -> None:
        message = build_cycle_commit_message(["009-add-commit-system.md"])
        self.assertEqual(message, "chore(evolvo): complete add commit system")

    def test_commit_all_changes_runs_add_then_commit(self) -> None:
        calls: list[list[str]] = []

        def fake_run_git(root: Path, args: list[str]) -> CompletedProcess[str]:
            calls.append(args)
            return CompletedProcess(args=["git", *args], returncode=0, stdout="", stderr="")

        with patch("app.git_workflow._run_git", side_effect=fake_run_git):
            commit_all_changes(Path("."), "chore(evolvo): complete approved task cycle")

        self.assertEqual(
            calls,
            [["add", "-A"], ["commit", "-m", "chore(evolvo): complete approved task cycle"]],
        )


if __name__ == "__main__":
    unittest.main()

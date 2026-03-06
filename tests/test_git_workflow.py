import sys
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.git_workflow import (
    PullRequestInfo,
    _build_github_auth_env,
    _origin_https_extraheader,
    build_cycle_commit_message,
    build_pull_request_title,
    build_review_fix_commit_message,
    build_task_branch_name,
    commit_all_changes,
    create_task_branch,
    ensure_clean_git,
    ensure_on_main_branch,
    ensure_pull_request,
    get_changed_paths,
    get_current_branch,
    has_code_changes,
    merge_pull_request,
    push_branch,
    submit_pull_request_review,
    sync_main_branch,
)


class GitWorkflowTests(unittest.TestCase):
    def test_build_github_auth_env_uses_pat_from_environment(self) -> None:
        with patch.dict("os.environ", {"GITHUB_PAT": "pat-123"}, clear=True):
            env = _build_github_auth_env()

        self.assertEqual(env["GH_TOKEN"], "pat-123")
        self.assertEqual(env["GITHUB_TOKEN"], "pat-123")

    def test_origin_https_extraheader_uses_token_for_https_remote(self) -> None:
        with patch.dict("os.environ", {"GITHUB_PAT": "pat-123"}, clear=True):
            with patch(
                "app.git_workflow.subprocess.run",
                return_value=CompletedProcess(
                    args=["git", "remote", "get-url", "origin"],
                    returncode=0,
                    stdout="https://github.com/evolvo-auto/evolvo-python.git\n",
                    stderr="",
                ),
            ):
                header = _origin_https_extraheader(Path("."))

        self.assertTrue(header is not None)
        self.assertIn("http.https://github.com/.extraheader=AUTHORIZATION: basic ", header)

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

    def test_build_review_fix_commit_message_uses_task_slug(self) -> None:
        message = build_review_fix_commit_message("009-add-commit-system.md")
        self.assertEqual(
            message,
            "chore(evolvo): address review feedback for add commit system",
        )

    def test_build_task_branch_name_uses_task_filename(self) -> None:
        branch_name = build_task_branch_name("009-add-commit-system.md")
        self.assertEqual(branch_name, "evolvo/009-add-commit-system")

    def test_build_pull_request_title_uses_task_filename(self) -> None:
        title = build_pull_request_title("009-add-commit-system.md")
        self.assertEqual(title, "Task 009: add commit system")

    def test_get_current_branch_reads_git_output(self) -> None:
        with patch(
            "app.git_workflow._run_git",
            return_value=CompletedProcess(
                args=["git", "branch", "--show-current"],
                returncode=0,
                stdout="main\n",
                stderr="",
            ),
        ):
            branch = get_current_branch(Path("."))

        self.assertEqual(branch, "main")

    def test_ensure_on_main_branch_raises_for_non_main_branch(self) -> None:
        with patch(
            "app.git_workflow._run_git",
            return_value=CompletedProcess(
                args=["git", "branch", "--show-current"],
                returncode=0,
                stdout="feature/task\n",
                stderr="",
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "Expected to start on main"):
                ensure_on_main_branch(Path("."))

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

    def test_create_task_branch_runs_checkout_from_main(self) -> None:
        calls: list[list[str]] = []

        def fake_run_git(root: Path, args: list[str]) -> CompletedProcess[str]:
            calls.append(args)
            return CompletedProcess(args=["git", *args], returncode=0, stdout="", stderr="")

        with patch("app.git_workflow._run_git", side_effect=fake_run_git):
            create_task_branch(Path("."), "evolvo/009-add-commit-system")

        self.assertEqual(calls, [["checkout", "-b", "evolvo/009-add-commit-system", "main"]])

    def test_push_branch_sets_upstream(self) -> None:
        calls: list[tuple[list[str], dict[str, str] | None]] = []

        def fake_subprocess_run(*args, **kwargs) -> CompletedProcess[str]:
            command = list(args[0])
            calls.append((command, kwargs.get("env")))
            if command[:4] == ["git", "remote", "get-url", "origin"]:
                return CompletedProcess(
                    args=command,
                    returncode=0,
                    stdout="https://github.com/evolvo-auto/evolvo-python.git\n",
                    stderr="",
                )
            return CompletedProcess(args=command, returncode=0, stdout="", stderr="")

        with patch.dict("os.environ", {"GITHUB_PAT": "pat-123"}, clear=True):
            with patch("app.git_workflow.subprocess.run", side_effect=fake_subprocess_run):
                push_branch(Path("."), "evolvo/009-add-commit-system")

        self.assertEqual(calls[1][0][:3], ["git", "-c", calls[1][0][2]])
        self.assertIn("http.https://github.com/.extraheader=AUTHORIZATION: basic ", calls[1][0][2])
        self.assertEqual(
            calls[1][0][3:],
            ["push", "--set-upstream", "origin", "evolvo/009-add-commit-system"],
        )
        self.assertEqual(calls[1][1]["GH_TOKEN"], "pat-123")

    def test_ensure_pull_request_creates_when_missing(self) -> None:
        gh_calls: list[list[str]] = []

        def fake_run_gh(root: Path, args: list[str]) -> CompletedProcess[str]:
            gh_calls.append(args)
            if args[:3] == ["pr", "view", "evolvo/009-add-commit-system"] and len(gh_calls) == 1:
                return CompletedProcess(
                    args=["gh", *args],
                    returncode=1,
                    stdout="",
                    stderr="not found",
                )
            if args[:3] == ["pr", "view", "evolvo/009-add-commit-system"]:
                return CompletedProcess(
                    args=["gh", *args],
                    returncode=0,
                    stdout='{"number": 12, "url": "https://github.com/example/repo/pull/12"}',
                    stderr="",
                )
            return CompletedProcess(
                args=["gh", *args],
                returncode=0,
                stdout="https://github.com/example/repo/pull/12\n",
                stderr="",
            )

        with patch("app.git_workflow._run_gh", side_effect=fake_run_gh):
            pr = ensure_pull_request(
                Path("."),
                "evolvo/009-add-commit-system",
                "Task 009: add commit system",
                "body",
            )

        self.assertEqual(
            pr,
            PullRequestInfo(12, "https://github.com/example/repo/pull/12", "evolvo/009-add-commit-system"),
        )
        self.assertEqual(
            gh_calls,
            [
                ["pr", "view", "evolvo/009-add-commit-system", "--json", "number,url"],
                [
                    "pr",
                    "create",
                    "--base",
                    "main",
                    "--head",
                    "evolvo/009-add-commit-system",
                    "--title",
                    "Task 009: add commit system",
                    "--body",
                    "body",
                ],
                ["pr", "view", "evolvo/009-add-commit-system", "--json", "number,url"],
            ],
        )

    def test_ensure_pull_request_edits_when_existing(self) -> None:
        gh_calls: list[list[str]] = []

        def fake_run_gh(root: Path, args: list[str]) -> CompletedProcess[str]:
            gh_calls.append(args)
            if args[:3] == ["pr", "view", "evolvo/009-add-commit-system"]:
                return CompletedProcess(
                    args=["gh", *args],
                    returncode=0,
                    stdout='{"number": 12, "url": "https://github.com/example/repo/pull/12"}',
                    stderr="",
                )
            return CompletedProcess(args=["gh", *args], returncode=0, stdout="", stderr="")

        with patch("app.git_workflow._run_gh", side_effect=fake_run_gh):
            pr = ensure_pull_request(
                Path("."),
                "evolvo/009-add-commit-system",
                "Task 009: add commit system",
                "body",
            )

        self.assertEqual(pr.number, 12)
        self.assertEqual(
            gh_calls,
            [
                ["pr", "view", "evolvo/009-add-commit-system", "--json", "number,url"],
                ["pr", "edit", "12", "--title", "Task 009: add commit system", "--body", "body"],
            ],
        )

    def test_submit_pull_request_review_uses_comment_only_reviews(self) -> None:
        gh_calls: list[tuple[list[str], dict[str, str] | None]] = []

        def fake_subprocess_run(*args, **kwargs) -> CompletedProcess[str]:
            command = list(args[0])
            gh_calls.append((command, kwargs.get("env")))
            return CompletedProcess(args=command, returncode=0, stdout="", stderr="")

        with patch.dict("os.environ", {"GITHUB_PAT": "pat-123"}, clear=True):
            with patch("app.git_workflow.subprocess.run", side_effect=fake_subprocess_run):
                submit_pull_request_review(Path("."), 12, approved=False, body="REVISE: fix it")
                submit_pull_request_review(Path("."), 12, approved=True, body="APPROVED: ready")

        self.assertEqual(
            [call[0][1:] for call in gh_calls],
            [
                ["pr", "review", "12", "--comment", "--body", "REVISE: fix it"],
                ["pr", "review", "12", "--comment", "--body", "APPROVED: ready"],
            ],
        )
        self.assertEqual(gh_calls[0][1]["GH_TOKEN"], "pat-123")

    def test_merge_and_sync_main_run_expected_commands(self) -> None:
        gh_calls: list[list[str]] = []
        git_calls: list[list[str]] = []

        def fake_run_gh(root: Path, args: list[str]) -> CompletedProcess[str]:
            gh_calls.append(args)
            return CompletedProcess(args=["gh", *args], returncode=0, stdout="", stderr="")

        def fake_run_git(root: Path, args: list[str]) -> CompletedProcess[str]:
            git_calls.append(args)
            return CompletedProcess(args=["git", *args], returncode=0, stdout="", stderr="")

        with patch("app.git_workflow._run_gh", side_effect=fake_run_gh):
            with patch("app.git_workflow._run_git", side_effect=fake_run_git):
                merge_pull_request(Path("."), 12)
                sync_main_branch(Path("."))

        self.assertEqual(gh_calls, [["pr", "merge", "12", "--squash", "--delete-branch"]])
        self.assertEqual(
            git_calls,
            [["checkout", "main"], ["pull", "--ff-only", "origin", "main"]],
        )


if __name__ == "__main__":
    unittest.main()

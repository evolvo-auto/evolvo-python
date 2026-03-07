import base64
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

try:
    from .conventional_commit import build_conventional_commit_message
except ImportError:
    from conventional_commit import build_conventional_commit_message


@dataclass
class PullRequestInfo:
    number: int
    url: str
    branch: str


@dataclass
class BranchDiffSummary:
    changed_files: list[str]
    diff_stat: str
    diff_patch: str


def _get_github_token() -> str | None:
    for key in ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_PAT"):
        value = os.environ.get(key)
        if value:
            return value
    return None


def _build_github_auth_env() -> dict[str, str]:
    env = os.environ.copy()
    token = _get_github_token()
    if token:
        env["GH_TOKEN"] = token
        env["GITHUB_TOKEN"] = token
    return env


def _origin_https_extraheader(root: Path) -> str | None:
    token = _get_github_token()
    if not token:
        return None

    remote_result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        env=_build_github_auth_env(),
    )
    if remote_result.returncode != 0:
        return None

    remote_url = remote_result.stdout.strip()
    if not remote_url.startswith("https://"):
        return None

    host = remote_url.split("/", 3)[2]
    auth_value = base64.b64encode(f"x-access-token:{token}".encode("utf-8")).decode("ascii")
    return f"http.https://{host}/.extraheader=AUTHORIZATION: basic {auth_value}"


def _run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    command = ["git", *args]
    extraheader = _origin_https_extraheader(root)
    if extraheader and args and args[0] in {"fetch", "pull", "push", "ls-remote"}:
        command = ["git", "-c", extraheader, *args]

    return subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        env=_build_github_auth_env(),
    )


def _run_gh(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        env=_build_github_auth_env(),
    )


def get_git_status_lines(root: Path) -> list[str]:
    result = _run_git(root, ["status", "--short"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git status failed")
    return [line for line in result.stdout.splitlines() if line.strip()]


def ensure_clean_git(root: Path) -> None:
    status_lines = get_git_status_lines(root)
    if status_lines:
        details = "\n".join(status_lines)
        raise RuntimeError(f"Git worktree is dirty. Refusing to start a run.\n{details}")


def get_current_branch(root: Path) -> str:
    result = _run_git(root, ["branch", "--show-current"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git branch --show-current failed")
    return result.stdout.strip()


def ensure_on_main_branch(root: Path, base_branch: str = "main") -> None:
    current_branch = get_current_branch(root)
    if current_branch != base_branch:
        raise RuntimeError(
            f"Expected to start on {base_branch}, found {current_branch}. Refusing to start a run."
        )


def _parse_status_path(line: str) -> str:
    path_text = line[3:].strip()
    if " -> " in path_text:
        return path_text.split(" -> ", 1)[1].strip()
    return path_text


def get_changed_paths(root: Path) -> list[str]:
    return sorted(_parse_status_path(line) for line in get_git_status_lines(root))


def _truncate_text(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    truncated_chars = len(value) - limit
    return f"{value[:limit]}\n\n[truncated {truncated_chars} characters]"


def get_branch_diff_summary(
    root: Path,
    base_ref: str = "main",
    head_ref: str = "HEAD",
    max_patch_chars: int = 12000,
) -> BranchDiffSummary:
    diff_range = f"{base_ref}...{head_ref}"

    changed_files_result = _run_git(root, ["diff", "--name-only", diff_range])
    if changed_files_result.returncode != 0:
        raise RuntimeError(changed_files_result.stderr.strip() or "git diff --name-only failed")

    diff_stat_result = _run_git(root, ["diff", "--stat", diff_range])
    if diff_stat_result.returncode != 0:
        raise RuntimeError(diff_stat_result.stderr.strip() or "git diff --stat failed")

    diff_patch_result = _run_git(root, ["diff", "--unified=3", diff_range])
    if diff_patch_result.returncode != 0:
        raise RuntimeError(diff_patch_result.stderr.strip() or "git diff failed")

    changed_files = [
        line.strip()
        for line in changed_files_result.stdout.splitlines()
        if line.strip()
    ]
    diff_stat = diff_stat_result.stdout.strip() or "(no diff stat available)"
    diff_patch = _truncate_text(
        diff_patch_result.stdout.strip() or "(no diff patch available)",
        max_patch_chars,
    )

    return BranchDiffSummary(
        changed_files=changed_files,
        diff_stat=diff_stat,
        diff_patch=diff_patch,
    )


def has_code_changes(changed_paths: list[str]) -> bool:
    return any(
        (path.startswith("app/") or path.startswith("tests/")) and path.endswith(".py")
        for path in changed_paths
    )


def _task_slug_to_description(task_filename: str) -> str | None:
    stem = Path(task_filename).stem
    if "-" not in stem:
        return None
    slug = stem.split("-", 1)[1].replace("-", " ").strip().lower()
    if not slug:
        return None
    return f"complete {slug}"


def build_cycle_commit_message(completed_task_files: list[str]) -> str:
    if len(completed_task_files) == 1:
        description = _task_slug_to_description(completed_task_files[0])
        if description:
            return build_conventional_commit_message("chore", "evolvo", description)

    return build_conventional_commit_message(
        "chore",
        "evolvo",
        "complete approved task cycle",
    )


def build_review_fix_commit_message(task_filename: str) -> str:
    description = _task_slug_to_description(task_filename)
    if description:
        suffix = description.removeprefix("complete ")
        return build_conventional_commit_message(
            "chore",
            "evolvo",
            f"address review feedback for {suffix}",
        )

    return build_conventional_commit_message(
        "chore",
        "evolvo",
        "address review feedback",
    )


def build_task_branch_name(task_filename: str) -> str:
    stem = Path(task_filename).stem.lower()
    safe = "".join(ch if ch.isalnum() or ch == "-" else "-" for ch in stem)
    safe = "-".join(part for part in safe.split("-") if part)
    if not safe:
        raise ValueError("task filename must contain a usable branch slug")
    return f"evolvo/{safe}"


def build_pull_request_title(task_filename: str) -> str:
    stem = Path(task_filename).stem
    if "-" in stem:
        task_id, slug = stem.split("-", 1)
        return f"Task {task_id}: {slug.replace('-', ' ')}"
    return f"Task: {stem}"


def commit_all_changes(root: Path, message: str) -> None:
    add_result = _run_git(root, ["add", "-A"])
    if add_result.returncode != 0:
        raise RuntimeError(add_result.stderr.strip() or "git add failed")

    commit_result = _run_git(root, ["commit", "-m", message])
    if commit_result.returncode != 0:
        raise RuntimeError(commit_result.stderr.strip() or "git commit failed")


def create_task_branch(root: Path, branch_name: str, base_branch: str = "main") -> None:
    result = _run_git(root, ["checkout", "-b", branch_name, base_branch])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git checkout -b failed")


def push_branch(root: Path, branch_name: str) -> None:
    result = _run_git(root, ["push", "--set-upstream", "origin", branch_name])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git push failed")


def _load_pull_request_info(raw: str, branch_name: str) -> PullRequestInfo:
    payload = json.loads(raw)
    return PullRequestInfo(
        number=int(payload["number"]),
        url=str(payload["url"]),
        branch=branch_name,
    )


def get_pull_request(root: Path, branch_name: str) -> PullRequestInfo | None:
    result = _run_gh(root, ["pr", "view", branch_name, "--json", "number,url"])
    if result.returncode != 0:
        return None
    return _load_pull_request_info(result.stdout, branch_name)


def ensure_pull_request(
    root: Path,
    branch_name: str,
    title: str,
    body: str,
    base_branch: str = "main",
) -> PullRequestInfo:
    existing = get_pull_request(root, branch_name)
    if existing is not None:
        edit_result = _run_gh(
            root,
            [
                "pr",
                "edit",
                str(existing.number),
                "--title",
                title,
                "--body",
                body,
            ],
        )
        if edit_result.returncode != 0:
            raise RuntimeError(edit_result.stderr.strip() or "gh pr edit failed")
        return existing

    create_result = _run_gh(
        root,
        [
            "pr",
            "create",
            "--base",
            base_branch,
            "--head",
            branch_name,
            "--title",
            title,
            "--body",
            body,
        ],
    )
    if create_result.returncode != 0:
        raise RuntimeError(create_result.stderr.strip() or "gh pr create failed")

    created = get_pull_request(root, branch_name)
    if created is None:
        raise RuntimeError("gh pr create succeeded but the pull request could not be resolved")
    return created


def submit_pull_request_review(
    root: Path,
    pr_number: int,
    approved: bool,
    body: str,
) -> None:
    review_body = body
    if approved and not body.lstrip().upper().startswith("APPROVED:"):
        review_body = f"APPROVED: {body}"
    if not approved and not body.lstrip().upper().startswith("REVISE:"):
        review_body = f"REVISE: {body}"

    result = _run_gh(
        root,
        ["pr", "review", str(pr_number), "--comment", "--body", review_body],
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gh pr review failed")


def merge_pull_request(root: Path, pr_number: int) -> None:
    result = _run_gh(root, ["pr", "merge", str(pr_number), "--squash", "--delete-branch"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gh pr merge failed")


def sync_main_branch(root: Path, base_branch: str = "main") -> None:
    checkout_result = _run_git(root, ["checkout", base_branch])
    if checkout_result.returncode != 0:
        raise RuntimeError(checkout_result.stderr.strip() or "git checkout main failed")

    pull_result = _run_git(root, ["pull", "--ff-only", "origin", base_branch])
    if pull_result.returncode != 0:
        raise RuntimeError(pull_result.stderr.strip() or "git pull failed")

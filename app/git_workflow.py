import subprocess
from pathlib import Path

try:
    from .conventional_commit import build_conventional_commit_message
except ImportError:
    from conventional_commit import build_conventional_commit_message


def _run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
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


def _parse_status_path(line: str) -> str:
    path_text = line[3:].strip()
    if " -> " in path_text:
        return path_text.split(" -> ", 1)[1].strip()
    return path_text


def get_changed_paths(root: Path) -> list[str]:
    return sorted(_parse_status_path(line) for line in get_git_status_lines(root))


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


def commit_all_changes(root: Path, message: str) -> None:
    add_result = _run_git(root, ["add", "-A"])
    if add_result.returncode != 0:
        raise RuntimeError(add_result.stderr.strip() or "git add failed")

    commit_result = _run_git(root, ["commit", "-m", message])
    if commit_result.returncode != 0:
        raise RuntimeError(commit_result.stderr.strip() or "git commit failed")

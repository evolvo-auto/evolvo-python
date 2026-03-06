from pathlib import Path


def select_pending_task(tasks_dir: Path) -> Path:
    """Return one pending task markdown file using deterministic ordering.

    Args:
        tasks_dir: Directory containing pending task markdown files.

    Returns:
        The lexicographically first `.md` file in `tasks_dir`.

    Raises:
        FileNotFoundError: If `tasks_dir` does not exist.
        ValueError: If there are no markdown task files to select.
    """
    if not tasks_dir.exists():
        raise FileNotFoundError(f"Tasks directory does not exist: {tasks_dir}")

    task_files = sorted(path for path in tasks_dir.glob("*.md") if path.is_file())
    if not task_files:
        raise ValueError(f"No pending markdown task files found in: {tasks_dir}")

    return task_files[0]

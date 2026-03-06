from pathlib import Path


def count_task_markdown_files(tasks_dir: Path, completed_tasks_dir: Path) -> tuple[int, int]:
    pending_count = sum(1 for path in tasks_dir.glob("*.md") if path.is_file())
    completed_count = sum(1 for path in completed_tasks_dir.glob("*.md") if path.is_file())
    return pending_count, completed_count


def list_task_markdown_files(tasks_dir: Path) -> list[str]:
    """Return sorted markdown task filenames from a task directory."""
    return sorted(path.name for path in tasks_dir.glob("*.md") if path.is_file())

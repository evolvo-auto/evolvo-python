from pathlib import Path

try:
    from ..task_file_counts import list_task_markdown_files
except ImportError:
    from task_file_counts import list_task_markdown_files


def collect_task_ids(directory: Path) -> set[str]:
    if not directory.exists():
        return set()

    ids: set[str] = set()
    for path in directory.glob("*.md"):
        prefix = path.name.split("-", 1)[0]
        if prefix.isdigit():
            ids.add(prefix)
    return ids


def summarize_task_reconciliation(root: Path) -> dict[str, list[str]]:
    tasks_ids = collect_task_ids(root / "tasks")
    completed_ids = collect_task_ids(root / "completed_tasks")
    overlap = sorted(tasks_ids & completed_ids)
    only_completed = sorted(completed_ids - tasks_ids)
    only_tasks = sorted(tasks_ids - completed_ids)
    return {
        "overlap_ids": overlap,
        "only_in_completed_ids": only_completed,
        "only_in_tasks_ids": only_tasks,
    }


def snapshot_completed_tasks(root: Path) -> set[str]:
    completed_dir = root / "completed_tasks"
    if not completed_dir.exists():
        return set()
    return set(list_task_markdown_files(completed_dir))


def list_pending_tasks(root: Path) -> list[str]:
    tasks_dir = root / "tasks"
    if not tasks_dir.exists():
        return []
    return list_task_markdown_files(tasks_dir)


def mark_task_failed(root: Path, task_file: Path, reason: str) -> Path:
    failed_dir = root / "failed_tasks"
    failed_dir.mkdir(parents=True, exist_ok=True)

    failure_note = f"\n\n## Failure\n{reason.strip()}\n"
    current_content = task_file.read_text(encoding="utf-8")
    if "## Failure" not in current_content:
        task_file.write_text(current_content.rstrip() + failure_note, encoding="utf-8")

    destination = failed_dir / task_file.name
    task_file.rename(destination)
    return destination

from pathlib import Path

try:
    from ..task_bootstrap_generator import create_task_file
    from ..task_file_counts import list_task_markdown_files
except ImportError:
    from task_bootstrap_generator import create_task_file
    from task_file_counts import list_task_markdown_files
def list_pending_tasks(root: Path) -> list[str]:
    tasks_dir = root / "tasks"
    if not tasks_dir.exists():
        return []
    return list_task_markdown_files(tasks_dir)


def ensure_minimum_pending_tasks(root: Path, minimum: int = 3) -> list[str]:
    tasks_dir = root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    pending = list_task_markdown_files(tasks_dir)
    while len(pending) < minimum:
        create_task_file(
            tasks_dir=tasks_dir,
            title=f"bootstrap-generated-task-{len(pending) + 1}",
            goal="Created automatically to satisfy minimum pending task requirements.",
        )
        pending = list_task_markdown_files(tasks_dir)
    return pending

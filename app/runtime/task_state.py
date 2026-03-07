from pathlib import Path

try:
    from ..task_file_counts import list_task_markdown_files
    from ..tools.github.issues.create import create_issue
except ImportError:
    from task_file_counts import list_task_markdown_files
    from tools.github.issues.create import create_issue
def list_pending_tasks(root: Path) -> list[str]:
    tasks_dir = root / "tasks"
    if not tasks_dir.exists():
        return []
    return list_task_markdown_files(tasks_dir)


def create_task_file_with_issue(root: Path, filename: str, content: str) -> Path:
    tasks_dir = root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    task_path = tasks_dir / filename
    task_path.write_text(content, encoding="utf-8")
    create_issue(content)
    return task_path

import re
from pathlib import Path


TASK_TEMPLATE = """# Task: {task_id}: {title}

## Goal
{goal}

## Scope
- Define concrete implementation steps.
- Add or update tests as needed.
- Keep changes focused and reviewable.

## Acceptance Criteria
- Implementation is complete and locally validated.
- Tests cover the intended behavior.
- Existing behavior remains backward compatible unless explicitly changed.
"""


def slugify_title(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", title.strip().lower())
    return normalized.strip("-") or "task"


def next_task_id(tasks_dir: Path) -> str:
    max_id = 0
    if tasks_dir.exists():
        for path in tasks_dir.glob("*.md"):
            prefix = path.name.split("-", 1)[0]
            if prefix.isdigit():
                max_id = max(max_id, int(prefix))
    return f"{max_id + 1:03d}"


def generate_task_markdown(task_id: str, title: str, goal: str | None = None) -> str:
    safe_goal = goal or "Describe the intended improvement and expected impact."
    return TASK_TEMPLATE.format(task_id=task_id, title=title, goal=safe_goal)


def create_task_file(tasks_dir: Path, title: str, goal: str | None = None) -> Path:
    tasks_dir.mkdir(parents=True, exist_ok=True)
    task_id = next_task_id(tasks_dir)
    filename = f"{task_id}-{slugify_title(title)}.md"
    destination = tasks_dir / filename
    destination.write_text(
        generate_task_markdown(task_id=task_id, title=title, goal=goal),
        encoding="utf-8",
    )
    return destination

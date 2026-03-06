import os
import asyncio
from pathlib import Path
async def main() -> None:
        await asyncio.sleep(2)


def _collect_task_ids(directory: Path) -> set[str]:
    if not directory.exists():
        return set()
    ids: set[str] = set()
    for path in directory.glob("*.md"):
        prefix = path.name.split("-", 1)[0]
        if prefix.isdigit():
            ids.add(prefix)
    return ids


def summarize_task_reconciliation(root: Path) -> dict[str, list[str]]:
    tasks_ids = _collect_task_ids(root / "tasks")
    completed_ids = _collect_task_ids(root / "completed_tasks")
    overlap = sorted(tasks_ids & completed_ids)
    only_completed = sorted(completed_ids - tasks_ids)
    only_tasks = sorted(tasks_ids - completed_ids)
    return {
        "overlap_ids": overlap,
        "only_in_completed_ids": only_completed,
        "only_in_tasks_ids": only_tasks,
    }

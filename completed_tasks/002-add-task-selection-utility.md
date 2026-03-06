## Acceptance criteria
- Utility function added under `app/` that lists `.md` files in `tasks/`.
- Selection strategy is deterministic (e.g., lexicographic first).
- Function includes docstring and basic error handling for empty task lists.

## Reflection
- Added `app/task_selection.py` with `select_pending_task(tasks_dir: Path) -> Path`.
- Implemented deterministic selection by sorting `*.md` files lexicographically and returning the first.
- Added explicit error handling for missing `tasks/` directory and empty task list, plus a docstring describing behavior.

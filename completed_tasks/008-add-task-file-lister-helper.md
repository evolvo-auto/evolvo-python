## Acceptance criteria
- Add a helper in `app/task_file_counts.py` to list task markdown filenames from a directory.
- Helper returns deterministic ordering (alphabetical).
- Add or update tests to validate returned filenames and ordering.

## Reflection
- Added `list_task_markdown_files(tasks_dir: Path) -> list[str]` to `app/task_file_counts.py`.
- Implemented deterministic alphabetical ordering by returning a sorted filename list.
- Updated `tests/test_task_file_counts.py` with a focused test that verifies only `*.md` files are returned and that ordering is alphabetical.

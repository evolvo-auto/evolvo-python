## Acceptance criteria
- A helper function under `app/` returns counts of `*.md` files for `tasks/` and `completed_tasks/`.
- Function has a docstring and uses `pathlib`.
- No behavior changes outside introducing the helper.

## Reflection
- Added `app/task_file_counts.py` with `count_task_markdown_files(tasks_dir, completed_tasks_dir)`.
- Implemented counting for `*.md` files in both directories using `pathlib.Path.glob`.
- Kept the change isolated to introducing the helper module, with no runtime behavior changes.

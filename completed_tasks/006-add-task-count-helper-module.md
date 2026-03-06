## Task: Add helper to count task markdown files
- A helper function under `app/` returns counts of `*.md` files for `tasks/` and `completed_tasks/`.
- Function has a docstring and uses `pathlib`.
- No behavior changes outside introducing the helper.

## Reflection
- Verified existing helper implementation in `app/task_file_counts.py`.
- Confirmed it counts only `*.md` files in both `tasks/` and `completed_tasks/` using `pathlib.Path.glob`.
- The helper is currently unused; a follow-up task should integrate it into runtime status output.

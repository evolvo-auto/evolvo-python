## Acceptance Criteria
- Helper is implemented in `app/`.
- At least one test verifies valid and invalid task files.

## Reflection
- Added `app/task_file_validation.py` with a `validate_task_file(task_file)` helper that checks required markdown headers.
- Integrated validation into `app/main.py` so the active task is checked before branch work begins.
- Added `tests/test_task_file_validation.py` covering both valid and invalid task file content.
- Attempted to run tests, but `pytest` is not installed in the current virtual environment (`No module named pytest`).

## Acceptance Criteria
- When the bot creates a new task, it also calls `create_issue(content: str)` to create a GitHub issue in the `evolvo-python` repository.
- The created issue content reflects the created task (for example, task title or task summary).
- If issue creation fails, the failure is surfaced clearly without silently passing.
- Relevant tests exist and validate both the success path and failure handling for this integration.
- No unrelated code changes are made in the repository.

## Reflection
- Added `create_task_file_with_issue` in `app/runtime/task_state.py` to centralize task file creation plus GitHub issue creation using existing `create_issue(content: str)` utility.
- Kept behavior minimal and explicit: write task file, call `create_issue`, and let any exception bubble so failures are surfaced.
- Added focused tests in `tests/test_task_issue_integration.py` to validate:
  - success path (task file written + issue creation called with full task content),
  - failure path (issue creation error is raised to caller).
- Ran quality checks for changed Python code:
  - `.venv/bin/python -m ruff check app tests`
  - `.venv/bin/python -m pytest -x -vv tests/test_task_issue_integration.py`

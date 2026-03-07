# Task 016: Add support for listing GitHub issues

## Scope
- Add a new utility in `/app/tools/github/issues.py`.
- Expose a `list_issues()` function.
- Add a corresponding test file for this utility.
- Keep the change minimal and do not integrate this function into existing runtime flows yet.
- Limit changes strictly to what is needed for this task.

## Acceptance Criteria
- `/app/tools/github/issues.py` exists and exposes a `list_issues()` function.
- Running `list_issues()` returns the issues for the `evolvo-python` repository.
- A relevant test file exists and validates the new utility behavior.
- Behavior remains minimal and backward compatible with the existing project structure.
- No other unrelated code changes are made in the repository.
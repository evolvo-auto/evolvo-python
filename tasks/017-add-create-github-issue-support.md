# Task 017: Add support for creating a GitHub issue

## Scope
- Add a new utility in `/app/tools/github/issues/create.py`.
- Expose a `create_issue(content: str)` function.
- Take heavy inspiration from `/app/tools/github/issues/list.py`.
- Add a corresponding test file for this utility.
- Keep the change minimal and do not integrate this function into existing runtime flows yet.
- Limit changes strictly to what is needed for this task.

## Acceptance Criteria
- `/app/tools/github/issues/create.py` exists and exposes a `create_issue(content: str)` function.
- Running `create_issue(content: str)` creates a new issue in the `evolvo-python` repository.
- A relevant test file exists and validates the new utility behavior.
- Behavior remains minimal and backward compatible with the existing project structure.
- No other unrelated code changes are made in the repository except for changing the md filesm that is allowed
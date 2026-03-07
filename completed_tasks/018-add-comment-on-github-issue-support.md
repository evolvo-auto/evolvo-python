- Behavior remains minimal and backward compatible with the existing project structure.
- No other unrelated code changes are made in the repository except for changing the md filesm that is allowed

## Reflection
- Restored `tests/test_github_issues.py` to a valid, importable module with correct structure and shared test helpers.
- Re-added coverage for existing `list_issues` and `create_issue` behaviors (filtering pull requests, empty-content validation, request/auth/json payload assertions).
- Kept the new `comment_on_issue` tests additive and focused on task 018 behavior.
- Verified module tests pass locally with:
  - `.venv/bin/python -m pytest -x -vv tests/test_github_issues.py`
  - `.venv/bin/python -m ruff check app tests`

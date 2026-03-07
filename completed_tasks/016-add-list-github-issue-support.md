## Acceptance Criteria
- `/app/tools/github/issues.py` exists and exposes a `list_issues()` function.
- Running `list_issues()` returns the issues for the `evolvo-python` repository.
- A relevant test file exists and validates the new utility behavior.
- Behavior remains minimal and backward compatible with the existing project structure.
- No other unrelated code changes are made in the repository.

## Reflection
- Added `app/tools/github/issues.py` with a minimal `list_issues()` helper that calls the GitHub REST issues endpoint for `paddyroddy/evolvo-python`.
- Added `tests/test_github_issues.py` to validate returned JSON parsing and list output behavior via a mocked HTTP response.
- Kept the implementation intentionally small and did not wire it into runtime flows yet, matching task scope.

# Task 019: Create a GitHub issue when creating a task

## Scope
- Integrate task creation flow so that creating a new task also creates a GitHub issue.
- Reuse the existing GitHub issue utility at `/app/tools/github/issues/create.py` instead of duplicating request logic.
- Ensure the GitHub issue title/content is derived from the created task in a minimal, predictable way.
- Add or update relevant tests to validate the integration behavior.
- Keep the change minimal and backward compatible with the existing project structure.

## Acceptance Criteria
- When the bot creates a new task, it also calls `create_issue(content: str)` to create a GitHub issue in the `evolvo-python` repository.
- The created issue content reflects the created task (for example, task title or task summary).
- If issue creation fails, the failure is surfaced clearly without silently passing.
- Relevant tests exist and validate both the success path and failure handling for this integration.
- No unrelated code changes are made in the repository.

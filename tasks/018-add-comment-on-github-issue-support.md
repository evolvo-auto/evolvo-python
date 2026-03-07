# Task 018: Add a utility to be able to create a github issue
## Acceptance criteria
- `/app/tools/github/issues.py` exists and exposes a `comment_on_issue(issue_id: str, content: str)` function.
- running the function comments on the correct issue with the desired content in the `evolvo-python` repository.
- Behavior remains minimal and backward compatible with existing project structure.
- do not integrate the function yet, just create it
- create and applicable test file
- No other code changes in the repo
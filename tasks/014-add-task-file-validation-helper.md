# Task: Add task file validation helper

## Why
Malformed task files can break automation. A small validator can ensure required sections exist before processing.

## Scope
- Add a helper that checks for required markdown headers.
- Expose a simple callable API suitable for use in `app/main.py`.

## Acceptance Criteria
- Helper is implemented in `app/`.
- At least one test verifies valid and invalid task files.

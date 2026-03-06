# Task 017: Add task lifecycle audit log for moves to completed

## Goal
Increase traceability by recording when tasks move from `./tasks/` to `./completed_tasks/` and what was changed during the run.

## Scope
- Add lightweight audit logging (e.g., append-only markdown or JSONL in repo).
- Capture task filename, timestamp, and key changed files for each completion event.
- Integrate logging into the task completion workflow.
- Add tests validating log entry creation and format.

## Acceptance Criteria
- Completing a task writes exactly one well-formed audit entry.
- Log includes task name, completion timestamp, and changed file list.
- Tests verify creation and schema of entries.
- No external services or secrets required.


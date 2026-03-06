# Task: Add tests for task selection utilities

## Why
Core task-selection helpers should be validated with unit tests to avoid regressions in the self-improvement loop.

## Scope
- Add tests covering deterministic selection behavior.
- Verify edge cases such as empty lists and already-completed task filtering (if supported).

## Acceptance Criteria
- New tests are added under `tests/`.
- Tests pass locally.

## Reflection
- Added unit tests for deterministic selection and edge cases (missing directory, no markdown files).
- Verified tests pass locally via unittest.

# Task: Add task selection utility for pending markdown tasks

## Goal
Implement a small utility function that selects exactly one pending task file from `./tasks/` in a deterministic way.

## Why this matters
Deterministic task selection reduces run-to-run ambiguity and makes the self-improvement loop easier to debug.

## Acceptance criteria
- Utility function added under `app/` that lists `.md` files in `tasks/`.
- Selection strategy is deterministic (e.g., lexicographic first).
- Function includes docstring and basic error handling for empty task lists.

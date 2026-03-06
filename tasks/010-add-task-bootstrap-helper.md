# Task: Add helper to bootstrap pending task files

## Goal
Create a small utility that ensures `./tasks/` contains at least a target number of markdown task files, creating placeholder tasks when needed.

## Why
The run policy requires at least 3 pending tasks before selecting one. A dedicated helper reduces repeated logic and makes this behavior testable.

## Requirements
- Add a focused module under `app/` for task bootstrapping.
- Implement a function that:
  - ensures `tasks/` exists
  - counts `*.md` task files
  - creates placeholder markdown tasks until the target count is met
- Keep behavior deterministic and simple.
- Do not modify unrelated orchestration code in this task.

## Completion criteria
- New helper module exists and is importable.
- Helper creates missing task files up to the target count.
- Existing tasks are not overwritten.

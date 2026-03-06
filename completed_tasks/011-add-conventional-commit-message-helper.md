# Task: Add conventional commit message helper

## Goal
Implement a small helper that builds valid conventional commit messages from `(type, scope, description)` inputs.

## Why
Task 009 needs commit messages with a consistent format. A helper centralizes validation and formatting.

## Requirements
- Add a module under `app/` with a function for formatting commit messages.
- Enforce basic rules:
  - non-empty type, scope, and description
  - lowercase description
  - no trailing period
- Return messages in `<type>(<scope>): <description>` form.

## Completion criteria
- Helper module exists and can be imported.
- Produces correctly formatted messages for valid input.
- Rejects invalid input with clear errors.


## Reflection
- Added app/conventional_commit.py with input validation and canonical formatting for conventional commit messages.
- Kept scope focused on reusable message construction logic for later commit-system integration.

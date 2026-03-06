# Task: 015: Fix `shell_excecutor.py` typo with backward-compatible import

## Goal
Improve code clarity by correcting the misspelled module name `shell_excecutor.py` to `shell_executor.py` without breaking existing imports.

## Scope
- Add a correctly named module at `app/shell_executor.py`.
- Keep compatibility for any existing references to `app/shell_excecutor.py`.
- Update internal imports to use the corrected module path where safe.
- Add/adjust tests to confirm both import paths continue to work.

## Acceptance Criteria
- `app/shell_executor.py` exists and exports the same public interface.
- Existing code and tests pass with the new import path.
- Legacy import path still works (deprecation-safe transition).
- No functional behavior change beyond naming/compatibility cleanup.


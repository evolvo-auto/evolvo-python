## Acceptance Criteria
- `app/shell_executor.py` exists and exports the same public interface.
- Existing code and tests pass with the new import path.
- Legacy import path still works (deprecation-safe transition).
- No functional behavior change beyond naming/compatibility cleanup.

## Reflection
- Restored runtime tool setup in `app/tools/agent_tools.py` (`workspace_dir`, `shell_tool`, `approvals`, `editor`, `apply_patch_tool`, and `agent_tools`) to remove the regression introduced previously.
- Updated `app/shell_executor.py` to support both package and top-level import contexts using a relative-import fallback pattern.
- Strengthened compatibility coverage in `tests/test_shell_executor_import_compat.py` to verify both imports are callable and reference the same exported function object.
- Verified required behavior with `pytest -q tests/test_shell_executor_import_compat.py` (passing).

# Task 016: Add bootstrap task template and generator helper

## Goal
Reduce manual effort and improve consistency when seeding `./tasks/` by introducing a small task-template generator utility.

## Scope
- Add a helper in `app/` to generate starter task markdown files from a template.
- Include deterministic numbering and title slugging.
- Wire helper usage into bootstrap flow (if aligned with existing orchestration).
- Add tests for numbering, slug format, and minimum-task creation behavior.

## Acceptance Criteria
- A reusable generator function exists and is unit-tested.
- Newly created tasks follow consistent filename and section structure.
- Bootstrap flow can create required minimum task files reliably.
- Existing behavior remains backward compatible.


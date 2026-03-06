# Task: Commit accepted changes with a conventional commit message

## Goal

After a task has been implemented, reviewed, and accepted, Evolvo must create a git commit for the specific file changes made in that task using a valid conventional commit message.

## Requirements

1. This must only happen **after**:
   - the task implementation is complete
   - the review phase returns `ACCEPT`
   - all approved patches have already been applied successfully

2. Evolvo must commit only the files relevant to the current task.
   - Do not stage unrelated modified files.
   - Prefer explicit file staging over broad staging.

3. The commit message must follow the **Conventional Commits** format.

## Conventional commit format

Use:

`<type>(<scope>): <description>`

Examples:
- `fix(main): handle missing task files after review`
- `refactor(run-loop): split implementation and review phases`
- `feat(tasks): add task completion reflection handling`
- `chore(logging): improve cycle status output`

## Type selection rules

Choose the most appropriate type:
- `feat` for new behavior or capability
- `fix` for bug fixes
- `refactor` for internal restructuring without changing intended behavior
- `test` for test-only changes
- `docs` for documentation-only changes
- `chore` for maintenance or non-functional repo/runtime updates

## Scope rules

The scope should reflect the main area changed, for example:
- `main`
- `run-loop`
- `tasks`
- `review`
- `shell`
- `tools`
- `workspace-editor`

## Description rules

- Keep it short and specific.
- Use lowercase.
- Do not end with a period.
- Describe the actual change made.

## Required behavior

After review is accepted:
1. identify the exact files changed for the task
2. stage only those files
3. generate an appropriate conventional commit message
4. create the git commit
5. verify the commit succeeded

## Validation

Before marking the task complete, verify:
- a commit was created successfully
- the working tree no longer contains those staged task changes
- the commit message matches conventional commit structure

## Constraints

- Do not commit if review result is `AMEND` or `REVERT`
- Do not use `git add .`
- Do not include unrelated files in the commit
- Do not create empty commits

## Completion criteria

This task is complete when accepted task changes are committed in git with a correct conventional commit message and the commit is verified.
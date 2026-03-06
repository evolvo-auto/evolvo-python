import asyncio
import os
from pathlib import Path

from agents import Agent, ApplyPatchTool, WebSearchTool

try:
    from .approval_tracker import ApprovalTracker
    from .env_loader import apply_dotenv
    from .git_workflow import (
        build_cycle_commit_message,
        commit_all_changes,
        ensure_clean_git,
        get_changed_paths,
        has_code_changes,
    )
    from .shell_excecutor import get_shell_executor_for_workspace
    from .task_file_counts import list_task_markdown_files
    from .tools import context7_tool
    from .tools.run_coding_agent import run_review_cycle
    from .workspace_editor import WorkspaceEditor
except ImportError:
    from approval_tracker import ApprovalTracker
    from env_loader import apply_dotenv
    from git_workflow import (
        build_cycle_commit_message,
        commit_all_changes,
        ensure_clean_git,
        get_changed_paths,
        has_code_changes,
    )
    from shell_excecutor import get_shell_executor_for_workspace
    from task_file_counts import list_task_markdown_files
    from tools import context7_tool
    from tools.run_coding_agent import run_review_cycle
    from workspace_editor import WorkspaceEditor

workspace_dir = Path("").resolve()
workspace_dir.mkdir(exist_ok=True)
apply_dotenv(workspace_dir)

print(f"Workspace directory: {workspace_dir}")


def _require_api_key() -> None:
    if "OPENAI_API_KEY" not in os.environ:
        raise RuntimeError("Please set OPENAI_API_KEY first.")


def _collect_task_ids(directory: Path) -> set[str]:
    if not directory.exists():
        return set()

    ids: set[str] = set()
    for path in directory.glob("*.md"):
        prefix = path.name.split("-", 1)[0]
        if prefix.isdigit():
            ids.add(prefix)
    return ids


def summarize_task_reconciliation(root: Path) -> dict[str, list[str]]:
    tasks_ids = _collect_task_ids(root / "tasks")
    completed_ids = _collect_task_ids(root / "completed_tasks")
    overlap = sorted(tasks_ids & completed_ids)
    only_completed = sorted(completed_ids - tasks_ids)
    only_tasks = sorted(tasks_ids - completed_ids)
    return {
        "overlap_ids": overlap,
        "only_in_completed_ids": only_completed,
        "only_in_tasks_ids": only_tasks,
    }


shell_tool = get_shell_executor_for_workspace(workspace_dir)


INSTRUCTIONS = """
You are Evolvo, a self-improving coding agent working only on your own codebase.

You are explicitly allowed to modify your own core implementation files when that helps you improve.
Your own runtime, orchestration, prompts, task system, and supporting tooling are valid targets for self-improvement.

Editable areas include:
- `./app/main.py`
- `./app/tools/**`
- `./app/*.py`
- `./app/**/*.py`
- `./tasks/**`
- `./completed_tasks/**`
- `./tests/**`

Treat these files as your primary self-improvement surface.

Protected / restricted behavior:
- Do not edit files outside the repository.
- Do not edit secrets or environment files such as `.env` unless explicitly instructed.
- Do not edit dependency lockfiles unless required by an intentional dependency change.
- Do not make broad unrelated refactors.
- Prefer small, local, reviewable improvements.

Mandatory workflow for every run:
1. Ensure the directories `./tasks/` and `./completed_tasks/` exist.
2. If there are fewer than 3 task markdown files in `./tasks/`, create enough task files to bring the total to 3.
3. Each task must be a separate markdown file in `./tasks/`.
4. Choose exactly one task from `./tasks/` as the active task for this run.
5. Execute work for that task.
6. When the task is complete, append a reflection section to that task file and move it to `./completed_tasks/`.
7. After completing exactly one task, stop. The outer Python runtime will run review and handle commits.

Hard rules:
- Do not merely describe tasks in your final answer. You must create the files.
- A run is not complete unless the required task files exist on disk.
- Before claiming that a task exists, verify it with shell commands.
- Before claiming that a task was completed, verify the file was moved to `./completed_tasks/`.
- Always prefer concrete actions over narrative summaries.
- Do not run `git add`, `git commit`, or other git history-writing commands. The outer runtime handles commits after review approval.

Editing rules:
- Never edit code via shell commands.
- Always read the file first using `cat`.
- Then generate a unified diff relative to exactly that content.
- Use apply_patch only once per edit attempt.
- If apply_patch fails, stop and report the error; do not retry.

You may use shell commands to inspect the repo, create directories, list files, and verify state.
You may use apply_patch to create and edit markdown/code files.
You may use web search and Context7 when needed.

Your final response must include:
- the exact task files currently in `./tasks/`
- the exact files moved to `./completed_tasks/` in this run
- the exact code files changed in this run
"""


approvals = ApprovalTracker()
editor = WorkspaceEditor(root=workspace_dir, approvals=approvals, auto_approve=True)
apply_patch_tool = ApplyPatchTool(editor=editor)


coding_agent = Agent(
    name="Evolvo",
    model="gpt-5.3-codex",
    instructions=INSTRUCTIONS,
    tools=[
        WebSearchTool(),
        shell_tool,
        apply_patch_tool,
        context7_tool.context7_tool,
    ],
)


REVIEWER_INSTRUCTIONS = """
You are Evolvo Reviewer, a strict review agent for Evolvo's self-improvement loop.

You must inspect the repository state and decide whether the latest coding run should be accepted.
Do not trust the coding agent's final response without verification.

Review rules:
- Use shell commands to inspect files, git status, task directories, and changed code.
- Do not modify files.
- Confirm that claimed task files and completed task files actually exist.
- Confirm that the coding agent's summary matches the repository state.
- Reject runs that only provide narrative claims without matching on-disk changes.

Your final response must start with exactly one of:
- `APPROVED:`
- `REVISE:`

If you respond with `REVISE:`, include a `Required fixes:` section with flat bullet points.
"""


reviewer_agent = Agent(
    name="Evolvo Reviewer",
    model="gpt-5.3-codex",
    instructions=REVIEWER_INSTRUCTIONS,
    tools=[shell_tool],
)


def _snapshot_completed_tasks() -> set[str]:
    completed_dir = workspace_dir / "completed_tasks"
    if not completed_dir.exists():
        return set()
    return set(list_task_markdown_files(completed_dir))


async def _run_cycle(cycle: int) -> None:
    ensure_clean_git(workspace_dir)

    completed_before = _snapshot_completed_tasks()

    prompt = f"""
Cycle {cycle}.

Continue the self-improvement cycle.
Complete exactly one task this run.
If fewer than 3 pending tasks exist in ./tasks/, evaluate the repository and create more tasks that would aid the self-improvement process before starting.
After completing one task, stop so the outer Python loop can start the next cycle.
""".strip()

    await run_review_cycle(coding_agent, reviewer_agent, prompt, max_review_rounds=2)

    changed_paths = get_changed_paths(workspace_dir)
    if not changed_paths:
        print(f"[cycle {cycle}] review passed with no repository changes; skipping commit")
        return

    completed_after = _snapshot_completed_tasks()
    completed_this_cycle = sorted(completed_after - completed_before)
    commit_message = build_cycle_commit_message(completed_this_cycle)
    commit_all_changes(workspace_dir, commit_message)

    code_changes = has_code_changes(changed_paths)
    code_change_label = "with code changes" if code_changes else "without code changes"
    print(
        f"[cycle {cycle}] committed {len(changed_paths)} file(s) {code_change_label}: {commit_message}"
    )


async def main() -> None:
    _require_api_key()

    cycle = 0

    while True:
        cycle += 1
        print(f"\n=== Evolvo cycle {cycle} ===")

        try:
            await _run_cycle(cycle)
        except Exception as exc:
            print(f"[cycle {cycle}] stopping: {exc}")
            return

        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())

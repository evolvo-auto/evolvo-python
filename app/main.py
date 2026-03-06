import asyncio
import os
from pathlib import Path

try:
    from .agent_roles.coding_agent import coding_agent
    from .agent_roles.review_agent import reviewer_agent
    from .env_loader import apply_dotenv
    from .git_workflow import (
        build_cycle_commit_message,
        build_pull_request_title,
        build_review_fix_commit_message,
        build_task_branch_name,
        commit_all_changes,
        create_task_branch,
        ensure_clean_git,
        ensure_on_main_branch,
        ensure_pull_request,
        get_changed_paths,
        has_code_changes,
        merge_pull_request,
        push_branch,
        submit_pull_request_review,
        sync_main_branch,
    )
    from .task_file_counts import list_task_markdown_files
    from .task_selection import select_pending_task
    from .tools.agent_tools import workspace_dir
    from .tools.run_coding_agent import run_agent, run_coding_agent
except ImportError:
    from agent_roles.coding_agent import coding_agent
    from agent_roles.review_agent import reviewer_agent
    from env_loader import apply_dotenv
    from git_workflow import (
        build_cycle_commit_message,
        build_pull_request_title,
        build_review_fix_commit_message,
        build_task_branch_name,
        commit_all_changes,
        create_task_branch,
        ensure_clean_git,
        ensure_on_main_branch,
        ensure_pull_request,
        get_changed_paths,
        has_code_changes,
        merge_pull_request,
        push_branch,
        submit_pull_request_review,
        sync_main_branch,
    )
    from task_file_counts import list_task_markdown_files
    from task_selection import select_pending_task
    from tools.agent_tools import workspace_dir
    from tools.run_coding_agent import run_agent, run_coding_agent

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


def _snapshot_completed_tasks() -> set[str]:
    completed_dir = workspace_dir / "completed_tasks"
    if not completed_dir.exists():
        return set()
    return set(list_task_markdown_files(completed_dir))


def _build_task_prompt(cycle: int, active_task: Path, branch_name: str, pr_url: str | None) -> str:
    pr_line = f"Pull request: {pr_url}" if pr_url else "Pull request: not created yet"
    return f"""
Cycle {cycle}.

Continue the self-improvement cycle.
Complete exactly one task this run.
The active task for this run is `{active_task.as_posix()}`.
Work only on that task and any directly necessary supporting code changes.
Git branch for this task: `{branch_name}`.
{pr_line}
If fewer than 3 pending tasks exist in ./tasks/, you may create additional task files before finishing the active task.
After completing the active task, stop so the outer Python loop can handle commit, push, PR review, and merge.
""".strip()


def _build_pull_request_body(active_task: Path, cycle: int) -> str:
    return "\n".join(
        [
            f"Automated task branch for `{active_task.name}`.",
            "",
            f"- Cycle: {cycle}",
            f"- Task file: `{active_task.as_posix()}`",
            "- Reviewer feedback is posted back as PR reviews.",
        ]
    )


def _review_is_approved(review_output: str) -> bool:
    return review_output.lstrip().upper().startswith("APPROVED:")


def _build_pr_review_prompt(
    active_task: Path,
    pr_number: int,
    pr_url: str,
    coding_output: str,
    review_round: int,
) -> str:
    return f"""
Review round {review_round}.

Active task file: {active_task.as_posix()}
Pull request number: {pr_number}
Pull request URL: {pr_url}

Coding agent final response:
{coding_output}

Review requirements:
- Review the pull request itself, not just the coding agent narrative. Use `gh pr view`, `gh pr diff`, and shell inspection as needed.
- Verify that the active task was completed correctly and that any claimed completed task move actually happened.
- Verify that the code and tests on the branch match the coding agent's summary.
- Approve only if the PR is ready to merge into `main`.

Respond in exactly one of these forms:
APPROVED: <short reason>
REVISE: <short reason>

If you respond with REVISE, add a section named `Required fixes:` with flat bullet points.
Your response will be posted back to the PR as the review body.
""".strip()


async def _run_cycle(cycle: int) -> None:
    ensure_clean_git(workspace_dir)
    ensure_on_main_branch(workspace_dir)

    active_task = select_pending_task(workspace_dir / "tasks")
    is_valid_task, missing_headers = validate_task_file(active_task)
    if not is_valid_task:
        missing = ", ".join(missing_headers)
        raise RuntimeError(
            f"Active task file is missing required headers: {missing} ({active_task.as_posix()})"
        )

    branch_name = build_task_branch_name(active_task.name)
    create_task_branch(workspace_dir, branch_name)

    completed_before = _snapshot_completed_tasks()
    review_feedback: str | None = None
    pr_url: str | None = None

    for review_round in range(1, 3):
        prompt = _build_task_prompt(cycle, active_task, branch_name, pr_url)
        if review_feedback:
            prompt = (
                f"{prompt}\n\n"
                "Reviewer feedback from the previous PR review:\n"
                f"{review_feedback}\n\n"
                "Address every required fix before stopping."
            )

        coding_summary = await run_coding_agent(coding_agent, prompt)

        changed_paths = get_changed_paths(workspace_dir)
        if not changed_paths:
            raise RuntimeError("Coding agent finished without any repository changes to commit.")

        completed_after = _snapshot_completed_tasks()
        completed_this_cycle = sorted(completed_after - completed_before)
        commit_message = (
            build_review_fix_commit_message(active_task.name)
            if review_feedback
            else build_cycle_commit_message(completed_this_cycle)
        )
        commit_all_changes(workspace_dir, commit_message)
        push_branch(workspace_dir, branch_name)

        pr = ensure_pull_request(
            workspace_dir,
            branch_name,
            build_pull_request_title(active_task.name),
            _build_pull_request_body(active_task, cycle),
        )
        pr_url = pr.url

        review_summary = await run_agent(
            reviewer_agent,
            _build_pr_review_prompt(
                active_task,
                pr.number,
                pr.url,
                coding_summary.final_output,
                review_round,
            ),
            agent_label="review",
        )

        approved = _review_is_approved(review_summary.final_output)
        submit_pull_request_review(
            workspace_dir,
            pr.number,
            approved=approved,
            body=review_summary.final_output,
        )

        if approved:
            merge_pull_request(workspace_dir, pr.number)
            sync_main_branch(workspace_dir)
            code_change_label = (
                "with code changes"
                if has_code_changes(changed_paths)
                else "without code changes"
            )
            print(
                f"[cycle {cycle}] merged PR #{pr.number} {code_change_label}: {commit_message}"
            )
            return

        review_feedback = review_summary.final_output
        completed_before = completed_after

    raise RuntimeError("Reviewer rejected the pull request too many times.")


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

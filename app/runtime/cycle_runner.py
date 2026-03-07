import asyncio
import os
from pathlib import Path

try:
    from ..agent_roles.coding_agent import coding_agent
    from ..agent_roles.review_agent import reviewer_agent
    from ..git_workflow import (
        build_cycle_commit_message,
        build_pull_request_title,
        build_review_fix_commit_message,
        build_task_branch_name,
        commit_all_changes,
        create_task_branch,
        ensure_clean_git,
        ensure_on_main_branch,
        ensure_pull_request,
        get_branch_diff_summary,
        get_changed_paths,
        has_code_changes,
        merge_pull_request,
        push_branch,
        submit_pull_request_review,
        sync_main_branch,
    )
    from ..task_file_validation import validate_task_file
    from ..task_selection import select_pending_task
    from ..tools.run_coding_agent import run_agent, run_coding_agent
    from .prompts import (
        build_bootstrap_branch_name,
        build_bootstrap_pr_body,
        build_bootstrap_prompt,
        build_bootstrap_review_prompt,
        build_pr_review_prompt,
        build_pull_request_body,
        build_task_prompt,
        review_is_approved,
    )
    from .task_state import list_pending_tasks, mark_task_failed, snapshot_completed_tasks
except ImportError:
    from agent_roles.coding_agent import coding_agent
    from agent_roles.review_agent import reviewer_agent
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
        get_branch_diff_summary,
        get_changed_paths,
        has_code_changes,
        merge_pull_request,
        push_branch,
        submit_pull_request_review,
        sync_main_branch,
    )
    from task_file_validation import validate_task_file
    from task_selection import select_pending_task
    from tools.run_coding_agent import run_agent, run_coding_agent
    from runtime.prompts import (
        build_bootstrap_branch_name,
        build_bootstrap_pr_body,
        build_bootstrap_prompt,
        build_bootstrap_review_prompt,
        build_pr_review_prompt,
        build_pull_request_body,
        build_task_prompt,
        review_is_approved,
    )
    from runtime.task_state import list_pending_tasks, mark_task_failed, snapshot_completed_tasks


def require_api_key() -> None:
    if "OPENAI_API_KEY" not in os.environ:
        raise RuntimeError("Please set OPENAI_API_KEY first.")


async def bootstrap_tasks_if_needed(cycle: int, workspace_dir: Path) -> None:
    if list_pending_tasks(workspace_dir):
        return

    branch_name = build_bootstrap_branch_name(cycle)
    create_task_branch(workspace_dir, branch_name)
    review_feedback: str | None = None
    pr_url: str | None = None

    for review_round in range(1, 3):
        prompt = build_bootstrap_prompt(cycle, branch_name, pr_url)
        if review_feedback:
            prompt = (
                f"{prompt}\n\n"
                "Reviewer feedback from the previous PR review:\n"
                f"{review_feedback}\n\n"
                "Address every required fix before stopping."
            )

        coding_summary = await run_coding_agent(coding_agent, prompt)

        pending_tasks = list_pending_tasks(workspace_dir)
        if len(pending_tasks) < 3:
            raise RuntimeError(
                "Bootstrap run finished without creating at least 3 pending task files."
            )

        changed_paths = get_changed_paths(workspace_dir)
        if not changed_paths:
            raise RuntimeError(
                "Bootstrap run finished without any repository changes to commit."
            )

        commit_message = build_cycle_commit_message([])
        if review_feedback:
            commit_message = build_review_fix_commit_message("bootstrap-tasks.md")

        commit_all_changes(workspace_dir, commit_message)
        push_branch(workspace_dir, branch_name)

        pr = ensure_pull_request(
            workspace_dir,
            branch_name,
            f"Bootstrap tasks cycle {cycle}",
            build_bootstrap_pr_body(cycle),
        )
        pr_url = pr.url
        diff_summary = get_branch_diff_summary(workspace_dir)

        review_summary = await run_agent(
            reviewer_agent,
            build_bootstrap_review_prompt(
                pr.number,
                pr.url,
                coding_summary.final_output,
                review_round,
                diff_summary.changed_files,
                diff_summary.diff_stat,
                diff_summary.diff_patch,
            ),
            agent_label="review",
        )

        approved = review_is_approved(review_summary.final_output)
        submit_pull_request_review(
            workspace_dir,
            pr.number,
            approved=approved,
            body=review_summary.final_output,
        )

        if approved:
            merge_pull_request(workspace_dir, pr.number)
            sync_main_branch(workspace_dir)
            print(f"[cycle {cycle}] merged bootstrap PR #{pr.number}")
            return

        review_feedback = review_summary.final_output

    raise RuntimeError("Reviewer rejected the bootstrap task PR too many times.")


async def run_cycle(cycle: int, workspace_dir: Path) -> None:
    ensure_clean_git(workspace_dir)
    ensure_on_main_branch(workspace_dir)
    await bootstrap_tasks_if_needed(cycle, workspace_dir)

    active_task = select_pending_task(workspace_dir / "tasks")
    is_valid_task, missing_headers = validate_task_file(active_task)
    if not is_valid_task:
        missing = ", ".join(missing_headers)
        raise RuntimeError(
            f"Active task file is missing required headers: {missing} "
            f"({active_task.as_posix()})"
        )

    branch_name = build_task_branch_name(active_task.name)
    create_task_branch(workspace_dir, branch_name)

    completed_before = snapshot_completed_tasks(workspace_dir)
    review_feedback: str | None = None
    pr_url: str | None = None

    for review_round in range(1, 3):
        prompt = build_task_prompt(cycle, active_task, branch_name, pr_url)
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
            raise RuntimeError(
                "Coding agent finished without any repository changes to commit."
            )

        completed_after = snapshot_completed_tasks(workspace_dir)
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
            build_pull_request_body(active_task, cycle),
        )
        pr_url = pr.url
        diff_summary = get_branch_diff_summary(workspace_dir)

        review_summary = await run_agent(
            reviewer_agent,
            build_pr_review_prompt(
                active_task,
                pr.number,
                pr.url,
                coding_summary.final_output,
                review_round,
                diff_summary.changed_files,
                diff_summary.diff_stat,
                diff_summary.diff_patch,
            ),
            agent_label="review",
        )

        approved = review_is_approved(review_summary.final_output)
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
                f"[cycle {cycle}] merged PR #{pr.number} "
                f"{code_change_label}: {commit_message}"
            )
            return

        review_feedback = review_summary.final_output
        completed_before = completed_after

    raise RuntimeError("Reviewer rejected the pull request too many times.")



def _get_max_cycles() -> int:
    value = os.environ.get("EVOLVO_MAX_CYCLES")
    if value is not None:
        return int(value)
    return 10

async def run_main_loop(workspace_dir: Path) -> None:
    require_api_key()
    max_cycles = _get_max_cycles()

    cycle = 0
    while cycle < max_cycles:
        cycle += 1
        print(f"\n=== Evolvo cycle {cycle} / {max_cycles} ===")

        active_task: Path | None = None
        try:
            pending_tasks = list_pending_tasks(workspace_dir)
            if pending_tasks:
                active_task = workspace_dir / "tasks" / pending_tasks[0]
            await run_cycle(cycle, workspace_dir)
        except Exception as exc:
            if active_task is not None and active_task.exists():
                failed_task = mark_task_failed(workspace_dir, active_task, str(exc))
                print(f"[cycle {cycle}] task failed and moved to {failed_task}: {exc}")
            else:
                print(f"[cycle {cycle}] stopping: {exc}")
                return

        await asyncio.sleep(2)

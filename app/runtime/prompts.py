from pathlib import Path


def build_bootstrap_branch_name(cycle: int) -> str:
    return f"evolvo/bootstrap-tasks-cycle-{cycle}"


def build_bootstrap_prompt(cycle: int, branch_name: str, pr_url: str | None) -> str:
    pr_line = f"Pull request: {pr_url}" if pr_url else "Pull request: not created yet"
    return f"""
Cycle {cycle}.

There are no pending task markdown files in `./tasks/`.
This run is only for backlog bootstrapping.
Analyze the repository and create at least 3 new task markdown files in `./tasks/`.
Do not complete an existing task in this bootstrap run.
Git branch for this bootstrap run: `{branch_name}`.
{pr_line}
After creating the new task files, stop so the outer Python loop can handle commit,
push, PR review, and merge.
""".strip()


def build_bootstrap_pr_body(cycle: int) -> str:
    return "\n".join(
        [
            "Automated backlog bootstrap for Evolvo.",
            "",
            f"- Cycle: {cycle}",
            "- Goal: create fresh task files because ./tasks/ was empty",
        ]
    )


def build_bootstrap_review_prompt(
    pr_number: int,
    pr_url: str,
    coding_output: str,
    review_round: int,
    changed_files: list[str],
    diff_stat: str,
    diff_patch: str,
) -> str:
    changed_files_block = "\n".join(f"- {path}" for path in changed_files) or "- (no files reported)"
    return f"""
Review round {review_round}.

Bootstrap review for pending-task generation.
Pull request number: {pr_number}
Pull request URL: {pr_url}

Coding agent final response:
{coding_output}

Changed files:
{changed_files_block}

Diff stat:
{diff_stat}

Diff patch excerpt:
{diff_patch}

Review requirements:
- Review the pull request itself, not just the coding agent narrative.
- Start from the provided changed-file list, diff stat, and diff patch excerpt, then verify them with shell inspection if needed.
- Inspect the full PR diff and changed-file list before deciding.
- Reject the bootstrap PR if it changes unrelated files or is larger than needed for creating task files.
- Verify that `./tasks/` now contains at least 3 valid markdown task files.
- Verify that the task files are concrete and relevant to improving the repository.
- Approve only if the backlog bootstrap result is ready to merge into `main`.

Respond in exactly one of these forms:
APPROVED: <short reason>
REVISE: <short reason>

If you respond with REVISE, add a section named `Required fixes:` with flat bullet points.
Your response will be posted back to the PR as the review body.
""".strip()


def build_task_prompt(
    cycle: int,
    active_task: Path,
    branch_name: str,
    pr_url: str | None,
) -> str:
    pr_line = f"Pull request: {pr_url}" if pr_url else "Pull request: not created yet"
    return f"""
Cycle {cycle}.

Continue the self-improvement cycle.
Complete exactly one task this run.
The active task for this run is `{active_task.as_posix()}`.
Work only on that task and any directly necessary supporting code changes.
Git branch for this task: `{branch_name}`.
{pr_line}
If fewer than 3 pending tasks exist in ./tasks/, you may create additional task files
before finishing the active task.
After completing the active task, stop so the outer Python loop can handle commit,
push, PR review, and merge.
""".strip()


def build_pull_request_body(active_task: Path, cycle: int) -> str:
    return "\n".join(
        [
            f"Automated task branch for `{active_task.name}`.",
            "",
            f"- Cycle: {cycle}",
            f"- Task file: `{active_task.as_posix()}`",
            "- Reviewer feedback is posted back as PR reviews.",
        ]
    )


def review_is_approved(review_output: str) -> bool:
    return review_output.lstrip().upper().startswith("APPROVED:")


def build_pr_review_prompt(
    active_task: Path,
    pr_number: int,
    pr_url: str,
    coding_output: str,
    review_round: int,
    changed_files: list[str],
    diff_stat: str,
    diff_patch: str,
) -> str:
    changed_files_block = "\n".join(f"- {path}" for path in changed_files) or "- (no files reported)"
    return f"""
Review round {review_round}.

Active task file: {active_task.as_posix()}
Pull request number: {pr_number}
Pull request URL: {pr_url}

Coding agent final response:
{coding_output}

Changed files:
{changed_files_block}

Diff stat:
{diff_stat}

Diff patch excerpt:
{diff_patch}

Review requirements:
- Review the pull request itself, not just the coding agent narrative.
- Start from the provided changed-file list, diff stat, and diff patch excerpt, then verify them with shell inspection if needed.
- Use `gh pr view`, `gh pr diff`, and shell inspection as needed.
- Inspect the full diff and changed-file list before deciding.
- Check that every file touched by the PR is necessary for the task.
- Reject overly broad patches, unrelated edits, and avoidable rewrites.
- Verify that the active task was completed correctly and that any claimed completed
  task move actually happened.
- Verify that the code and tests on the branch match the coding agent's summary.
- Approve only if the PR is ready to merge into `main`.

Respond in exactly one of these forms:
APPROVED: <short reason>
REVISE: <short reason>

If you respond with REVISE, add a section named `Required fixes:` with flat bullet points.
Your response will be posted back to the PR as the review body.
""".strip()

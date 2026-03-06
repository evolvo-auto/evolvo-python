import asyncio

try:
    from .env_loader import apply_dotenv
    from .runtime.cycle_runner import run_main_loop
    from .runtime.prompts import build_bootstrap_branch_name, build_bootstrap_prompt
    from .runtime.task_state import (
        list_pending_tasks,
        mark_task_failed,
        summarize_task_reconciliation,
    )
    from .tools.agent_tools import workspace_dir
except ImportError:
    from env_loader import apply_dotenv
    from runtime.cycle_runner import run_main_loop
    from runtime.prompts import build_bootstrap_branch_name, build_bootstrap_prompt
    from runtime.task_state import (
        list_pending_tasks,
        mark_task_failed,
        summarize_task_reconciliation,
    )
    from tools.agent_tools import workspace_dir

apply_dotenv(workspace_dir)

print(f"Workspace directory: {workspace_dir}")


def _list_pending_tasks() -> list[str]:
    return list_pending_tasks(workspace_dir)


def _mark_task_failed(task_file, reason: str):
    return mark_task_failed(workspace_dir, task_file, reason)


def _build_bootstrap_branch_name(cycle: int) -> str:
    return build_bootstrap_branch_name(cycle)


def _build_bootstrap_prompt(cycle: int, branch_name: str, pr_url: str | None) -> str:
    return build_bootstrap_prompt(cycle, branch_name, pr_url)


async def main() -> None:
    await run_main_loop(workspace_dir)


if __name__ == "__main__":
    asyncio.run(main())

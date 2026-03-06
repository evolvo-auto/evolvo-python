try:
    from .task_file_counts import list_task_markdown_files
    from .task_file_validation import validate_task_file
    from .task_selection import select_pending_task
    from task_file_counts import list_task_markdown_files
    from task_file_validation import validate_task_file
    from task_selection import select_pending_task
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

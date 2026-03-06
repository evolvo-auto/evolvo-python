try:
except ImportError:
    from tools import context7_tool

workspace_dir = context7_tool.resolve_workspace_root()
shell_tool = get_shell_executor_for_workspace(workspace_dir)
approvals = ApprovalTracker(workspace_dir / ".approvals.json")
editor = WorkspaceEditor(workspace_dir)
apply_patch_tool = editor.build_apply_patch_tool()

agent_tools = [shell_tool, approvals.as_tool(), apply_patch_tool]

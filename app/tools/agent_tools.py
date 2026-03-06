from pathlib import Path

from agents import ApplyPatchTool, WebSearchTool

try:
    from ..approval_tracker import ApprovalTracker
    from ..shell_executor import get_shell_executor_for_workspace
    from ..workspace_editor import WorkspaceEditor
    from . import context7_tool
except ImportError:
    from approval_tracker import ApprovalTracker
    from shell_excecutor import get_shell_executor_for_workspace
    from workspace_editor import WorkspaceEditor
    from tools import context7_tool

workspace_dir = Path("").resolve()
workspace_dir.mkdir(exist_ok=True)

shell_tool = get_shell_executor_for_workspace(workspace_dir)
approvals = ApprovalTracker()
editor = WorkspaceEditor(root=workspace_dir, approvals=approvals, auto_approve=True)
apply_patch_tool = ApplyPatchTool(editor=editor)

agent_tools = [
    WebSearchTool(),
    shell_tool,
    apply_patch_tool,
    context7_tool.context7_tool,
]

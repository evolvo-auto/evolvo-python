try:
    from ..approval_tracker import ApprovalTracker
    from ..shell_executor import get_shell_executor_for_workspace
    from ..workspace_editor import WorkspaceEditor
    from . import context7_tool
except ImportError:
    from approval_tracker import ApprovalTracker
    from shell_executor import get_shell_executor_for_workspace
    from workspace_editor import WorkspaceEditor
    from tools import context7_tool

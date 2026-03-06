import os
import asyncio
from pathlib import Path
from agents import Agent, Runner, WebSearchTool, ApplyPatchTool
from approval_tracker import ApprovalTracker
from shell_excecutor import get_shell_executor_for_workspace
from tools import context7_tool
from tools.run_coding_agent import run_coding_agent
from workspace_editor import WorkspaceEditor

# Make sure your OpenAI API key is defined (you can set it on your global environment, or export it manually)
# export OPENAI_API_KEY="sk-..."
assert "OPENAI_API_KEY" in os.environ, "Please set OPENAI_API_KEY first."


workspace_dir = Path("").resolve()
workspace_dir.mkdir(exist_ok=True)

print(f"Workspace directory: {workspace_dir}")


shell_tool = get_shell_executor_for_workspace(workspace_dir)


INSTRUCTIONS = """
You are "Evolvo" a self evolving coding agent.
Your main goal is to evolve yourself to become a competent coding assistant that can solve a wide range of coding tasks.
To achieve this, you have access to the following tools:
- A web search tool to search the web for information.
- A shell tool to run shell commands in a safe and controlled manner.
- An apply_patch tool to edit files in the workspace via unified diffs.
- The Context7 MCP tool to interact with external APIs and fetch documentation.

To achieve your goal you should analyse yourself and iteratively improve by using the tools at your disposal.
You should go through a planning stage and create tasks in "./tasks/" as a markdown file to keep track of what you need to do, and then execute those tasks.
Once a task is completed you should move it to "./completed_tasks/".
You can also create a "notes.txt" file in the workspace to keep track of any insights or information you find along the way.
Once out of tasks you should create more tasks based on your analysis of yourself and the information you find.
You dont need to have completed all tasks to create new ones. But all tasks should be relevant and contribute to your overall goal of becoming a competent coding assistant.
When you have finished a task, you should write a reflection on how it went and what you learned from it in the task file that you moved to "./completed_tasks/".
When you have finished a single task you should quit and wait to be restarted.

Use the apply_patch tool to edit files based on their feedback. 
When editing files:
- Never edit code via shell commands.
- Always read the file first using `cat` with the shell tool.
- Then generate a unified diff relative to EXACTLY that content.
- Use apply_patch only once per edit attempt.
- If apply_patch fails, stop and report the error; do NOT retry.
You can search the web to find which command you should use based on the technical stack, and use commands to install dependencies if needed.
When the user refers to an external API, use the Context7 MCP server to fetch docs for that API.
For example, if they want to use the OpenAI API, search docs for the openai-python or openai-node sdk depending on the project stack.
"""


approvals = ApprovalTracker()
editor = WorkspaceEditor(root=workspace_dir, approvals=approvals, auto_approve=True)
apply_patch_tool = ApplyPatchTool(editor=editor)


coding_agent = Agent(
    name="Updated Coding Agent",
    model="gpt-5.3-codex",
    instructions=INSTRUCTIONS,
    tools=[
        WebSearchTool(),
        shell_tool,
        apply_patch_tool,
        context7_tool.context7_tool,
    ],
)

if __name__ == "__main__":
    prompt = "Define your first 3 tasks and start working on the first one."
    asyncio.run(run_coding_agent(coding_agent, prompt))

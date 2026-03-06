import os

from agents import HostedMCPTool

CONTEXT7_API_KEY = os.getenv("CONTEXT7_API_KEY")

context7_tool = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "context7",
        "server_url": "https://mcp.context7.com/mcp",
        # Basic usage works without auth; for higher rate limits, pass your key here.
        **({"authorization": f"Bearer {CONTEXT7_API_KEY}"} if CONTEXT7_API_KEY else {}),
        "require_approval": "never",
    },
)
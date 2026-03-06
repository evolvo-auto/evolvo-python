import os
from dataclasses import dataclass

from agents import Agent, ItemHelpers, Runner


@dataclass
class AgentRunSummary:
    final_output: str
    apply_patch_seen: bool


def _get_max_turns() -> int:
    raw_value = os.environ.get("EVOLVO_MAX_TURNS", "").strip()
    if not raw_value:
        return 10

    try:
        parsed = int(raw_value)
    except ValueError:
        return 10

    return parsed if parsed > 0 else 10


def _truncate_output(value: str, limit: int = 400) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "…"


def _is_apply_patch_output(raw_item: object, output_preview: str) -> bool:
    if isinstance(raw_item, dict) and raw_item.get("type") == "apply_patch_call_output":
        return True
    return any(
        output_preview.startswith(prefix)
        for prefix in ("Created ", "Updated ", "Deleted ")
    )


async def run_agent(agent: Agent, prompt: str, agent_label: str) -> AgentRunSummary:
    print(f"=== {agent_label} run starting ===")
    print(f"[user] {prompt}\n")

    apply_patch_seen = False
    result = Runner.run_streamed(agent, input=prompt, max_turns=_get_max_turns())

    async for event in result.stream_events():
        if event.type != "run_item_stream_event":
            continue

        item = event.item

        if item.type == "tool_call_item":
            raw = item.raw_item
            raw_type_name = type(raw).__name__

            if raw_type_name == "ResponseFunctionWebSearch":
                print("[tool] web_search – agent is calling web search")
            elif raw_type_name == "LocalShellCall":
                action = getattr(raw, "action", None)
                commands = getattr(action, "commands", None) if action else None
                if commands:
                    print(f"[tool] shell – running commands: {commands}")
                else:
                    print("[tool] shell – running command")
            elif "MCP" in raw_type_name or "Mcp" in raw_type_name:
                tool_name = getattr(raw, "tool_name", None)
                if tool_name is None:
                    action = getattr(raw, "action", None)
                    tool_name = getattr(action, "tool", None) if action else None
                server_label = getattr(raw, "server_label", None)
                label_str = f" (server={server_label})" if server_label else ""
                if tool_name:
                    print(f"[tool] mcp{label_str} – calling tool {tool_name!r}")
                else:
                    print(f"[tool] mcp{label_str} – MCP tool call")
            else:
                print(f"[tool] {raw_type_name} called")

        elif item.type == "tool_call_output_item":
            raw = item.raw_item
            output_preview = str(item.output)

            if _is_apply_patch_output(raw, output_preview):
                apply_patch_seen = True
                print(f"[apply_patch] {_truncate_output(output_preview)}\n")
            else:
                print(f"[tool output]\n{_truncate_output(output_preview)}\n")

        elif item.type == "message_output_item":
            text = ItemHelpers.text_message_output(item)
            print(f"[{agent_label}]\n{text}\n")

    final_output = "" if result.final_output is None else str(result.final_output)

    print(f"=== {agent_label} run complete ===\n")
    print(f"{agent_label.capitalize()} final answer:\n")
    print(final_output)

    if apply_patch_seen:
        print("\n[apply_patch] One or more apply_patch calls were executed.")
    else:
        print("\n[apply_patch] No apply_patch calls detected in this run.")

    return AgentRunSummary(
        final_output=final_output,
        apply_patch_seen=apply_patch_seen,
    )

async def run_coding_agent(coding_agent: Agent, prompt: str) -> AgentRunSummary:
    return await run_agent(coding_agent, prompt, agent_label="coding")


def _build_review_prompt(
    original_prompt: str,
    coding_output: str,
    review_round: int,
) -> str:
    return f"""
Review round {review_round}.

Original coding prompt:
{original_prompt}

Coding agent final response:
{coding_output}

Review requirements:
- Use shell commands to inspect the repository. Do not trust the coding agent's narrative.
- Verify that the claimed task files, completed task files, and code changes exist on disk.
- Check whether the run followed the task workflow and whether the resulting state is coherent.
- Approve only if the repository state matches the claims and there are no obvious workflow regressions.

Respond in exactly one of these forms:
APPROVED: <short reason>
REVISE: <short reason>

If you respond with REVISE, add a section named `Required fixes:` with flat bullet points.
""".strip()


def _review_is_approved(review_output: str) -> bool:
    return review_output.lstrip().upper().startswith("APPROVED:")


async def run_review_cycle(
    coding_agent: Agent,
    reviewer_agent: Agent,
    prompt: str,
    max_review_rounds: int = 2,
) -> AgentRunSummary:
    reviewer_feedback: str | None = None
    latest_coding_summary: AgentRunSummary | None = None
    latest_review_output = ""

    for review_round in range(1, max_review_rounds + 1):
        coding_prompt = prompt
        if reviewer_feedback:
            coding_prompt = (
                f"{prompt}\n\n"
                "Reviewer feedback from the previous attempt:\n"
                f"{reviewer_feedback}\n\n"
                "Address every required fix before stopping."
            )

        latest_coding_summary = await run_coding_agent(coding_agent, coding_prompt)
        review_summary = await run_agent(
            reviewer_agent,
            _build_review_prompt(prompt, latest_coding_summary.final_output, review_round),
            agent_label="review",
        )
        latest_review_output = review_summary.final_output

        if _review_is_approved(latest_review_output):
            print(f"[review] approved on round {review_round}")
            return latest_coding_summary

        reviewer_feedback = latest_review_output
        print(f"[review] changes requested on round {review_round}")

    raise RuntimeError(
        f"Review cycle failed after {max_review_rounds} round(s).\n{latest_review_output}"
    )

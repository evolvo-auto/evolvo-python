import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.tools.run_coding_agent import AgentRunSummary, run_review_cycle


class ReviewCycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_review_approval_stops_after_first_round(self) -> None:
        calls: list[tuple[str, str]] = []

        async def fake_run_agent(agent, prompt, agent_label):
            calls.append((agent_label, prompt))
            if agent_label == "coding":
                return AgentRunSummary(
                    final_output="implemented the task",
                    apply_patch_seen=True,
                )
            return AgentRunSummary(
                final_output="APPROVED: repository state matches the report",
                apply_patch_seen=False,
            )

        with patch("app.tools.run_coding_agent.run_agent", side_effect=fake_run_agent):
            result = await run_review_cycle(object(), object(), "Base prompt", 2)

        self.assertEqual(result.final_output, "implemented the task")
        self.assertEqual([label for label, _ in calls], ["coding", "review"])

    async def test_review_feedback_is_passed_back_to_coding_agent(self) -> None:
        calls: list[tuple[str, str]] = []

        async def fake_run_agent(agent, prompt, agent_label):
            calls.append((agent_label, prompt))
            if agent_label == "coding":
                attempt = sum(1 for label, _ in calls if label == "coding")
                return AgentRunSummary(
                    final_output=f"coding attempt {attempt}",
                    apply_patch_seen=True,
                )

            review_attempt = sum(1 for label, _ in calls if label == "review")
            if review_attempt == 1:
                return AgentRunSummary(
                    final_output=(
                        "REVISE: task verification was incomplete\n"
                        "Required fixes:\n"
                        "- verify the moved task file\n"
                        "- list the changed code files accurately"
                    ),
                    apply_patch_seen=False,
                )

            return AgentRunSummary(
                final_output="APPROVED: fixes were applied and verified",
                apply_patch_seen=False,
            )

        with patch("app.tools.run_coding_agent.run_agent", side_effect=fake_run_agent):
            result = await run_review_cycle(object(), object(), "Base prompt", 2)

        self.assertEqual(result.final_output, "coding attempt 2")
        self.assertEqual(
            [label for label, _ in calls],
            ["coding", "review", "coding", "review"],
        )
        self.assertIn("Reviewer feedback from the previous attempt", calls[2][1])
        self.assertIn("Required fixes:", calls[2][1])

    async def test_review_cycle_raises_after_max_rounds(self) -> None:
        calls: list[tuple[str, str]] = []

        async def fake_run_agent(agent, prompt, agent_label):
            calls.append((agent_label, prompt))
            if agent_label == "coding":
                return AgentRunSummary(
                    final_output="still working",
                    apply_patch_seen=True,
                )
            return AgentRunSummary(
                final_output=(
                    "REVISE: the coding agent did not satisfy the workflow\n"
                    "Required fixes:\n"
                    "- complete exactly one task"
                ),
                apply_patch_seen=False,
            )

        with patch("app.tools.run_coding_agent.run_agent", side_effect=fake_run_agent):
            with self.assertRaisesRegex(RuntimeError, "Review cycle failed after 2 round"):
                await run_review_cycle(object(), object(), "Base prompt", 2)

        self.assertEqual(
            [label for label, _ in calls],
            ["coding", "review", "coding", "review"],
        )


if __name__ == "__main__":
    unittest.main()

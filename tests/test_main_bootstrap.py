import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import (
    _build_bootstrap_branch_name,
    _build_bootstrap_prompt,
    _list_pending_tasks,
)


class MainBootstrapTests(unittest.TestCase):
    def test_build_bootstrap_branch_name_uses_cycle(self) -> None:
        self.assertEqual(
            _build_bootstrap_branch_name(7),
            "evolvo/bootstrap-tasks-cycle-7",
        )

    def test_build_bootstrap_prompt_mentions_task_creation_requirement(self) -> None:
        prompt = _build_bootstrap_prompt(3, "evolvo/bootstrap-tasks-cycle-3", None)

        self.assertIn("There are no pending task markdown files", prompt)
        self.assertIn("create at least 3 new task markdown files", prompt)
        self.assertIn("evolvo/bootstrap-tasks-cycle-3", prompt)

    def test_list_pending_tasks_returns_empty_when_tasks_dir_missing(self) -> None:
        fake_root = Path("/tmp/evolvo-tests-no-tasks")
        with patch("app.main.workspace_dir", fake_root):
            self.assertEqual(_list_pending_tasks(), [])


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.quality_commands import (
    LINT_COMMAND,
    PYTHON_COMMAND,
    TEST_COMMAND,
    TEST_FAILURE_COMMAND,
    TEST_TARGET_COMMAND_TEMPLATE,
)


class QualityCommandsTests(unittest.TestCase):
    def test_python_command_prefers_repo_virtualenv(self) -> None:
        self.assertEqual(PYTHON_COMMAND, ".venv/bin/python")

    def test_lint_command_uses_ruff(self) -> None:
        self.assertEqual(LINT_COMMAND, ".venv/bin/python -m ruff check app tests")

    def test_test_command_uses_pytest(self) -> None:
        self.assertEqual(TEST_COMMAND, ".venv/bin/python -m pytest")

    def test_failure_command_uses_verbose_fail_fast_pytest(self) -> None:
        self.assertEqual(TEST_FAILURE_COMMAND, ".venv/bin/python -m pytest -x -vv")

    def test_target_command_template_uses_nodeid_placeholder(self) -> None:
        self.assertEqual(
            TEST_TARGET_COMMAND_TEMPLATE,
            ".venv/bin/python -m pytest -x -vv <path-or-nodeid>",
        )


if __name__ == "__main__":
    unittest.main()

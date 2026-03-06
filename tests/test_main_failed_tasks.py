import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import _mark_task_failed


class MainFailedTasksTests(unittest.TestCase):
    def test_mark_task_failed_moves_file_and_appends_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_file = root / "tasks" / "015-sample.md"
            task_file.parent.mkdir(parents=True, exist_ok=True)
            task_file.write_text("# Task: Sample\n\n## Why\nBecause\n", encoding="utf-8")

            with patch("app.main.workspace_dir", root):
                failed_path = _mark_task_failed(task_file, "example failure")

            self.assertEqual(failed_path, root / "failed_tasks" / "015-sample.md")
            self.assertFalse(task_file.exists())
            self.assertTrue(failed_path.exists())
            content = failed_path.read_text(encoding="utf-8")
            self.assertIn("## Failure", content)
            self.assertIn("example failure", content)


if __name__ == "__main__":
    unittest.main()

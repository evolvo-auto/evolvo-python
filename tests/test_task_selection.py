import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.task_selection import select_pending_task


class TaskSelectionTests(unittest.TestCase):
    def test_selects_lexicographically_first_markdown_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tasks_dir = Path(tmp)
            (tasks_dir / "020-zeta.md").write_text("# zeta\n", encoding="utf-8")
            (tasks_dir / "010-alpha.md").write_text("# alpha\n", encoding="utf-8")
            (tasks_dir / "notes.txt").write_text("not a task\n", encoding="utf-8")

            selected = select_pending_task(tasks_dir)

            self.assertEqual(selected.name, "010-alpha.md")

    def test_raises_when_tasks_directory_is_missing(self) -> None:
        missing_dir = Path("this-directory-should-not-exist-for-task-selection-tests")
        with self.assertRaises(FileNotFoundError):
            select_pending_task(missing_dir)

    def test_raises_when_no_markdown_tasks_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tasks_dir = Path(tmp)
            (tasks_dir / "readme.txt").write_text("empty\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                select_pending_task(tasks_dir)


if __name__ == "__main__":
    unittest.main()

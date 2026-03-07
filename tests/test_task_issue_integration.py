from pathlib import Path
from unittest.mock import patch

import pytest

from app.runtime.task_state import create_task_file_with_issue


def test_create_task_file_with_issue_writes_task_and_creates_issue(tmp_path: Path) -> None:
    content = "# Task 999: Example\n\n## Scope\n- test\n"
    with patch("app.runtime.task_state.create_issue", return_value={"id": 1}) as mocked:
        task_path = create_task_file_with_issue(tmp_path, "999-example.md", content)

    assert task_path == tmp_path / "tasks" / "999-example.md"
    assert task_path.exists()
    assert task_path.read_text(encoding="utf-8") == content
    mocked.assert_called_once_with(content)


def test_create_task_file_with_issue_surfaces_issue_creation_failure(tmp_path: Path) -> None:
    with patch("app.runtime.task_state.create_issue", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError, match="boom"):
            create_task_file_with_issue(tmp_path, "999-example.md", "# Task 999")

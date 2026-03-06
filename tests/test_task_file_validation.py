from pathlib import Path

from app.task_file_validation import validate_task_file


def test_validate_task_file_returns_true_for_valid_content(tmp_path: Path) -> None:
    task_file = tmp_path / "001-valid-task.md"
    task_file.write_text(
        "\n".join(
            [
                "# Task: Example task",
                "",
                "## Why",
                "Because reasons.",
                "",
                "## Scope",
                "- Add thing",
                "",
                "## Acceptance Criteria",
                "- Works",
            ]
        ),
        encoding="utf-8",
    )

    is_valid, missing_headers = validate_task_file(task_file)

    assert is_valid is True
    assert missing_headers == []


def test_validate_task_file_returns_missing_headers(tmp_path: Path) -> None:
    task_file = tmp_path / "002-invalid-task.md"
    task_file.write_text(
        "\n".join(
            [
                "# Task: Incomplete",
                "",
                "## Why",
                "Need to do this.",
            ]
        ),
        encoding="utf-8",
    )

    is_valid, missing_headers = validate_task_file(task_file)

    assert is_valid is False
    assert missing_headers == ["## Scope", "## Acceptance Criteria"]


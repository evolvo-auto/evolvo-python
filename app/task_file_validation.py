"""Helpers for validating task markdown files."""

from __future__ import annotations

from pathlib import Path


REQUIRED_HEADERS: tuple[str, ...] = (
    "# Task:",
    "# Task",
    "## Why",
    "## Scope",
    "## Acceptance Criteria",
)


def validate_task_file(task_file: str | Path) -> tuple[bool, list[str]]:
    """Validate that a task markdown file contains required headers."""
    file_path = Path(task_file)
    content = file_path.read_text(encoding="utf-8")

    missing_headers = [header for header in REQUIRED_HEADERS if header not in content]
    return (len(missing_headers) == 0, missing_headers)


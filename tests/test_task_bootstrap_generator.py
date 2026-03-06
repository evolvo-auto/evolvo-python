from pathlib import Path

from app.task_bootstrap_generator import (
    create_task_file,
    generate_task_markdown,
    next_task_id,
    slugify_title,
)
from app.runtime.task_state import ensure_minimum_pending_tasks


def test_slugify_title_normalizes_format() -> None:
    assert slugify_title("Add Bootstrap Task Template & Helper!") == "add-bootstrap-task-template-helper"


def test_next_task_id_uses_highest_numeric_prefix(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / "002-existing.md").write_text("x", encoding="utf-8")
    (tasks_dir / "010-another.md").write_text("x", encoding="utf-8")
    (tasks_dir / "note.md").write_text("x", encoding="utf-8")

    assert next_task_id(tasks_dir) == "011"


def test_generate_task_markdown_has_expected_sections() -> None:
    content = generate_task_markdown("021", "sample title", "sample goal")
    assert content.startswith("# Task: 021: sample title")
    assert "## Goal" in content
    assert "## Scope" in content
    assert "## Acceptance Criteria" in content


def test_ensure_minimum_pending_tasks_bootstraps_to_three(tmp_path: Path) -> None:
    pending = ensure_minimum_pending_tasks(tmp_path, minimum=3)

    assert len(pending) == 3
    generated = sorted((tmp_path / "tasks").glob("*.md"))
    assert len(generated) == 3
    assert generated[0].name.startswith("001-")


def test_create_task_file_uses_deterministic_numbering(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    first = create_task_file(tasks_dir, "first task")
    second = create_task_file(tasks_dir, "second task")
    assert first.name.startswith("001-")
    assert second.name.startswith("002-")

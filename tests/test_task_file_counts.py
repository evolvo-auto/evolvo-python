from pathlib import Path

from app.task_file_counts import count_task_markdown_files, list_task_markdown_files


def test_count_task_markdown_files_returns_zero_for_empty_directories(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    completed_dir = tmp_path / "completed_tasks"
    tasks_dir.mkdir()
    completed_dir.mkdir()

    pending_count, completed_count = count_task_markdown_files(tasks_dir, completed_dir)

    assert pending_count == 0
    assert completed_count == 0


def test_count_task_markdown_files_only_counts_markdown_files(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    completed_dir = tmp_path / "completed_tasks"
    tasks_dir.mkdir()
    completed_dir.mkdir()

    (tasks_dir / "001-task.md").write_text("pending markdown", encoding="utf-8")
    (tasks_dir / "notes.txt").write_text("not markdown", encoding="utf-8")
    (completed_dir / "999-done.md").write_text("completed markdown", encoding="utf-8")
    (completed_dir / "archive.json").write_text("not markdown", encoding="utf-8")

    pending_count, completed_count = count_task_markdown_files(tasks_dir, completed_dir)

    assert pending_count == 1
    assert completed_count == 1


def test_list_task_markdown_files_returns_sorted_markdown_filenames(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()

    (tasks_dir / "020-zeta.md").write_text("a", encoding="utf-8")
    (tasks_dir / "010-alpha.md").write_text("b", encoding="utf-8")
    (tasks_dir / "notes.txt").write_text("c", encoding="utf-8")

    files = list_task_markdown_files(tasks_dir)

    assert files == ["010-alpha.md", "020-zeta.md"]

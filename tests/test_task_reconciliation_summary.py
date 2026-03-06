from pathlib import Path

from app.main import summarize_task_reconciliation


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# x\n", encoding="utf-8")


def test_summarize_task_reconciliation_reports_overlap_and_unique_ids(tmp_path: Path) -> None:
    _touch(tmp_path / "tasks" / "001-a.md")
    _touch(tmp_path / "tasks" / "002-b.md")
    _touch(tmp_path / "completed_tasks" / "002-b.md")
    _touch(tmp_path / "completed_tasks" / "003-c.md")

    result = summarize_task_reconciliation(tmp_path)

    assert result["overlap_ids"] == ["002"]
    assert result["only_in_tasks_ids"] == ["001"]
    assert result["only_in_completed_ids"] == ["003"]

from pathlib import Path

from app.runtime.prompts import build_bootstrap_review_prompt, build_pr_review_prompt


def test_build_pr_review_prompt_includes_diff_context() -> None:
    prompt = build_pr_review_prompt(
        Path("tasks/015-fix-shell-executor.md"),
        12,
        "https://github.com/example/repo/pull/12",
        "Implemented a narrow fix.",
        1,
        ["app/main.py", "tests/test_main.py"],
        "2 files changed, 12 insertions(+), 3 deletions(-)",
        "diff --git a/app/main.py b/app/main.py",
    )

    assert "Changed files:" in prompt
    assert "- app/main.py" in prompt
    assert "Diff stat:" in prompt
    assert "2 files changed, 12 insertions(+), 3 deletions(-)" in prompt
    assert "Diff patch excerpt:" in prompt
    assert "diff --git a/app/main.py b/app/main.py" in prompt


def test_build_bootstrap_review_prompt_includes_diff_context() -> None:
    prompt = build_bootstrap_review_prompt(
        3,
        "https://github.com/example/repo/pull/3",
        "Created three backlog tasks.",
        2,
        ["tasks/017-example.md"],
        "1 file changed, 20 insertions(+)",
        "diff --git a/tasks/017-example.md b/tasks/017-example.md",
    )

    assert "Changed files:" in prompt
    assert "- tasks/017-example.md" in prompt
    assert "Diff stat:" in prompt
    assert "1 file changed, 20 insertions(+)" in prompt
    assert "Diff patch excerpt:" in prompt
    assert "diff --git a/tasks/017-example.md b/tasks/017-example.md" in prompt

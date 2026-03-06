from pathlib import Path


def _python_command() -> str:
    return ".venv/bin/python" if Path(".venv/bin/python").exists() else "python3"


PYTHON_COMMAND = _python_command()
LINT_COMMAND = f"{PYTHON_COMMAND} -m ruff check app tests"
TEST_COMMAND = f"{PYTHON_COMMAND} -m pytest"

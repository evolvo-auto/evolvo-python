import sys
from pathlib import Path


def test_shell_executor_import_paths_are_backward_compatible() -> None:
    app_dir = Path(__file__).resolve().parents[1] / "app"
    sys.path.insert(0, str(app_dir))

    from shell_executor import get_shell_executor_for_workspace as new_import
    from shell_excecutor import get_shell_executor_for_workspace as legacy_import

    assert callable(new_import)
    assert callable(legacy_import)
    assert new_import is legacy_import

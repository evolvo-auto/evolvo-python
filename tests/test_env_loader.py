import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.env_loader import apply_dotenv, load_dotenv


class EnvLoaderTests(unittest.TestCase):
    def test_load_dotenv_returns_empty_dict_when_file_is_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            loaded = load_dotenv(Path(tmp))
        self.assertEqual(loaded, {})

    def test_load_dotenv_parses_comments_export_and_quoted_values(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env").write_text(
                "\n".join(
                    [
                        "# comment",
                        "OPENAI_API_KEY=sk-test",
                        " export MODEL = gpt-5.3-codex ",
                        'QUOTED="hello world"',
                        "SINGLE='value'",
                        "INVALID_LINE",
                    ]
                ),
                encoding="utf-8",
            )

            loaded = load_dotenv(root)

        self.assertEqual(
            loaded,
            {
                "OPENAI_API_KEY": "sk-test",
                "MODEL": "gpt-5.3-codex",
                "QUOTED": "hello world",
                "SINGLE": "value",
            },
        )

    def test_apply_dotenv_does_not_override_existing_environment(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env").write_text(
                "OPENAI_API_KEY=from-file\nNEW_VALUE=from-dotenv\n",
                encoding="utf-8",
            )

            with patch.dict(os.environ, {"OPENAI_API_KEY": "already-set"}, clear=True):
                loaded = apply_dotenv(root)
                self.assertEqual(os.environ["OPENAI_API_KEY"], "already-set")
                self.assertEqual(os.environ["NEW_VALUE"], "from-dotenv")

        self.assertEqual(
            loaded,
            {
                "OPENAI_API_KEY": "from-file",
                "NEW_VALUE": "from-dotenv",
            },
        )

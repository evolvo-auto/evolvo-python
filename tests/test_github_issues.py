from __future__ import annotations

import json
from unittest.mock import patch

from app.tools.github.issues import list_issues


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_list_issues_returns_parsed_issue_list() -> None:
    expected = [{"id": 1, "title": "example issue"}]
    payload = json.dumps(expected).encode("utf-8")

    with patch("app.tools.github.issues.urlopen", return_value=_FakeResponse(payload)) as mocked_open:
        result = list_issues()

    assert result == expected
    mocked_open.assert_called_once()

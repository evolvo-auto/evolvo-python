from __future__ import annotations

import json
import os
from unittest.mock import patch

import pytest

from app.tools.github.issues.list import list_issues


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

    with patch.dict(
        os.environ,
        {
            "GITHUB_OWNER": "evolvo-auto",
            "GITHUB_REPO": "evolvo-python",
            "GITHUB_TOKEN": "pat-123",
        },
        clear=True,
    ), patch("app.tools.github.issues.list.urlopen", return_value=_FakeResponse(payload)) as mocked_open:
        result = list_issues()

    assert result == expected
    mocked_open.assert_called_once()
    request = mocked_open.call_args.args[0]
    headers = {key.lower(): value for key, value in request.header_items()}
    assert request.full_url == (
        "https://api.github.com/repos/evolvo-auto/evolvo-python/issues?state=all&per_page=100&page=1"
    )
    assert headers["authorization"] == "Bearer pat-123"


def test_list_issues_filters_pull_requests() -> None:
    payload = json.dumps(
        [
            {"id": 1, "title": "issue"},
            {"id": 2, "title": "pr", "pull_request": {"url": "https://api.github.com/pr/2"}},
        ]
    ).encode("utf-8")

    with patch.dict(
        os.environ,
        {"GITHUB_OWNER": "evolvo-auto", "GITHUB_REPO": "evolvo-python"},
        clear=True,
    ), patch("app.tools.github.issues.list.urlopen", return_value=_FakeResponse(payload)):
        result = list_issues()

    assert result == [{"id": 1, "title": "issue"}]


def test_list_issues_requires_owner_and_repo() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="GITHUB_OWNER and GITHUB_REPO must be set"):
            list_issues()

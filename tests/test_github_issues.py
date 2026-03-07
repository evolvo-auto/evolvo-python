import json
import os
from unittest.mock import patch

import pytest

from app.tools.github.issues.create import create_issue
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


def test_list_issues_requires_owner_and_repo() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="GITHUB_OWNER and GITHUB_REPO must be set"):
            list_issues()


def test_create_issue_rejects_empty_content() -> None:
    with patch.dict(
        os.environ,
        {
            "GITHUB_OWNER": "evolvo-auto",
            "GITHUB_REPO": "evolvo-python",
            "GITHUB_TOKEN": "pat-123",
        },
        clear=True,
    ):
        with pytest.raises(ValueError, match="Issue content must not be empty"):
            create_issue("   ")


def test_create_issue_sends_json_with_auth_header() -> None:
    payload = json.dumps({"id": 42, "title": "New issue"}).encode("utf-8")

    with patch.dict(
        os.environ,
        {
            "GITHUB_OWNER": "evolvo-auto",
            "GITHUB_REPO": "evolvo-python",
            "GITHUB_TOKEN": "pat-123",
        },
        clear=True,
    ), patch("app.tools.github.issues.create.urlopen", return_value=_FakeResponse(payload)) as mocked_open:
        result = create_issue("New issue")

    assert result == {"id": 42, "title": "New issue"}
    mocked_open.assert_called_once()
    request = mocked_open.call_args.args[0]
    headers = {key.lower(): value for key, value in request.header_items()}
    assert request.full_url == "https://api.github.com/repos/evolvo-auto/evolvo-python/issues"
    assert headers["authorization"] == "Bearer pat-123"
    assert headers["content-type"] == "application/json"


def test_list_issues_returns_parsed_list_and_filters_pull_requests() -> None:
    payload = json.dumps(
        [
            {"id": 1, "title": "Issue 1"},
            {"id": 2, "title": "PR 1", "pull_request": {"url": "https://example.invalid/pr/2"}},
            {"id": 3, "title": "Issue 2"},
        ]
    ).encode("utf-8")

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

    assert result == [{"id": 1, "title": "Issue 1"}, {"id": 3, "title": "Issue 2"}]
    mocked_open.assert_called_once()

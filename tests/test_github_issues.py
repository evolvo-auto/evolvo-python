from __future__ import annotations

import json
import os
from unittest.mock import patch

import pytest

from app.tools.github.issues.comment import comment_on_issue
from app.tools.github.issues.create import create_issue
from app.tools.github.issues.list import list_issues


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def test_list_issues_returns_parsed_list_and_filters_pull_requests() -> None:
    payload = json.dumps(
        [
            {"id": 1, "title": "Bug"},
            {"id": 2, "title": "PR", "pull_request": {"url": "https://example.test/pr/2"}},
            {"id": 3, "title": "Feature"},
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

    assert result == [{"id": 1, "title": "Bug"}, {"id": 3, "title": "Feature"}]
    mocked_open.assert_called_once()
    request = mocked_open.call_args.args[0]
    headers = {key.lower(): value for key, value in request.header_items()}
    assert headers["authorization"] == "Bearer pat-123"


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
    payload = json.dumps({"id": 1000, "title": "New task"}).encode("utf-8")

    with patch.dict(
        os.environ,
        {
            "GITHUB_OWNER": "evolvo-auto",
            "GITHUB_REPO": "evolvo-python",
            "GITHUB_TOKEN": "pat-123",
        },
        clear=True,
    ), patch("app.tools.github.issues.create.urlopen", return_value=_FakeResponse(payload)) as mocked_open:
        result = create_issue("New task")

    assert result == {"id": 1000, "title": "New task"}
    mocked_open.assert_called_once()
    request = mocked_open.call_args.args[0]
    headers = {key.lower(): value for key, value in request.header_items()}
    assert request.full_url == "https://api.github.com/repos/evolvo-auto/evolvo-python/issues"
    assert headers["authorization"] == "Bearer pat-123"
    assert headers["content-type"] == "application/json"
    assert json.loads(request.data.decode("utf-8")) == {"title": "New task"}


def test_comment_on_issue_rejects_empty_fields() -> None:
    with patch.dict(
        os.environ,
        {
            "GITHUB_OWNER": "evolvo-auto",
            "GITHUB_REPO": "evolvo-python",
            "GITHUB_TOKEN": "pat-123",
        },
        clear=True,
    ):
        with pytest.raises(ValueError, match="Issue ID must not be empty"):
            comment_on_issue("   ", "hello")
        with pytest.raises(ValueError, match="Comment content must not be empty"):
            comment_on_issue("123", "   ")


def test_comment_on_issue_sends_json_with_auth_header() -> None:
    payload = json.dumps({"id": 1001, "body": "Nice work"}).encode("utf-8")

    with patch.dict(
        os.environ,
        {
            "GITHUB_OWNER": "evolvo-auto",
            "GITHUB_REPO": "evolvo-python",
            "GITHUB_TOKEN": "pat-123",
        },
        clear=True,
    ), patch("app.tools.github.issues.comment.urlopen", return_value=_FakeResponse(payload)) as mocked_open:
        result = comment_on_issue("123", "Nice work")

    assert result == {"id": 1001, "body": "Nice work"}
    mocked_open.assert_called_once()
    request = mocked_open.call_args.args[0]
    headers = {key.lower(): value for key, value in request.header_items()}
    assert request.full_url == "https://api.github.com/repos/evolvo-auto/evolvo-python/issues/123/comments"
    assert headers["authorization"] == "Bearer pat-123"
    assert headers["content-type"] == "application/json"
    assert json.loads(request.data.decode("utf-8")) == {"body": "Nice work"}

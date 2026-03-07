from unittest.mock import patch

import pytest

from app.tools.github.issues.create import create_issue
from app.tools.github.issues.list import list_issues
def test_list_issues_requires_owner_and_repo() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="GITHUB_OWNER and GITHUB_REPO must be set"):
            list_issues()


def test_create_issue_posts_title_and_returns_parsed_response() -> None:
    expected = {"id": 7, "title": "New issue"}
    payload = json.dumps(expected).encode("utf-8")

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

    assert result == expected
    mocked_open.assert_called_once()
    request = mocked_open.call_args.args[0]
    headers = {key.lower(): value for key, value in request.header_items()}
    assert request.full_url == "https://api.github.com/repos/evolvo-auto/evolvo-python/issues"
    assert request.get_method() == "POST"
    assert request.data == b'{"title": "New issue"}'
    assert headers["authorization"] == "Bearer pat-123"


def test_create_issue_requires_owner_and_repo() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="GITHUB_OWNER and GITHUB_REPO must be set"):
            create_issue("Example issue")


def test_create_issue_rejects_empty_content() -> None:
    with patch.dict(
        os.environ,
        {"GITHUB_OWNER": "evolvo-auto", "GITHUB_REPO": "evolvo-python"},
        clear=True,
    ):
        with pytest.raises(ValueError, match="Issue content must not be empty"):
            create_issue("   ")

from __future__ import annotations

from urllib.request import Request, urlopen


def list_issues() -> list[dict]:
    """Return issues for the evolvo-python repository from GitHub's REST API."""
    request = Request(
        "https://api.github.com/repos/paddyroddy/evolvo-python/issues",
        headers={"Accept": "application/vnd.github+json"},
    )
    with urlopen(request) as response:  # nosec B310 - controlled GitHub API URL
        return __import__("json").loads(response.read().decode("utf-8"))

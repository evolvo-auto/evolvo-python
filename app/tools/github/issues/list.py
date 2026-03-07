from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.tools.github.urls import build_issues_url
from app.tools.github.shared import build_headers


def list_issues() -> list[dict]:
    """Return repository issues from GitHub's REST API.

    Pull requests are excluded from the returned result.
    """
    owner = os.environ.get("GITHUB_OWNER")
    repo = os.environ.get("GITHUB_REPO")
    if not owner or not repo:
        raise RuntimeError("GITHUB_OWNER and GITHUB_REPO must be set.")

    headers = build_headers()
    issues: list[dict] = []
    page = 1

    while True:
        request = Request(build_issues_url(owner, repo, page), headers=headers)
        try:
            with urlopen(request, timeout=15) as response:  # nosec B310 - controlled GitHub API URL
                payload = response.read().decode("utf-8")
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace").strip()
            message = f"GitHub API request failed with status {exc.code}."
            if details:
                message = f"{message} {details}"
            raise RuntimeError(message) from exc
        except URLError as exc:
            raise RuntimeError(f"GitHub API request failed: {exc.reason}") from exc

        page_data = json.loads(payload)
        if not isinstance(page_data, list):
            raise RuntimeError("GitHub issues response was not a list.")

        issues.extend(
            item
            for item in page_data
            if isinstance(item, dict) and "pull_request" not in item
        )

        if len(page_data) < 100:
            break
        page += 1

    return issues

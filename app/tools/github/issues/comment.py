from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.tools.github.shared import build_headers


def comment_on_issue(issue_id: str, content: str) -> dict:
    """Post a comment on an existing GitHub issue in the configured repository."""
    owner = os.environ.get("GITHUB_OWNER")
    repo = os.environ.get("GITHUB_REPO")
    if not owner or not repo:
        raise RuntimeError("GITHUB_OWNER and GITHUB_REPO must be set.")

    issue_number = (issue_id or "").strip()
    if not issue_number:
        raise ValueError("Issue ID must not be empty.")

    body = (content or "").strip()
    if not body:
        raise ValueError("Comment content must not be empty.")

    headers = build_headers()
    headers["Content-Type"] = "application/json"
    payload = json.dumps({"body": body}).encode("utf-8")
    request = Request(
        f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments",
        data=payload,
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:  # nosec B310 - controlled GitHub API URL
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace").strip()
        message = f"GitHub API request failed with status {exc.code}."
        if details:
            message = f"{message} {details}"
        raise RuntimeError(message) from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub API request failed: {exc.reason}") from exc

    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError("GitHub comment response was not an object.")
    return parsed

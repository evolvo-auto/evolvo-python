from urllib.parse import urlencode


def build_issues_url(owner: str, repo: str, page: int) -> str:
    query = urlencode({"state": "all", "per_page": 100, "page": page})
    return f"https://api.github.com/repos/{owner}/{repo}/issues?{query}"
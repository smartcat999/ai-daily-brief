from __future__ import annotations

from app.models import GithubProject


def fetch_github_projects() -> list[GithubProject]:
    # MVP: placeholder. In next iteration we will call GitHub search/trending.
    return [
        GithubProject(
            name="mvp-placeholder/project",
            url="https://github.com",
            stars=0,
            description="MVP placeholder GitHub project",
        )
    ]

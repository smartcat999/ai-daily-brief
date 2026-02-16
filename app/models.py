from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class NewsItem:
    title: str
    url: str
    published_at: dt.datetime | None = None
    source: str | None = None


@dataclass(frozen=True)
class GithubProject:
    name: str
    url: str
    stars: int | None = None
    description: str | None = None

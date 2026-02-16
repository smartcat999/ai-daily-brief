from __future__ import annotations

import datetime as dt

from app.models import NewsItem


def fetch_rss_items() -> list[NewsItem]:
    # MVP: placeholder. In next iteration we will fetch RSS feeds.
    return [
        NewsItem(
            title="MVP placeholder news item",
            url="https://example.com",
            published_at=dt.datetime.now(dt.timezone.utc),
            source="placeholder",
        )
    ]

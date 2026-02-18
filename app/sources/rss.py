from __future__ import annotations

import datetime as dt
import html
import os
import re
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import feedparser
import requests

from app.models import NewsItem


_TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
}


_TAG_RE = re.compile(r"<[^>]+>")


def _parse_datetime(entry: dict) -> dt.datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            return dt.datetime.fromtimestamp(
                dt.datetime(*parsed[:6], tzinfo=dt.timezone.utc).timestamp(),
                tz=dt.timezone.utc,
            )
    return None


def _iter_feed_urls() -> list[str]:
    raw = os.getenv("RSS_FEEDS", "").strip()
    if not raw:
        return []
    return [u.strip() for u in raw.split(",") if u.strip()]


def _source_label(feed: feedparser.FeedParserDict, url: str) -> str:
    title = (feed.get("title") or "").strip()
    if title:
        return title
    host = urlparse(url).netloc
    return host or url


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.query:
        return url
    params = [(k, v) for k, v in parse_qsl(parsed.query) if k.lower() not in _TRACKING_PARAMS]
    clean = parsed._replace(query=urlencode(params, doseq=True))
    return urlunparse(clean)


def _normalize_title(title: str) -> str:
    return " ".join(title.lower().split())


def _clean_text(text: str) -> str:
    text = html.unescape(text)
    text = _TAG_RE.sub(" ", text)
    return " ".join(text.split()).strip()


def _exclude_keywords() -> tuple[str, ...]:
    raw = os.getenv("RSS_EXCLUDE_KEYWORDS", "").strip()
    if not raw:
        return tuple()
    return tuple(k.strip().lower() for k in raw.split(",") if k.strip())


def _include_keywords() -> tuple[str, ...]:
    raw = os.getenv("RSS_INCLUDE_KEYWORDS", "").strip()
    if not raw:
        return tuple()
    return tuple(k.strip().lower() for k in raw.split(",") if k.strip())


def _entry_text(entry: dict) -> str:
    parts: list[str] = []
    title = entry.get("title")
    summary = entry.get("summary")
    description = entry.get("description")
    if title:
        parts.append(str(title))
    if summary:
        parts.append(str(summary))
    if description:
        parts.append(str(description))
    return " ".join(parts).lower()


def _entry_summary(entry: dict) -> str:
    summary = entry.get("summary") or entry.get("description") or ""
    if not summary:
        return ""
    return _clean_text(str(summary))


def _dedupe(items: Iterable[NewsItem]) -> list[NewsItem]:
    seen_url: set[str] = set()
    seen_title: set[str] = set()
    out: list[NewsItem] = []
    for item in items:
        url = item.url or ""
        title = item.title or ""
        key_url = _normalize_url(url)
        key_title = _normalize_title(title)
        if key_url and key_url in seen_url:
            continue
        if key_title and key_title in seen_title:
            continue
        if key_url:
            seen_url.add(key_url)
        if key_title:
            seen_title.add(key_title)
        out.append(item)
    return out


def fetch_rss_items() -> list[NewsItem]:
    urls = _iter_feed_urls()
    if not urls:
        return []

    timeout_raw = os.getenv("RSS_REQUEST_TIMEOUT", "15").strip()
    try:
        timeout = max(1, int(timeout_raw))
    except ValueError:
        timeout = 15

    per_feed_raw = os.getenv("RSS_PER_FEED_LIMIT", "50").strip()
    try:
        per_feed_limit = max(1, int(per_feed_raw))
    except ValueError:
        per_feed_limit = 50

    exclude = _exclude_keywords()
    include = _include_keywords()

    items: list[NewsItem] = []
    for url in urls:
        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": "ai-daily-brief"})
            resp.raise_for_status()
        except requests.RequestException:
            continue

        feed = feedparser.parse(resp.content)
        source = _source_label(feed.feed, url)

        for entry in feed.entries[:per_feed_limit]:
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            if not title or not link:
                continue
            haystack = _entry_text(entry)
            if include and not any(keyword in haystack for keyword in include):
                continue
            if exclude and any(keyword in haystack for keyword in exclude):
                continue
            link = _normalize_url(link)
            items.append(
                NewsItem(
                    title=title,
                    url=link,
                    published_at=_parse_datetime(entry),
                    source=source,
                    summary=_entry_summary(entry),
                    source_url=url,
                )
            )

    items = _dedupe(items)
    min_ts = dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    items.sort(key=lambda x: x.published_at or min_ts, reverse=True)
    return items

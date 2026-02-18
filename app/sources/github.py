from __future__ import annotations

import datetime as dt
import os
from typing import Any

import requests

from app.models import GithubProject


_DEFAULT_EXCLUDE_KEYWORDS = (
    "course",
    "homework",
    "assignment",
    "lecture",
    "slides",
    "notes",
    "syllabus",
    "curriculum",
    "class",
    "school",
    "internship",
    "task",
    "lab",
    "project",
    "introduction",
    "academic",
    "courseware",
    "课程",
    "作业",
    "课件",
    "讲义",
    "笔记",
    "试卷",
    "习题",
    "课堂",
)


def _build_query() -> str:
    base = os.getenv("GITHUB_SEARCH_QUERY", "llm OR ai").strip()
    qualifiers = os.getenv("GITHUB_SEARCH_QUALIFIERS", "").strip()
    if qualifiers:
        base = f"{base} {qualifiers}"

    days_raw = os.getenv("GITHUB_SEARCH_DAYS", "30").strip()
    try:
        days = int(days_raw)
    except ValueError:
        days = 30

    if days <= 0:
        return base

    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).date().isoformat()
    return f"{base} created:>{since}"


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-daily-brief",
    }
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _log_request_error(msg: str) -> None:
    if os.getenv("GITHUB_DEBUG", "").strip().lower() in {"1", "true", "yes"}:
        print(msg)


def _exclude_keywords() -> tuple[str, ...]:
    raw = os.getenv("GITHUB_EXCLUDE_KEYWORDS", "").strip()
    if not raw:
        return _DEFAULT_EXCLUDE_KEYWORDS
    return tuple(k.strip().lower() for k in raw.split(",") if k.strip())


def _min_stars() -> int:
    raw = os.getenv("GITHUB_MIN_STARS", "1000").strip()
    try:
        return max(0, int(raw))
    except ValueError:
        return 0


def fetch_github_projects() -> list[GithubProject]:
    per_page_raw = os.getenv("GITHUB_SEARCH_PER_PAGE", "20").strip()
    try:
        per_page = max(1, min(50, int(per_page_raw)))
    except ValueError:
        per_page = 20

    params = {
        "q": _build_query(),
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
    }

    try:
        resp = requests.get(
            "https://api.github.com/search/repositories",
            params=params,
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        body = ""
        if getattr(exc, "response", None) is not None:
            try:
                body = exc.response.text[:300]
            except Exception:
                body = ""
        _log_request_error(f"github search failed status={status} body={body}")
        return []

    payload: dict[str, Any] = resp.json()
    items = payload.get("items", [])
    projects: list[GithubProject] = []

    min_stars = _min_stars()
    exclude = _exclude_keywords()

    for item in items:
        name = (item.get("full_name") or "").strip()
        url = (item.get("html_url") or "").strip()
        if not name or not url:
            continue
        stars = item.get("stargazers_count") or 0
        if stars < min_stars:
            continue
        description = item.get("description") or ""
        haystack = f"{name} {description}".lower()
        if any(keyword in haystack for keyword in exclude):
            continue

        projects.append(
            GithubProject(
                name=name,
                url=url,
                stars=stars,
                description=description,
            )
        )

    return projects

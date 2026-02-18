from __future__ import annotations

import datetime as dt
from collections import Counter
from typing import Iterable

from app.models import GithubProject, NewsItem


def _h(s: str) -> str:
    return s.replace("\n", " ").strip()


def _format_source_counts(news: list[NewsItem]) -> str:
    counts = Counter([n.source or "unknown" for n in news])
    if not counts:
        return ""
    parts = [f"{name} {count}" for name, count in counts.most_common()]
    return " / ".join(parts)


def _shorten(text: str, limit: int = 120) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _advantage_tags(text: str) -> str:
    haystack = text.lower()
    tags: list[str] = []
    tag_map = {
        "隐私": ["privacy", "private", "local", "on-device", "offline"],
        "可视化": ["visual", "visualization", "visualisation", "dashboard", "ui", "gui", "studio"],
        "效率": ["fast", "speed", "efficient", "performance", "accelerat", "optimiz"],
        "易部署": ["docker", "install", "setup", "deploy"],
        "成本": ["free", "cost", "cheap", "low-cost"],
        "开发": ["sdk", "api", "cli", "tool", "framework", "library", "workflow", "agent"],
        "安全": ["secure", "security", "safety"],
    }
    for tag, keys in tag_map.items():
        if any(k in haystack for k in keys):
            tags.append(tag)
        if len(tags) >= 3:
            break
    return "/".join(tags)


def _group_by_source(items: Iterable[NewsItem]) -> list[tuple[str, list[NewsItem]]]:
    groups: list[tuple[str, list[NewsItem]]] = []
    index: dict[str, int] = {}
    for item in items:
        source = item.source or "unknown"
        if source in index:
            groups[index[source]][1].append(item)
        else:
            index[source] = len(groups)
            groups.append((source, [item]))
    return groups


def _format_source_text(item: NewsItem) -> str:
    source = item.source or ""
    source_url = item.source_url or ""
    if not source:
        return ""
    if source_url:
        return f"来源：[{source}]({source_url})"
    return f"来源：{source}"


def _format_news_item(item: NewsItem, summary_limit: int = 60) -> str:
    title = _h(item.title)
    url = item.url
    summary = _h(item.summary or "")
    tags = _advantage_tags(f"{title} {summary}")
    source_text = _format_source_text(item)

    lines: list[str] = [f"- **[{title}]({url})**"]
    if summary:
        lines.append(f"  摘要：{_shorten(summary, summary_limit)}")
    if tags:
        lines.append(f"  优势：{tags}")
    if source_text:
        lines.append(f"  {source_text}")
    return "\n".join(lines)


def render_daily_brief(*, date: dt.date, news: list[NewsItem], projects: list[GithubProject]) -> str:
    max_news = 15
    max_projects = 10

    lines: list[str] = []
    news_count = len(news)
    project_count = len(projects)
    sources = _format_source_counts(news)

    lines.append("# AI Daily Brief")
    lines.append(f"> {date.isoformat()} · 新闻 {news_count} · GitHub {project_count}")
    lines.append("")

    lines.append("## 今日概览")
    summary_bits = [
        f"新闻 {news_count}",
        f"GitHub {project_count}",
        f"筛选：30 天 / 1000 星 / Top {max_projects}",
    ]
    if sources:
        summary_bits.insert(1, f"来源：{sources}")
    lines.append(f"**今日概览**：{'｜'.join(summary_bits)}")
    lines.append("")

    lines.append("## Top 3 推荐")
    if not news:
        lines.append("- (no items)")
    else:
        for idx, item in enumerate(news[:3], start=1):
            title = _h(item.title)
            url = item.url
            summary = _h(item.summary or "")
            tags = _advantage_tags(f"{title} {summary}")
            source_text = _format_source_text(item)

            lines.append(f"{idx}. **[{title}]({url})**")
            if summary:
                lines.append(f"   - 摘要：{_shorten(summary, 60)}")
            if tags:
                lines.append(f"   - 优势：{tags}")
            if source_text:
                lines.append(f"   - {source_text}")
    lines.append("")

    lines.append("## News")
    if not news:
        lines.append("- (no items)")
    else:
        selected_news = news[:max_news]
        for source, items in _group_by_source(selected_news):
            lines.append(f"### {source}")
            for item in items:
                lines.append(_format_news_item(item, summary_limit=40))
    lines.append("")

    lines.append("## GitHub Projects")
    if not projects:
        lines.append("- (no items)")
    else:
        for p in projects[:max_projects]:
            name = _h(p.name)
            url = p.url
            star = f" ⭐{p.stars}" if p.stars is not None else ""
            desc = _h(p.description or "")
            tags = _advantage_tags(f"{name} {desc}")

            lines.append(f"- **[{name}]({url})**{star}")
            if desc:
                lines.append(f"  描述：{_shorten(desc, 80)}")
            if tags:
                lines.append(f"  优势：{tags}")

    lines.append("")
    return "\n".join(lines)

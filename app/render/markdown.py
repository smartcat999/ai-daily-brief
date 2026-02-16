from __future__ import annotations

import datetime as dt

from app.models import GithubProject, NewsItem


def _h(s: str) -> str:
    return s.replace("\n", " ").strip()


def render_daily_brief(*, date: dt.date, news: list[NewsItem], projects: list[GithubProject]) -> str:
    lines: list[str] = []
    lines.append(f"# AI Daily Brief ({date.isoformat()})")
    lines.append("")

    lines.append("## News")
    if not news:
        lines.append("- (no items)")
    else:
        for n in news[:20]:
            title = _h(n.title)
            url = n.url
            lines.append(f"- [{title}]({url})")
    lines.append("")

    lines.append("## GitHub Projects")
    if not projects:
        lines.append("- (no items)")
    else:
        for p in projects[:20]:
            name = _h(p.name)
            url = p.url
            star = f" ⭐{p.stars}" if p.stars is not None else ""
            desc = f" — {_h(p.description)}" if p.description else ""
            lines.append(f"- [{name}]({url}){star}{desc}")

    lines.append("")
    return "\n".join(lines)

from __future__ import annotations

import datetime as dt
from pathlib import Path

from dotenv import load_dotenv

from app.sources.github import fetch_github_projects
from app.sources.rss import fetch_rss_items
from app.render.markdown import render_daily_brief
from app.push.wecom import push_wecom_markdown


OUTPUT_DIR = Path("data/output")


def run_now(date: dt.date | None = None) -> Path:
    load_dotenv()
    date = date or dt.date.today()

    news = fetch_rss_items()
    projects = fetch_github_projects()

    md = render_daily_brief(date=date, news=news, projects=projects)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"daily-brief-{date.isoformat()}.md"
    out_path.write_text(md, encoding="utf-8")

    # Push to WeCom if configured; otherwise no-op.
    push_wecom_markdown(md)

    return out_path


if __name__ == "__main__":
    from app.__main__ import main

    raise SystemExit(main())

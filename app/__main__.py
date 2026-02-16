from __future__ import annotations

import argparse
import datetime as dt

from .main import run_now


def _parse_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ai-daily-brief")
    p.add_argument("cmd", nargs="?", default="run-now", choices=["run-now"])
    p.add_argument("--date", type=_parse_date, default=None)
    args = p.parse_args(argv)

    if args.cmd == "run-now":
        out = run_now(date=args.date)
        print(str(out))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

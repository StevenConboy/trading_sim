"""Earnings calendar from Nasdaq's public JSON (no API key).

Source: https://api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD
One call per date. Each row has a symbol and a "time" field:
  time-pre-market   -> bmo (before open)
  time-after-hours  -> amc (after close)
  anything else     -> unknown (never traded)
The host must be on the environment's network allow-list.
"""
from __future__ import annotations

import datetime as dt
import json
import os

import net

URL = "https://api.nasdaq.com/api/calendar/earnings"
ALLOWED = frozenset({"api.nasdaq.com"})
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)", "Accept": "application/json, text/plain, */*"}
TIMING = {"time-pre-market": "bmo", "time-after-hours": "amc"}
REFRESH_DAYS = 7
LOOKAHEAD_DAYS = 21


def parse_day(payload: dict, day: dt.date, watch: set[str]) -> list[dict]:
    rows = ((payload or {}).get("data") or {}).get("rows") or []
    out = []
    for r in rows:
        sym = (r.get("symbol") or "").strip().upper()
        if sym in watch:
            out.append({"ticker": sym, "date": day.isoformat(),
                        "when": TIMING.get((r.get("time") or "").strip(), "unknown"),
                        "raw_time": r.get("time")})
    return out


def fetch_day(day: dt.date, watch: set[str]) -> list[dict]:
    return parse_day(net.request("GET", URL, ALLOWED, params={"date": day.isoformat()}, headers=HEADERS),
                     day, watch)


def refresh(start: dt.date, watch: set[str], days: int = LOOKAHEAD_DAYS) -> dict:
    events, d = [], start
    while d <= start + dt.timedelta(days=days):
        if d.weekday() < 5:
            events += fetch_day(d, watch)
        d += dt.timedelta(days=1)
    return {"source": URL, "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "from": start.isoformat(), "to": (start + dt.timedelta(days=days)).isoformat(), "events": events}


def is_stale(cache: dict | None, today: dt.date) -> bool:
    if not cache or not cache.get("fetched_at"):
        return True
    fetched = dt.datetime.fromisoformat(cache["fetched_at"]).date()
    return (today - fetched).days >= REFRESH_DAYS or dt.date.fromisoformat(cache["to"]) < today + dt.timedelta(days=2)


def load(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def save(path: str, cache: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cache, f, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def still_scheduled(ticker: str, day: dt.date, when: str, fresh: list[dict]) -> str | None:
    """None if `fresh` (today's re-fetch of `day`) still has the report; else why not."""
    match = [e for e in fresh if e["ticker"] == ticker]
    if not match:
        return f"{ticker} no longer listed for {day} (date moved?)"
    if match[0]["when"] != when:
        return f"{ticker} timing changed from {when} to {match[0]['when']}"
    return None

"""Load config.yaml, calendar.yaml and watchlist.yaml."""
from __future__ import annotations

import datetime as dt
import os
from decimal import Decimal

import yaml

from chain import Rules
from timing import MacroEvent

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name: str) -> dict:
    with open(os.path.join(HERE, name)) as f:
        return yaml.safe_load(f) or {}


def _t(x: str) -> dt.time:
    h, m = str(x).split(":")
    return dt.time(int(h), int(m))


def config() -> dict:
    c = _load("config.yaml")
    c["rules"] = Rules(start=Decimal(str(c["start_balance"])), target=Decimal(str(c["target"])),
                       win_multiple=Decimal(str(c["win_multiple"])), slippage=Decimal(str(c["slippage"])))
    c["windows"] = {k: (_t(a), _t(b)) for k, (a, b) in c["windows"].items()}
    return c


def macro_events(cal: dict | None = None) -> tuple[list[MacroEvent], list[str]]:
    """(events, warnings). A warning for every list that is still empty (TODO)."""
    cal = cal if cal is not None else _load("calendar.yaml")
    out, warn = [], []
    for kind in ("cpi", "jobs", "fed"):
        dates = (cal.get(kind) or {}).get("dates") or []
        if not dates:
            warn.append(f"calendar.yaml: no {kind} dates (TODO), {kind} events never trade")
        for d in dates:
            out.append(MacroEvent(kind, d if isinstance(d, dt.date) else dt.date.fromisoformat(str(d))))
    return out, warn


def watchlist() -> list[str]:
    return [t.upper() for t in _load("watchlist.yaml")["tickers"]]

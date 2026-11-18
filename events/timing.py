"""Market-calendar logic: which events qualify on which day, and when.

Pure functions only (no network). The market calendar comes from Alpaca's
/v2/calendar at run time and from a fake in the tests.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Iterable

NORMAL_CLOSE = dt.time(16, 0)
ONE_DAY = dt.timedelta(days=1)


@dataclass(frozen=True)
class Session:
    date: dt.date
    open: dt.time
    close: dt.time


class MarketCalendar:
    """Trading sessions over a window of dates. Days not listed are closed."""

    def __init__(self, sessions: Iterable[Session], first: dt.date, last: dt.date):
        self.sessions = {s.date: s for s in sessions}
        self.first, self.last = first, last

    @classmethod
    def from_alpaca(cls, rows: list[dict], first: dt.date, last: dt.date) -> "MarketCalendar":
        def t(x: str) -> dt.time:
            h, m = x.split(":")[:2]
            return dt.time(int(h), int(m))
        return cls((Session(dt.date.fromisoformat(r["date"]), t(r["open"]), t(r["close"])) for r in rows),
                   first, last)

    def _covered(self, d: dt.date) -> None:
        if not (self.first <= d <= self.last):
            raise ValueError(f"{d} is outside the loaded market calendar {self.first}..{self.last}")

    def is_trading_day(self, d: dt.date) -> bool:
        self._covered(d)
        return d in self.sessions

    def is_normal_day(self, d: dt.date) -> bool:
        """A full session (closes 4:00 p.m. ET). Early-close days are not normal."""
        return self.is_trading_day(d) and self.sessions[d].close == NORMAL_CLOSE

    def next_trading_day(self, d: dt.date) -> dt.date | None:
        x = d + ONE_DAY
        while x <= self.last:
            if x in self.sessions:
                return x
            x += ONE_DAY
        return None

    def prev_trading_day(self, d: dt.date) -> dt.date | None:
        x = d - ONE_DAY
        while x >= self.first:
            if x in self.sessions:
                return x
            x -= ONE_DAY
        return None


def overnight_problem(entry: dt.date, cal: MarketCalendar) -> str | None:
    """Why an overnight trade bought on `entry` can't be made, or None if it can.

    Bought 3:15 p.m. on `entry`, sold 9:45 a.m. and 3:15 p.m. on the next
    session. That next session must be the very next calendar day (no weekend
    or holiday in between) and both days must be full sessions.
    """
    if not cal.is_trading_day(entry):
        return f"{entry} ({entry:%a}) is not a trading day"
    if not cal.is_normal_day(entry):
        return f"{entry} closes early ({cal.sessions[entry].close:%H:%M} ET)"
    nxt = cal.next_trading_day(entry)
    if nxt is None:
        return f"no trading day after {entry} in the loaded calendar"
    if nxt != entry + ONE_DAY:
        return (f"would be held over a weekend/holiday: next session after {entry} ({entry:%a}) "
                f"is {nxt} ({nxt:%a})")
    if not cal.is_normal_day(nxt):
        return f"exit day {nxt} closes early ({cal.sessions[nxt].close:%H:%M} ET)"
    return None


@dataclass
class Candidate:
    """An event that qualifies for a bet on a given run."""
    kind: str                 # cpi | jobs | earnings | fed
    ticker: str               # SPY for macro, the stock for earnings
    event_date: dt.date
    when: str                 # "08:30", "14:00", "bmo" or "amc"
    entry_day: dt.date
    exit_day: dt.date
    expiry_on_or_after: dt.date
    exact_expiry: bool        # SPY macro / Fed: must expire exactly on the event day
    notes: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return f"{self.kind}:{self.ticker}:{self.event_date.isoformat()}"

    @property
    def overnight(self) -> bool:
        return self.exit_day != self.entry_day

    def label(self) -> str:
        names = {"cpi": "CPI 8:30", "jobs": "jobs report 8:30", "fed": "Fed decision 2:00"}
        if self.kind == "earnings":
            return f"{self.ticker} earnings {'before open' if self.when == 'bmo' else 'after close'} {self.event_date}"
        return f"{names[self.kind]} {self.event_date}"


@dataclass(frozen=True)
class MacroEvent:
    kind: str        # cpi | jobs | fed
    date: dt.date


@dataclass(frozen=True)
class EarningsEvent:
    ticker: str
    date: dt.date
    when: str        # bmo | amc | unknown


def buy_run_candidates(today: dt.date, cal: MarketCalendar, macro: Iterable[MacroEvent],
                       earnings: Iterable[EarningsEvent], spy: str = "SPY"
                       ) -> tuple[list[Candidate], list[str]]:
    """Events the 3:15 p.m. buy run on `today` may bet on, plus skip reasons.

    - CPI / jobs at 8:30 tomorrow: buy today, SPY expiring the event day.
    - Earnings after close today: buy today, nearest expiry after the report.
    - Earnings before open tomorrow: buy today, nearest expiry on/after that day.
    Every one is an overnight hold, so `overnight_problem` must be None.
    """
    cands: list[Candidate] = []
    skipped: list[str] = []
    if not cal.is_trading_day(today):
        return [], [f"{today} ({today:%a}) is not a trading day"]
    nxt = cal.next_trading_day(today)
    problem = overnight_problem(today, cal)
    tomorrow = today + ONE_DAY
    # Events that land before the next session's close: tomorrow, or any day up
    # to the next session (so a Monday event seen on Friday is logged as skipped).
    horizon = nxt or tomorrow

    for ev in macro:
        if ev.kind not in ("cpi", "jobs") or not (today < ev.date <= horizon):
            continue
        c = Candidate(ev.kind, spy, ev.date, "08:30", today, ev.date, ev.date, True)
        if ev.date != tomorrow:
            skipped.append(f"{c.label()}: entry would be the day before ({ev.date - ONE_DAY}), "
                           f"not a market day; would be held over a weekend/holiday")
        elif problem:
            skipped.append(f"{c.label()}: {problem}")
        elif not cal.is_trading_day(ev.date):
            skipped.append(f"{c.label()}: event day is not a trading day")
        else:
            cands.append(c)

    for ev in earnings:
        if ev.when == "amc" and ev.date == today:
            c = Candidate("earnings", ev.ticker, ev.date, "amc", today, nxt or tomorrow, tomorrow, False)
        elif ev.when == "bmo" and today < ev.date <= horizon:
            c = Candidate("earnings", ev.ticker, ev.date, "bmo", today, ev.date, ev.date, False)
            if ev.date != tomorrow:
                skipped.append(f"{c.label()}: day before is not a market day; would be held over a weekend/holiday")
                continue
        elif ev.when not in ("amc", "bmo") and today <= ev.date <= horizon:
            skipped.append(f"{ev.ticker} earnings {ev.date}: report time not published (not before open / after close)")
            continue
        else:
            continue
        if problem:
            skipped.append(f"{c.label()}: {problem}")
        else:
            cands.append(c)
    return cands, skipped


def fed_candidate(today: dt.date, cal: MarketCalendar, macro: Iterable[MacroEvent],
                  spy: str = "SPY") -> tuple[Candidate | None, str | None]:
    """The Fed decision-day bet: buy 1:45 p.m., SPY same-day expiry, close 3:15 p.m."""
    if not any(ev.kind == "fed" and ev.date == today for ev in macro):
        return None, f"{today} is not a Fed decision day in calendar.yaml"
    if not cal.is_trading_day(today):
        return None, f"Fed decision day {today} is not a trading day"
    if not cal.is_normal_day(today):
        return None, f"Fed decision day {today} closes early"
    return Candidate("fed", spy, today, "14:00", today, today, today, True), None


def in_window(now: dt.time, start: dt.time, end: dt.time) -> bool:
    return start <= now <= end

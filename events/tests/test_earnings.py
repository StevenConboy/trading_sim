import datetime as dt

import earnings

PAYLOAD = {"data": {"asOf": "Wed, Nov 18, 2026", "rows": [
    {"symbol": "NVDA", "time": "time-after-hours", "name": "NVIDIA"},
    {"symbol": "WMT", "time": "time-pre-market", "name": "Walmart"},
    {"symbol": "TGT", "time": "time-not-supplied", "name": "Target"},
    {"symbol": "ZZZZ", "time": "time-after-hours", "name": "Not watched"},
]}, "status": {"rCode": 200}}
WATCH = {"NVDA", "WMT", "TGT"}
DAY = dt.date(2026, 11, 18)


def test_parse_day_filters_and_maps_timing():
    rows = earnings.parse_day(PAYLOAD, DAY, WATCH)
    assert {(r["ticker"], r["when"]) for r in rows} == {("NVDA", "amc"), ("WMT", "bmo"), ("TGT", "unknown")}


def test_parse_day_empty_and_null():
    assert earnings.parse_day({"data": {"rows": None}}, DAY, WATCH) == []
    assert earnings.parse_day({"data": None}, DAY, WATCH) == []
    assert earnings.parse_day(None, DAY, WATCH) == []


def test_still_scheduled():
    fresh = earnings.parse_day(PAYLOAD, DAY, WATCH)
    assert earnings.still_scheduled("NVDA", DAY, "amc", fresh) is None
    assert "no longer listed" in earnings.still_scheduled("AAPL", DAY, "amc", fresh)
    assert "timing changed" in earnings.still_scheduled("WMT", DAY, "amc", fresh)


def test_weekly_staleness():
    fresh = {"fetched_at": "2026-11-16T12:00:00+00:00", "to": "2026-12-07"}
    assert not earnings.is_stale(fresh, dt.date(2026, 11, 18))
    assert earnings.is_stale(fresh, dt.date(2026, 11, 23))      # 7 days later
    assert earnings.is_stale(None, DAY)
    assert earnings.is_stale({"fetched_at": "2026-11-17T00:00:00+00:00", "to": "2026-11-19"}, DAY)  # window ran out

import datetime as dt

from timing import (EarningsEvent, MacroEvent, MarketCalendar, Session, buy_run_candidates,
                    fed_candidate, overnight_problem)

D = dt.date
FULL = (dt.time(9, 30), dt.time(16, 0))
HALF = (dt.time(9, 30), dt.time(13, 0))
# Nov 2026: Thanksgiving Thu 26 closed, Fri 27 early close. Dec 25 (Fri) closed.
HOLIDAYS = {D(2026, 11, 26), D(2026, 12, 25), D(2027, 1, 1)}
EARLY = {D(2026, 11, 27), D(2026, 12, 24)}


def make_cal(first=D(2026, 11, 1), last=D(2027, 1, 31)):
    sessions, d = [], first
    while d <= last:
        if d.weekday() < 5 and d not in HOLIDAYS:
            o, c = HALF if d in EARLY else FULL
            sessions.append(Session(d, o, c))
        d += dt.timedelta(days=1)
    return MarketCalendar(sessions, first, last)


CAL = make_cal()


def test_calendar_basics():
    assert CAL.is_trading_day(D(2026, 11, 18))
    assert not CAL.is_trading_day(D(2026, 11, 21))       # Saturday
    assert not CAL.is_trading_day(D(2026, 11, 26))       # Thanksgiving
    assert CAL.is_trading_day(D(2026, 11, 27)) and not CAL.is_normal_day(D(2026, 11, 27))
    assert CAL.next_trading_day(D(2026, 11, 20)) == D(2026, 11, 23)
    assert CAL.next_trading_day(D(2026, 11, 25)) == D(2026, 11, 27)
    assert CAL.prev_trading_day(D(2026, 11, 23)) == D(2026, 11, 20)


def test_overnight_weekday_ok():
    assert overnight_problem(D(2026, 11, 18), CAL) is None   # Wed -> Thu


def test_overnight_over_weekend_skipped():
    assert "weekend/holiday" in overnight_problem(D(2026, 11, 20), CAL)   # Fri -> Mon


def test_overnight_over_holiday_skipped():
    assert "weekend/holiday" in overnight_problem(D(2026, 11, 25), CAL)   # Wed -> (Thanksgiving) -> Fri
    assert "weekend/holiday" in overnight_problem(D(2026, 12, 31), CAL)   # Thu -> (New Year) -> Mon


def test_overnight_into_early_close_skipped():
    assert "closes early" in overnight_problem(D(2026, 12, 23), CAL)      # Wed -> Thu 24 half day


def test_overnight_from_non_trading_day():
    assert "not a trading day" in overnight_problem(D(2026, 11, 22), CAL)


def test_cpi_tomorrow_qualifies():
    cands, skipped = buy_run_candidates(D(2026, 12, 9), CAL, [MacroEvent("cpi", D(2026, 12, 10))], [])
    assert [c.id for c in cands] == ["cpi:SPY:2026-12-10"]
    c = cands[0]
    assert c.entry_day == D(2026, 12, 9) and c.exit_day == D(2026, 12, 10)
    assert c.expiry_on_or_after == D(2026, 12, 10) and c.exact_expiry and c.overnight


def test_cpi_today_or_later_is_not_a_candidate_today():
    cands, _ = buy_run_candidates(D(2026, 12, 8), CAL, [MacroEvent("cpi", D(2026, 12, 10))], [])
    assert cands == []
    cands, _ = buy_run_candidates(D(2026, 12, 10), CAL, [MacroEvent("cpi", D(2026, 12, 10))], [])
    assert cands == []


def test_jobs_monday_seen_friday_skipped_for_weekend():
    cands, skipped = buy_run_candidates(D(2026, 12, 4), CAL, [MacroEvent("jobs", D(2026, 12, 7))], [])
    assert cands == [] and "weekend/holiday" in skipped[0]


def test_jobs_friday_bought_thursday():
    cands, _ = buy_run_candidates(D(2026, 12, 3), CAL, [MacroEvent("jobs", D(2026, 12, 4))], [])
    assert cands and cands[0].exit_day == D(2026, 12, 4)


def test_macro_on_market_holiday_skipped():
    # Release on a day the market is shut (e.g. a Friday holiday): nothing to sell into.
    cands, skipped = buy_run_candidates(D(2026, 12, 24), CAL, [MacroEvent("jobs", D(2026, 12, 25))], [])
    assert cands == [] and skipped


def test_fed_ignored_by_buy_run():
    cands, skipped = buy_run_candidates(D(2026, 12, 15), CAL, [MacroEvent("fed", D(2026, 12, 16))], [])
    assert cands == [] and skipped == []


def test_earnings_after_close_today():
    cands, _ = buy_run_candidates(D(2026, 11, 18), CAL, [], [EarningsEvent("NVDA", D(2026, 11, 18), "amc")])
    c = cands[0]
    assert c.id == "earnings:NVDA:2026-11-18" and c.entry_day == D(2026, 11, 18)
    assert c.exit_day == D(2026, 11, 19)
    assert c.expiry_on_or_after == D(2026, 11, 19) and not c.exact_expiry


def test_earnings_after_close_friday_skipped():
    cands, skipped = buy_run_candidates(D(2026, 11, 20), CAL, [], [EarningsEvent("X", D(2026, 11, 20), "amc")])
    assert cands == [] and "weekend/holiday" in skipped[0]


def test_earnings_before_open_tomorrow():
    cands, _ = buy_run_candidates(D(2026, 11, 18), CAL, [], [EarningsEvent("WMT", D(2026, 11, 19), "bmo")])
    c = cands[0]
    assert c.entry_day == D(2026, 11, 18) and c.exit_day == D(2026, 11, 19)
    assert c.expiry_on_or_after == D(2026, 11, 19)


def test_earnings_before_open_monday_skipped():
    cands, skipped = buy_run_candidates(D(2026, 11, 20), CAL, [], [EarningsEvent("X", D(2026, 11, 23), "bmo")])
    assert cands == [] and "weekend/holiday" in skipped[0]


def test_earnings_before_open_today_is_too_late():
    cands, _ = buy_run_candidates(D(2026, 11, 18), CAL, [], [EarningsEvent("X", D(2026, 11, 18), "bmo")])
    assert cands == []


def test_earnings_unknown_time_skipped():
    cands, skipped = buy_run_candidates(D(2026, 11, 18), CAL, [], [EarningsEvent("X", D(2026, 11, 18), "unknown")])
    assert cands == [] and "not published" in skipped[0]


def test_earnings_before_thanksgiving_skipped():
    cands, skipped = buy_run_candidates(D(2026, 11, 25), CAL, [], [EarningsEvent("X", D(2026, 11, 25), "amc")])
    assert cands == [] and skipped


def test_several_candidates_same_night():
    cands, _ = buy_run_candidates(
        D(2026, 12, 9), CAL, [MacroEvent("cpi", D(2026, 12, 10))],
        [EarningsEvent("ORCL", D(2026, 12, 9), "amc"), EarningsEvent("ADBE", D(2026, 12, 10), "bmo")])
    assert {c.ticker for c in cands} == {"SPY", "ORCL", "ADBE"}


def test_non_trading_day_has_no_candidates():
    cands, skipped = buy_run_candidates(D(2026, 11, 21), CAL, [MacroEvent("cpi", D(2026, 11, 22))], [])
    assert cands == [] and "not a trading day" in skipped[0]


def test_fed_candidate():
    c, why = fed_candidate(D(2026, 12, 16), CAL, [MacroEvent("fed", D(2026, 12, 16))])
    assert why is None and c.entry_day == c.exit_day == c.expiry_on_or_after == D(2026, 12, 16)
    assert c.exact_expiry and not c.overnight


def test_fed_not_today():
    c, why = fed_candidate(D(2026, 12, 15), CAL, [MacroEvent("fed", D(2026, 12, 16))])
    assert c is None and "not a Fed decision day" in why


def test_fed_on_early_close_skipped():
    c, why = fed_candidate(D(2026, 12, 24), CAL, [MacroEvent("fed", D(2026, 12, 24))])
    assert c is None and "early" in why


def test_calendar_window_guard():
    import pytest
    with pytest.raises(ValueError):
        CAL.is_trading_day(D(2030, 1, 2))

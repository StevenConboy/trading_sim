"""End-to-end runs of buy / sell / fed with Alpaca and Nasdaq faked out.

Nothing here touches the network: every alpaca/earnings call is replaced.
"""
import datetime as dt
import json
import math
from decimal import Decimal as D
from zoneinfo import ZoneInfo

import pytest

import alpaca
import earnings
import run
import settings
from strikes import OptionQuote
from timing import MacroEvent

ET = ZoneInfo("America/New_York")
HOLIDAYS = {dt.date(2026, 11, 26), dt.date(2026, 12, 25), dt.date(2027, 1, 1)}


def cal_rows(start, end):
    out, d = [], start
    while d <= end:
        if d.weekday() < 5 and d not in HOLIDAYS:
            out.append({"date": d.isoformat(), "open": "09:30",
                        "close": "13:00" if d == dt.date(2026, 11, 27) else "16:00"})
        d += dt.timedelta(days=1)
    return out


def fake_chain(ticker, expiry, spot=600.0, scale=3.0, extra=0.0):
    out = []
    for k in range(int(spot) - 20, int(spot) + 21):
        for kind in ("call", "put"):
            intrinsic = max(0.0, spot - k) if kind == "call" else max(0.0, k - spot)
            ask = round(intrinsic + scale * math.exp(-abs(k - spot) / scale) + 0.02 + extra, 2)
            bid = max(0.0, round(ask - 0.04, 2))
            sym = f"{ticker}{expiry:%y%m%d}{'C' if kind == 'call' else 'P'}{k * 1000:08d}"
            out.append(OptionQuote(sym, kind, D(k), expiry, D(str(bid)), D(str(ask))))
    return out


class Fake:
    def __init__(self):
        self.orders = []          # (symbol, qty, side, price, cid)
        self.held = {}            # symbol -> qty
        self.fill = True
        self.bid = {}             # symbol -> bid for exits
        self.change = D("0.8")
        self.macro = []
        self.earnings = []        # cached rows
        self.fresh = None         # rows returned by today's re-check (None -> same as cache)

    def limit_and_wait(self, symbol, qty, side, price, cid, wait, log):
        self.orders.append((symbol, qty, side, price, cid))
        if not self.fill:
            return 0, None, {"status": "canceled", "filled_qty": "0"}
        self.held[symbol] = self.held.get(symbol, 0) + (qty if side == "buy" else -qty)
        if not self.held[symbol]:
            del self.held[symbol]
        return qty, price, {"status": "filled", "filled_qty": str(qty)}


@pytest.fixture
def fake(tmp_path, monkeypatch):
    f = Fake()
    monkeypatch.setattr(run, "LEDGER_PATH", str(tmp_path / "ledger.json"))
    monkeypatch.setattr(run, "EARNINGS_PATH", str(tmp_path / "earnings.json"))
    monkeypatch.setattr(run, "LOG_PATH", str(tmp_path / "run.log"))
    monkeypatch.setattr(alpaca, "require_paper", lambda: {"account_number": "PA0", "status": "ACTIVE"})
    monkeypatch.setattr(alpaca, "calendar", cal_rows)
    monkeypatch.setattr(alpaca, "positions", lambda: [
        {"symbol": s, "qty": str(q), "asset_class": "us_option"} for s, q in f.held.items()])
    monkeypatch.setattr(alpaca, "spot_and_change", lambda t: (D(600), f.change))
    monkeypatch.setattr(alpaca, "expiries", lambda t, d: [d, d + dt.timedelta(days=1)])
    monkeypatch.setattr(alpaca, "option_chain", fake_chain)
    monkeypatch.setattr(alpaca, "quote", lambda s: (f.bid.get(s, D("0.50")), f.bid.get(s, D("0.50")) + D("0.05")))
    monkeypatch.setattr(alpaca, "limit_and_wait", f.limit_and_wait)
    monkeypatch.setattr(settings, "macro_events", lambda: (f.macro, []))
    monkeypatch.setattr(earnings, "load", lambda p: {"fetched_at": "2026-12-08T00:00:00+00:00",
                                                     "to": "2027-01-31", "events": f.earnings})
    monkeypatch.setattr(earnings, "fetch_day", lambda d, w: f.fresh if f.fresh is not None else
                        [e for e in f.earnings if e["date"] == d.isoformat()])
    return f


def go(monkeypatch, when, *argv):
    t = dt.datetime.fromisoformat(when).replace(tzinfo=ET)
    monkeypatch.setattr(run.Run, "_now", lambda self, args: t)
    return run.main(list(argv))


def ledger():
    with open(run.LEDGER_PATH) as f:
        return json.load(f)


def test_cpi_overnight_full_cycle(fake, monkeypatch):
    fake.macro = [MacroEvent("cpi", dt.date(2026, 12, 10))]
    assert go(monkeypatch, "2026-12-09T15:16", "buy") == 0
    (sym, qty, side, price, cid), = fake.orders
    # spot 600, ATM straddle ~6.0 -> first call strike beyond 606 is 607 (momentum +0.8% -> call)
    assert sym == "SPY261210C00607000" and side == "buy" and cid == "evt-claude-20261209-buy"
    assert price == D("0.31") and qty == 2          # $100 / (0.31 * 100 * 1.15) = 2.8
    L = ledger()
    c, s = L["chains"]["claude"], L["chains"]["shadow"]
    assert c["balance"] == "28.70" and c["step"] == 1 and c["open"]
    assert s["step"] == 1 and s["open"]             # shadow booked at the quote, no order
    tc = next(t for t in L["trades"] if t["chain"] == "claude")
    assert "momentum" in tc["reasoning"] and tc["event"].startswith("CPI")

    fake.bid = {sym: D("1.20")}
    assert go(monkeypatch, "2026-12-10T09:46", "sell") == 0
    assert fake.orders[-1] == (sym, 1, "sell", D("1.20"), "evt-claude-20261210-half")
    L = ledger()
    assert L["chains"]["claude"]["balance"] == "130.70"   # 28.70 + 1 x 120 x 0.85

    # Running sell twice does not sell another half.
    n = len(fake.orders)
    go(monkeypatch, "2026-12-10T09:50", "sell")
    assert len(fake.orders) == n

    fake.bid = {sym: D("0.10")}
    assert go(monkeypatch, "2026-12-10T15:16", "buy") == 0
    assert fake.orders[-1] == (sym, 1, "sell", D("0.10"), "evt-claude-20261210-close")
    L = ledger()
    c = L["chains"]["claude"]
    assert c["open"] is None and c["balance"] == "139.20"   # + 1 x 10 x 0.85
    tc = next(t for t in L["trades"] if t["chain"] == "claude")
    assert tc["status"] == "closed" and tc["balance_after"] == "139.20" and tc["haircut_value"] == "110.50"
    assert L["chains"]["shadow"]["open"] is None


def test_dry_run_sends_nothing_and_writes_nothing(fake, monkeypatch):
    fake.macro = [MacroEvent("cpi", dt.date(2026, 12, 10))]
    assert run.main(["buy", "--dry-run", "--at", "2026-12-09T15:16"]) == 0
    assert fake.orders == []
    assert not __import__("os").path.exists(run.LEDGER_PATH)


def test_at_requires_dry_run(fake):
    with pytest.raises(SystemExit):
        run.main(["buy", "--at", "2026-12-09T15:16"])


def test_time_window_enforced(fake, monkeypatch):
    with pytest.raises(SystemExit):
        go(monkeypatch, "2026-12-09T11:00", "buy")


def test_no_fill_logged(fake, monkeypatch):
    fake.macro = [MacroEvent("cpi", dt.date(2026, 12, 10))]
    fake.fill = False
    go(monkeypatch, "2026-12-09T15:16", "buy")
    L = ledger()
    assert L["chains"]["claude"]["open"] is None and L["chains"]["claude"]["step"] == 0
    assert any("no fill" in x["msg"] and "cancelled after 120s" in x["msg"] for x in L["log"])
    assert L["chains"]["shadow"]["open"]           # shadow still books its bet


def test_claude_override(fake, monkeypatch):
    fake.macro = [MacroEvent("cpi", dt.date(2026, 12, 10))]
    fake.earnings = [{"ticker": "ORCL", "date": "2026-12-09", "when": "amc"}]
    go(monkeypatch, "2026-12-09T15:16", "buy", "--event", "cpi", "--direction", "put", "--reason", "hot print")
    sym, *_ = fake.orders[0]
    assert sym == "SPY261210P00593000"
    t = next(t for t in ledger()["trades"] if t["chain"] == "claude")
    assert t["reasoning"] == "hot print" and t["direction"] == "put"


def test_ambiguous_direction_without_event(fake, monkeypatch):
    fake.macro = [MacroEvent("cpi", dt.date(2026, 12, 10))]
    fake.earnings = [{"ticker": "ORCL", "date": "2026-12-09", "when": "amc"}]
    with pytest.raises(SystemExit):
        go(monkeypatch, "2026-12-09T15:16", "buy", "--direction", "put", "--reason", "x")


def test_earnings_moved_on_recheck_is_skipped(fake, monkeypatch):
    fake.earnings = [{"ticker": "ORCL", "date": "2026-12-09", "when": "amc"}]
    fake.fresh = []        # gone from today's listing
    go(monkeypatch, "2026-12-09T15:16", "buy")
    assert fake.orders == []
    assert any("no longer listed" in x["msg"] for x in ledger()["log"])


def test_earnings_after_close_uses_next_expiry(fake, monkeypatch):
    fake.earnings = [{"ticker": "ORCL", "date": "2026-12-09", "when": "amc"}]
    go(monkeypatch, "2026-12-09T15:16", "buy")
    sym = fake.orders[0][0]
    assert sym.startswith("ORCL261210")       # first expiry after the report, not today's


def test_friday_after_close_not_held_over_weekend(fake, monkeypatch):
    fake.earnings = [{"ticker": "ORCL", "date": "2026-12-11", "when": "amc"}]
    go(monkeypatch, "2026-12-11T15:16", "buy")
    assert fake.orders == []
    assert any("weekend/holiday" in x["msg"] for x in ledger()["log"])


def test_fed_day(fake, monkeypatch):
    fake.macro = [MacroEvent("fed", dt.date(2026, 12, 16))]
    assert go(monkeypatch, "2026-12-16T13:46", "fed") == 0
    sym, qty, side, price, cid = fake.orders[0]
    assert sym.startswith("SPY261216") and cid == "evt-claude-20261216-fed" and side == "buy"
    t = next(t for t in ledger()["trades"] if t["chain"] == "claude")
    assert not t["overnight"] and t["exit_day"] == "2026-12-16"
    go(monkeypatch, "2026-12-16T15:16", "buy")      # 3:15 run closes it
    assert fake.orders[-1][2] == "sell" and fake.orders[-1][4] == "evt-claude-20261216-close"
    assert ledger()["chains"]["claude"]["open"] is None


def test_fed_skipped_while_overnight_bet_open(fake, monkeypatch):
    fake.macro = [MacroEvent("cpi", dt.date(2026, 12, 16)), MacroEvent("fed", dt.date(2026, 12, 16))]
    go(monkeypatch, "2026-12-15T15:16", "buy")
    n = len(fake.orders)
    go(monkeypatch, "2026-12-16T13:46", "fed")
    assert len(fake.orders) == n
    assert any("still open" in x["msg"] for x in ledger()["log"])


def test_fed_not_today(fake, monkeypatch):
    fake.macro = [MacroEvent("fed", dt.date(2026, 12, 16))]
    go(monkeypatch, "2026-12-15T13:46", "fed")
    assert fake.orders == []


def test_unknown_alpaca_position_blocks_claude_buy(fake, monkeypatch):
    fake.macro = [MacroEvent("cpi", dt.date(2026, 12, 10))]
    fake.held = {"SPY261209C00610000": 3}
    go(monkeypatch, "2026-12-09T15:16", "buy")
    assert fake.orders == []
    L = ledger()
    assert any("!= ledger" in x["msg"] for x in L["log"])
    assert L["chains"]["shadow"]["open"]          # shadow unaffected


def test_unaffordable_skip_and_bust_flow(fake, monkeypatch):
    fake.macro = [MacroEvent("cpi", dt.date(2026, 12, 10))]
    monkeypatch.setattr(alpaca, "option_chain", lambda t, e: fake_chain(t, e, extra=1.0))  # every ask > $0.87
    go(monkeypatch, "2026-12-09T15:16", "buy")
    assert fake.orders == []
    L = ledger()
    assert any("can't afford" in x["msg"] for x in L["log"])
    assert L["chains"]["claude"]["busts"] == 0


def test_weekly_earnings_refresh_writes_cache(fake, monkeypatch):
    monkeypatch.setattr(earnings, "load", lambda p: None)
    monkeypatch.setattr(earnings, "fetch_day", lambda d, w: [{"ticker": "NVDA", "date": d.isoformat(), "when": "amc"}]
                        if d == dt.date(2026, 12, 17) else [])
    go(monkeypatch, "2026-12-09T15:16", "buy")
    with open(run.EARNINGS_PATH) as f:
        cache = json.load(f)
    assert cache["events"] == [{"ticker": "NVDA", "date": "2026-12-17", "when": "amc"}]
    assert cache["from"] == "2026-12-09"


def test_earnings_source_down_still_trades_macro(fake, monkeypatch):
    fake.macro = [MacroEvent("cpi", dt.date(2026, 12, 10))]
    monkeypatch.setattr(earnings, "load", lambda p: None)

    def boom(d, w):
        raise OSError("Tunnel connection failed: 403")
    monkeypatch.setattr(earnings, "fetch_day", boom)
    go(monkeypatch, "2026-12-09T15:16", "buy")
    assert fake.orders and fake.orders[0][0].startswith("SPY")
    assert any("earnings refresh failed" in x["msg"] for x in ledger()["log"])


def test_test_trade_round_trip_leaves_ledger_alone(fake, monkeypatch):
    fake.bid = {}
    assert go(monkeypatch, "2026-12-09T10:30", "test-trade") == 0
    buy, sell = fake.orders
    assert buy[1:3] == (1, "buy") and buy[4].startswith("evt-test-20261209-1030-buy")
    assert sell[1:3] == (1, "sell") and sell[3] == D("0.50")
    assert fake.held == {}
    L = ledger()
    assert L["trades"] == [] and L["chains"]["claude"]["balance"] == "100.00"


def test_test_trade_refuses_with_open_position(fake, monkeypatch):
    fake.held = {"SPY261209C00610000": 1}
    with pytest.raises(SystemExit):
        go(monkeypatch, "2026-12-09T10:30", "test-trade")
    assert fake.orders == []

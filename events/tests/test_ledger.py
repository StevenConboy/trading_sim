import datetime as dt
from decimal import Decimal as D
from zoneinfo import ZoneInfo

import pytest

import chain as ch

R = ch.Rules()
ET = ZoneInfo("America/New_York")
T0 = dt.datetime(2026, 12, 9, 15, 15, tzinfo=ET)
T1 = dt.datetime(2026, 12, 10, 9, 45, tzinfo=ET)
T2 = dt.datetime(2026, 12, 10, 15, 15, tzinfo=ET)


def entry(ledger, chain="claude", qty=2, price="0.30", when=T0):
    return ch.record_entry(ledger, chain, when, event="CPI", event_id="cpi:SPY:2026-12-10", ticker="SPY",
                           direction="call", symbol="SPY261210C00607000", strike=D(607),
                           expiry=dt.date(2026, 12, 10), qty=qty, price=D(price), quote_ask=D(price),
                           reasoning="test", overnight=True, exit_day=dt.date(2026, 12, 10), r=R)


def test_new_ledger():
    L = ch.new_ledger(R)
    assert set(L["chains"]) == {"claude", "shadow"}
    assert L["chains"]["claude"] == {"balance": "100.00", "step": 0, "restarts": 0, "busts": 0,
                                     "targets_hit": 0, "open": None}


def test_entry_debits_haircut_cost_and_steps():
    L = ch.new_ledger(R)
    t = entry(L)
    c = L["chains"]["claude"]
    assert t["entry_value"] == "69.00"          # 2 x 0.30 x 100 x 1.15
    assert c["balance"] == "31.00" and c["step"] == 1 and c["open"] == t["id"]
    assert t["status"] == "open" and t["remaining"] == 2
    assert L["chains"]["shadow"]["balance"] == "100.00"   # chains are independent


def test_one_open_bet_at_a_time():
    L = ch.new_ledger(R)
    entry(L)
    with pytest.raises(RuntimeError):
        entry(L)


def test_exits_credit_haircut_value_and_close():
    L = ch.new_ledger(R)
    t = entry(L, qty=3, price="0.25")       # 3 x 25 x 1.15 = 86.25
    ch.record_exit(L, "claude", T1, 1, D("1.00"), R, how="half")
    assert t["remaining"] == 2 and t["status"] == "open"
    assert t["exit_value"] == "85.00"       # 1 x 1.00 x 100 x 0.85
    assert t["balance_after"] is None
    ch.record_exit(L, "claude", T2, 2, D("0.50"), R, how="close")
    c = L["chains"]["claude"]
    assert t["status"] == "closed" and t["haircut_value"] == "170.00"   # 85 + 2 x 50 x 0.85
    assert t["balance_after"] == c["balance"] == "183.75"   # 100 - 86.25 + 170
    assert t["profit"] == "83.75"
    assert c["open"] is None
    assert [x["qty"] for x in t["exits"]] == [1, 2]


def test_cannot_oversell():
    L = ch.new_ledger(R)
    entry(L)
    with pytest.raises(ValueError):
        ch.record_exit(L, "claude", T1, 3, D(1), R)


def test_bust_after_total_loss_restarts():
    L = ch.new_ledger(R)
    entry(L, qty=2, price="0.40")                       # 92.00 -> balance 8.00
    ch.record_exit(L, "claude", T2, 2, D(0), R)          # worthless
    c = L["chains"]["claude"]
    # $8 can still buy a cheap contract, so no bust yet
    assert c["balance"] == "8.00" and c["busts"] == 0
    # Next bet: ask 0.20 -> $23 a contract: $8 can't buy one -> bust, restart at $100, size 4
    n, why = ch.size_bet(L, "claude", D("0.20"), T2, R)
    assert c["busts"] == 1 and c["restarts"] == 1 and c["balance"] == "100.00" and c["step"] == 0
    assert n == 4 and why is None
    assert "BUST #1" in L["log"][-1]["msg"]


def test_bust_immediately_when_balance_below_cheapest_contract():
    L = ch.new_ledger(R)
    entry(L, qty=2, price="0.43")                       # 98.90 -> balance 1.10 < 1.15
    ch.record_exit(L, "claude", T2, 2, D(0), R)
    c = L["chains"]["claude"]
    assert c["busts"] == 1 and c["balance"] == "100.00" and c["step"] == 0
    t = L["trades"][-1]
    assert t["balance_after"] == "1.10"       # the trade shows what it left behind


def test_unaffordable_at_start_is_a_skip_not_a_bust():
    L = ch.new_ledger(R)
    n, why = ch.size_bet(L, "claude", D("2.00"), T0, R)
    assert n == 0 and "can't afford" in why
    assert L["chains"]["claude"]["busts"] == 0


def test_bust_then_still_unaffordable():
    L = ch.new_ledger(R)
    L["chains"]["claude"]["balance"] = "50.00"
    n, why = ch.size_bet(L, "claude", D("2.00"), T0, R)
    assert n == 0 and L["chains"]["claude"]["busts"] == 1 and L["chains"]["claude"]["balance"] == "100.00"


def test_restart_count_carried_on_trades():
    L = ch.new_ledger(R)
    L["chains"]["shadow"]["balance"] = "5.00"
    ch.size_bet(L, "shadow", D("0.30"), T0, R)
    t = entry(L, chain="shadow", qty=1)
    assert t["restarts"] == 1 and t["step"] == 1


def test_target_hit_restarts():
    L = ch.new_ledger(R)
    L["chains"]["claude"]["balance"] = "590000.00"
    entry(L, qty=10, price="1.00")
    ch.record_exit(L, "claude", T2, 10, D("50.00"), R)
    c = L["chains"]["claude"]
    assert c["targets_hit"] == 1 and c["balance"] == "100.00" and c["restarts"] == 1
    assert D(L["trades"][-1]["balance_after"]) >= R.target


def test_write_off():
    L = ch.new_ledger(R)
    t = entry(L)
    ch.write_off(L, "claude", T2, "expired", R)
    assert t["status"] == "closed" and t["haircut_value"] == "0.00"
    assert L["chains"]["claude"]["open"] is None


def test_trade_record_has_every_logged_field():
    L = ch.new_ledger(R)
    t = entry(L)
    for k in ("date", "event", "ticker", "direction", "strike", "expiry", "contracts", "entry_price",
              "exits", "haircut_value", "balance_after", "step", "restarts", "reasoning"):
        assert k in t

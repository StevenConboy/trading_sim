import datetime as dt
from decimal import Decimal as D

import pytest

from strikes import OptionQuote, expected_move, parse_occ, pick_strike

EXP = dt.date(2026, 12, 10)


def q(kind, k, bid, ask):
    sym = f"SPY261210{'C' if kind == 'call' else 'P'}{int(D(k) * 1000):08d}"
    return OptionQuote(sym, kind, D(k), EXP, D(bid), D(ask))


CHAIN = [
    q("call", 595, "6.00", "6.10"), q("put", 595, "1.00", "1.10"),
    q("call", 600, "3.00", "3.10"), q("put", 600, "2.90", "3.00"),
    q("call", 605, "1.00", "1.10"), q("put", 605, "6.00", "6.10"),
    q("call", 606, "0.70", "0.75"), q("put", 594, "0.70", "0.75"),
    q("call", 607, "0.40", "0.45"), q("put", 593, "0.40", "0.45"),
    q("call", 608, "0.20", "0.25"), q("put", 592, "0.20", "0.25"),
]


def test_parse_occ():
    assert parse_occ("SPY261210C00600000") == ("SPY", EXP, "call", D(600))
    assert parse_occ("NVDA261121P00142500") == ("NVDA", dt.date(2026, 11, 21), "put", D("142.5"))


def test_expected_move_is_atm_straddle_mid():
    atm, move = expected_move(CHAIN, D("600.40"))
    assert atm == 600
    assert move == D("3.05") + D("2.95")   # call mid + put mid = 6.00


def test_atm_tie_goes_to_lower_strike():
    atm, _ = expected_move(CHAIN, D("602.50"))
    assert atm == 600


def test_expected_move_uses_ask_without_bid():
    chain = [q("call", 600, "0", "3.00"), q("put", 600, "0", "2.00")]
    assert expected_move(chain, D(600)) == (D(600), D(5))


def test_expected_move_none_without_pair():
    assert expected_move([q("call", 600, "1", "2")], D(600)) is None


def test_call_strike_first_beyond_move():
    # spot 600.40 + move 6.00 = 606.40 -> first call strike above is 607
    assert pick_strike(CHAIN, D("600.40"), D(6), "call").strike == 607


def test_put_strike_first_beyond_move():
    # 600.40 - 6.00 = 594.40 -> first put strike below is 594
    assert pick_strike(CHAIN, D("600.40"), D(6), "put").strike == 594


def test_strike_exactly_on_the_line_is_not_beyond():
    assert pick_strike(CHAIN, D(600), D(6), "call").strike == 607
    assert pick_strike(CHAIN, D(600), D(6), "put").strike == 593


def test_strike_without_ask_is_skipped():
    chain = CHAIN + [q("call", D("606.5"), "0", "0")]
    assert pick_strike(chain, D("600.40"), D(6), "call").strike == 607


def test_no_strike_beyond():
    assert pick_strike(CHAIN, D(600), D(50), "call") is None


def test_bad_direction():
    with pytest.raises(ValueError):
        pick_strike(CHAIN, D(600), D(6), "straddle")

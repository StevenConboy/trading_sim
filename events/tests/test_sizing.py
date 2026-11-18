from decimal import Decimal as D

import chain as ch

R = ch.Rules()


def test_stake_is_whole_balance_far_from_target():
    assert ch.stake(D(100), R) == D(100)


def test_stake_shrinks_near_target():
    # (600000 - 500000) / (5 - 1) = 25000
    assert ch.stake(D(500000), R) == D(25000)


def test_stake_zero_at_target():
    assert ch.stake(D(600000), R) == 0
    assert ch.stake(D(700000), R) == 0


def test_stake_uses_configured_multiple():
    r = ch.Rules(win_multiple=D(3))
    assert ch.stake(D(400000), r) == D(100000)  # (600000-400000)/2


def test_contracts_round_down_with_haircut():
    # ask 0.30 -> $30 * 1.15 = $34.50 a contract; $100 buys 2
    assert ch.contracts_for(D(100), D("0.30"), R) == 2
    # ask 0.29 -> $33.35; $100 buys 2 (2.99 rounded down)
    assert ch.contracts_for(D(100), D("0.29"), R) == 2
    # ask 0.28 -> $32.20; 3.1 -> 3
    assert ch.contracts_for(D(100), D("0.28"), R) == 3


def test_contracts_zero_when_unaffordable_or_bad_ask():
    assert ch.contracts_for(D(100), D("0.90"), R) == 0   # $103.50 > $100
    assert ch.contracts_for(D(100), D(0), R) == 0


def test_haircut_values():
    assert ch.buy_value(2, D("0.50"), R) == D("115.00")
    assert ch.sell_value(2, D("0.50"), R) == D("85.00")
    r = ch.Rules(slippage=D("0.10"))
    assert ch.sell_value(1, D("1"), r) == D("90.0")

import pytest

import alpaca
import earnings
import net


def test_dry_run_refuses_orders(monkeypatch):
    monkeypatch.setattr(net, "DRY_RUN", True)
    with pytest.raises(SystemExit, match="dry-run"):
        net.request("POST", alpaca.TRADING + "/v2/orders", alpaca.ALLOWED, body={})
    with pytest.raises(SystemExit, match="dry-run"):
        net.request("DELETE", alpaca.TRADING + "/v2/orders/x", alpaca.ALLOWED)


def test_host_allow_list():
    with pytest.raises(SystemExit, match="REFUSED"):
        net.request("GET", "https://api.alpaca.markets/v2/account", alpaca.ALLOWED)   # live host
    with pytest.raises(SystemExit, match="REFUSED"):
        net.request("GET", earnings.URL, alpaca.ALLOWED)
    with pytest.raises(SystemExit, match="REFUSED"):
        net.request("GET", "http://paper-api.alpaca.markets/v2/account", alpaca.ALLOWED)


def test_quote_freshness():
    import datetime as dt
    now = dt.datetime(2026, 11, 19, 14, 47, tzinfo=dt.timezone.utc)
    yesterday_close = "2026-11-18T21:14:59.00163899Z"
    assert alpaca.parse_ts(yesterday_close) == dt.datetime(2026, 11, 18, 21, 14, 59, 1638, tzinfo=dt.timezone.utc)
    assert not alpaca.is_fresh(yesterday_close, now, dt.timedelta(minutes=20))
    assert alpaca.is_fresh("2026-11-19T14:30:00Z", now, dt.timedelta(minutes=20))
    assert not alpaca.is_fresh("2026-11-19T14:26:59Z", now, dt.timedelta(minutes=20))
    assert not alpaca.is_fresh(None, now)

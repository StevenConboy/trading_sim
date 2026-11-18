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

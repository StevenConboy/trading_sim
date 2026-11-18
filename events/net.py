"""HTTPS with a per-module host allow-list, no auth headers, no redirects.

The code never holds or sends API keys: the environment's network proxy adds
them. A 401/403 stops the run and prints the exact response. In --dry-run,
any request other than GET is refused.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

DRY_RUN = False


class AuthStop(Exception):
    def __init__(self, method: str, url: str, status: int, body: str):
        super().__init__(f"HTTP {status} from {method} {url}")
        self.method, self.url, self.status, self.body = method, url, status, body


class ApiError(Exception):
    def __init__(self, method: str, url: str, status: int, body: str):
        super().__init__(f"HTTP {status} from {method} {url}: {body[:500]}")
        self.status, self.body = status, body


class Unreachable(Exception):
    """The host could not be reached (e.g. blocked by the environment's network policy)."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ApiError(req.get_method(), req.full_url, code, f"redirect to {newurl} refused")


_OPENER = urllib.request.build_opener(_NoRedirect())


def request(method: str, url: str, allowed: frozenset[str], params: dict | None = None,
            body: dict | None = None, headers: dict | None = None, timeout: float = 30):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in allowed or parts.port not in (None, 443):
        raise SystemExit(f"REFUSED: {url} is not one of the allowed hosts {sorted(allowed)}")
    if DRY_RUN and method != "GET":
        raise SystemExit(f"REFUSED in --dry-run: {method} {url}")
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    data = json.dumps(body).encode() if body is not None else None
    h = {"Accept": "application/json", "User-Agent": "trading-sim-events/1.0", **(headers or {})}
    if data is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        if e.code in (401, 403):
            raise AuthStop(method, url, e.code, raw) from None
        raise ApiError(method, url, e.code, raw) from None
    except urllib.error.URLError as e:
        raise Unreachable(f"{parts.hostname} unreachable ({e.reason}); if this is a proxy 403, the host "
                          "is not on this environment's network allow-list") from None
    return json.loads(raw) if raw.strip() else None

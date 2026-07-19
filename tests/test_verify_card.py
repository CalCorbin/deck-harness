"""Tests for verify_card.py — fetch, render, and report layers.

No real network calls: urllib.request.urlopen and time.sleep are patched via monkeypatch.
"""

import io
import json
import urllib.error

import verify_card


class FakeResponse:
    """Minimal context manager mimicking http.client.HTTPResponse for json.load()."""

    def __init__(self, payload):
        self._buf = io.BytesIO(json.dumps(payload).encode())

    def __enter__(self):
        return self._buf

    def __exit__(self, *exc_info):
        return False


def raising(exc):
    """Return a fake urlopen(req, timeout) that raises exc instead of hitting the network."""

    def fake_urlopen(req, timeout):
        raise exc

    return fake_urlopen


# ---------------------------------------------------------------------------
# fetch_card
# ---------------------------------------------------------------------------


def test_fetch_card_found(monkeypatch):
    card = {"name": "Sol Ring", "mana_cost": "{1}"}

    def fake_urlopen(req, timeout):
        return FakeResponse(card)

    monkeypatch.setattr(verify_card.urllib.request, "urlopen", fake_urlopen)

    found, data = verify_card.fetch_card("Sol Ring")

    assert (found, data) == (True, card)


def test_fetch_card_not_found(monkeypatch):
    fp = io.BytesIO(json.dumps({"details": 'perhaps you meant "Sol Ring"?'}).encode())
    error = urllib.error.HTTPError("url", 404, "Not Found", {}, fp)
    monkeypatch.setattr(verify_card.urllib.request, "urlopen", raising(error))

    found, data = verify_card.fetch_card("Sol Rign")

    assert (found, data) == (False, {"details": 'perhaps you meant "Sol Ring"?'})


def test_fetch_card_not_found_with_unparsable_body(monkeypatch):
    fp = io.BytesIO(b"not json")
    error = urllib.error.HTTPError("url", 404, "Not Found", {}, fp)
    monkeypatch.setattr(verify_card.urllib.request, "urlopen", raising(error))

    found, data = verify_card.fetch_card("Not A Card")

    assert (found, data) == (False, {"details": "not found"})


def test_fetch_card_retries_on_429_then_succeeds(monkeypatch):
    sleeps = []
    monkeypatch.setattr(verify_card.time, "sleep", lambda s: sleeps.append(s))

    attempts = {"count": 0}
    card = {"name": "Sol Ring"}

    def flaky(req, timeout):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise urllib.error.HTTPError("url", 429, "Too Many Requests", {}, io.BytesIO(b""))
        return FakeResponse(card)

    monkeypatch.setattr(verify_card.urllib.request, "urlopen", flaky)

    found, data = verify_card.fetch_card("Sol Ring")

    assert (found, data) == (True, card)
    assert sleeps == [1]  # 2**0 on the first (and only) retry


def test_fetch_card_gives_up_after_exhausting_429_retries(monkeypatch):
    monkeypatch.setattr(verify_card.time, "sleep", lambda s: None)
    error = urllib.error.HTTPError("url", 429, "Too Many Requests", {}, io.BytesIO(b""))
    monkeypatch.setattr(verify_card.urllib.request, "urlopen", raising(error))

    found, data = verify_card.fetch_card("Sol Ring")

    assert (found, data) == (False, {"details": "rate limited (HTTP 429)"})


def test_fetch_card_other_http_error(monkeypatch):
    error = urllib.error.HTTPError("url", 500, "Server Error", {}, io.BytesIO(b""))
    monkeypatch.setattr(verify_card.urllib.request, "urlopen", raising(error))

    found, data = verify_card.fetch_card("Sol Ring")

    assert (found, data) == (False, {"details": "HTTP 500"})


def test_fetch_card_network_error(monkeypatch):
    error = urllib.error.URLError("no route to host")
    monkeypatch.setattr(verify_card.urllib.request, "urlopen", raising(error))

    found, data = verify_card.fetch_card("Sol Ring")

    assert (found, data) == (False, {"details": "network error: no route to host"})

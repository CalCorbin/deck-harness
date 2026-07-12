"""Tests for verify_deck.py — parse, check, and report layers.

No real network calls: urllib.request.urlopen and time.sleep are patched via monkeypatch.
"""

import io
import json
import urllib.error

import pytest

import verify_deck


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
# parse_deck
# ---------------------------------------------------------------------------


def test_parse_deck_reads_count_and_name(tmp_path):
    deck = tmp_path / "deck.md"
    deck.write_text("1 Sol Ring\n5 Forest\n")

    assert verify_deck.parse_deck(deck) == [(1, "Sol Ring"), (5, "Forest")]


def test_parse_deck_accepts_x_suffix(tmp_path):
    deck = tmp_path / "deck.md"
    deck.write_text("10x Island\n")

    assert verify_deck.parse_deck(deck) == [(10, "Island")]


def test_parse_deck_skips_headers_and_blanks(tmp_path):
    deck = tmp_path / "deck.md"
    deck.write_text("# Deck Name\n\n1 Sol Ring\n")

    assert verify_deck.parse_deck(deck) == [(1, "Sol Ring")]


def test_parse_deck_returns_empty_list_for_no_matches(tmp_path):
    deck = tmp_path / "deck.md"
    deck.write_text("# Just a header\n")

    assert verify_deck.parse_deck(deck) == []


# ---------------------------------------------------------------------------
# check_card
# ---------------------------------------------------------------------------


def test_check_card_found(monkeypatch):
    def fake_urlopen(req, timeout):
        return FakeResponse({"name": "Sol Ring"})

    monkeypatch.setattr(verify_deck.urllib.request, "urlopen", fake_urlopen)

    found, detail = verify_deck.check_card("Sol Ring")

    assert (found, detail) == (True, "Sol Ring")


def test_check_card_not_found(monkeypatch):
    fp = io.BytesIO(json.dumps({"details": "no card found"}).encode())
    error = urllib.error.HTTPError("url", 404, "Not Found", {}, fp)
    monkeypatch.setattr(verify_deck.urllib.request, "urlopen", raising(error))

    found, detail = verify_deck.check_card("Not A Card")

    assert (found, detail) == (False, "no card found")


def test_check_card_not_found_with_unparsable_body(monkeypatch):
    fp = io.BytesIO(b"not json")
    error = urllib.error.HTTPError("url", 404, "Not Found", {}, fp)
    monkeypatch.setattr(verify_deck.urllib.request, "urlopen", raising(error))

    found, detail = verify_deck.check_card("Not A Card")

    assert (found, detail) == (False, "not found")


def test_check_card_retries_on_429_then_succeeds(monkeypatch):
    sleeps = []
    monkeypatch.setattr(verify_deck.time, "sleep", lambda s: sleeps.append(s))

    attempts = {"count": 0}

    def flaky(req, timeout):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise urllib.error.HTTPError("url", 429, "Too Many Requests", {}, io.BytesIO(b""))
        return FakeResponse({"name": "Sol Ring"})

    monkeypatch.setattr(verify_deck.urllib.request, "urlopen", flaky)

    found, detail = verify_deck.check_card("Sol Ring")

    assert (found, detail) == (True, "Sol Ring")
    assert sleeps == [1]  # 2**0 on the first (and only) retry


def test_check_card_gives_up_after_exhausting_429_retries(monkeypatch):
    monkeypatch.setattr(verify_deck.time, "sleep", lambda s: None)
    error = urllib.error.HTTPError("url", 429, "Too Many Requests", {}, io.BytesIO(b""))
    monkeypatch.setattr(verify_deck.urllib.request, "urlopen", raising(error))

    found, detail = verify_deck.check_card("Sol Ring")

    assert (found, detail) == (False, "rate limited (HTTP 429)")


def test_check_card_other_http_error(monkeypatch):
    error = urllib.error.HTTPError("url", 500, "Server Error", {}, io.BytesIO(b""))
    monkeypatch.setattr(verify_deck.urllib.request, "urlopen", raising(error))

    found, detail = verify_deck.check_card("Sol Ring")

    assert (found, detail) == (False, "HTTP 500")


def test_check_card_network_error(monkeypatch):
    error = urllib.error.URLError("no route to host")
    monkeypatch.setattr(verify_deck.urllib.request, "urlopen", raising(error))

    found, detail = verify_deck.check_card("Sol Ring")

    assert (found, detail) == (False, "network error: no route to host")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def no_real_delay(monkeypatch):
    """Every main() test drives check_card directly, so REQUEST_DELAY sleeps are dead weight."""
    monkeypatch.setattr(verify_deck.time, "sleep", lambda s: None)


def test_main_returns_0_when_all_cards_found(tmp_path, monkeypatch, capsys):
    deck = tmp_path / "deck.md"
    deck.write_text("1 Sol Ring\n")
    monkeypatch.setattr(verify_deck, "check_card", lambda name: (True, name))
    monkeypatch.setattr("sys.argv", ["verify_deck.py", str(deck)])

    exit_code = verify_deck.main()

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "OK    1 Sol Ring" in out
    assert "1/1 verified." in out


def test_main_returns_1_and_lists_missing_cards(tmp_path, monkeypatch, capsys):
    deck = tmp_path / "deck.md"
    deck.write_text("1 Not A Real Card\n")
    monkeypatch.setattr(verify_deck, "check_card", lambda name: (False, "not found"))
    monkeypatch.setattr("sys.argv", ["verify_deck.py", str(deck)])

    exit_code = verify_deck.main()

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "FAIL  1 Not A Real Card  -> not found" in out
    assert "1 not found:" in out
    assert "- Not A Real Card" in out


def test_main_returns_1_for_empty_deck(tmp_path, monkeypatch, capsys):
    deck = tmp_path / "deck.md"
    deck.write_text("# Just a header\n")
    monkeypatch.setattr("sys.argv", ["verify_deck.py", str(deck)])

    exit_code = verify_deck.main()

    err = capsys.readouterr().err
    assert exit_code == 1
    assert "No card lines found" in err

"""Tests for verify_card.py — fetch, render, and report layers.

No real network calls: urllib.request.urlopen and time.sleep are patched via monkeypatch.
"""

import io
import json
import os
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


# ---------------------------------------------------------------------------
# render_card_table
# ---------------------------------------------------------------------------


def test_render_card_table_single_faced_card():
    data = {
        "name": "Sol Ring",
        "mana_cost": "{1}",
        "type_line": "Artifact",
        "rarity": "uncommon",
        "set_name": "Commander",
        "set": "cmd",
        "oracle_text": "{T}: Add {C}{C}.",
        "prices": {"usd": "1.23"},
    }

    table = verify_card.render_card_table(data)

    assert "🃏" in table and "Sol Ring" in table
    assert "💠" in table and "{1}" in table
    assert "📜" in table and "Artifact" in table
    assert "⭐" in table and "uncommon" in table
    assert "📦" in table and "Commander (CMD)" in table
    assert "📝" in table and "{T}: Add {C}{C}." in table
    assert "💵" in table and "$1.23" in table


def test_render_card_table_borders_align_with_wide_emoji_labels():
    data = {
        "name": "Sol Ring",
        "mana_cost": "{1}",
        "type_line": "Artifact",
        "rarity": "uncommon",
        "set_name": "Commander",
        "set": "cmd",
        "oracle_text": "{T}: Add {C}{C}.",
        "prices": {"usd": "1.23"},
    }

    table = verify_card.render_card_table(data)
    widths = {verify_card.display_width(line) for line in table.splitlines()}

    assert len(widths) == 1


def test_render_card_table_double_faced_card_uses_face_fallback():
    data = {
        "name": "Delver of Secrets // Insectile Aberration",
        "type_line": "Creature // Creature",
        "rarity": "common",
        "set_name": "Innistrad",
        "set": "isd",
        "prices": {"usd": None},
        "card_faces": [
            {"mana_cost": "{U}", "oracle_text": "At the beginning of your upkeep..."},
            {"mana_cost": "", "oracle_text": "Flying"},
        ],
    }

    table = verify_card.render_card_table(data)

    assert "{U}" in table
    assert "At the beginning of your upkeep..." in table


def test_render_card_table_wraps_long_oracle_text(monkeypatch):
    monkeypatch.setattr(
        verify_card.shutil, "get_terminal_size", lambda fallback=None: os.terminal_size((80, 24))
    )
    data = {
        "name": "Test Card",
        "mana_cost": "{1}",
        "type_line": "Artifact",
        "rarity": "common",
        "set_name": "Test Set",
        "set": "tst",
        "oracle_text": "word " * 40,
        "prices": {"usd": None},
    }

    table = verify_card.render_card_table(data)
    lines = table.splitlines()
    text_row_index = next(i for i, line in enumerate(lines) if "📝" in line)

    assert "word" in lines[text_row_index + 1]


def test_render_card_table_shows_na_for_missing_price():
    data = {
        "name": "Test Card",
        "mana_cost": "{1}",
        "type_line": "Artifact",
        "rarity": "common",
        "set_name": "Test Set",
        "set": "tst",
        "oracle_text": "",
        "prices": {"usd": None},
    }

    table = verify_card.render_card_table(data)

    assert "n/a" in table


# ---------------------------------------------------------------------------
# render_not_found
# ---------------------------------------------------------------------------


def test_render_not_found_includes_name_and_detail():
    message = verify_card.render_not_found("Sol Rign", 'perhaps you meant "Sol Ring"?')

    assert "❌" in message
    assert "Sol Rign" in message
    assert 'perhaps you meant "Sol Ring"?' in message


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_prints_table_and_returns_0_when_found(monkeypatch, capsys):
    card = {"name": "Sol Ring", "prices": {}}
    monkeypatch.setattr(verify_card, "fetch_card", lambda name: (True, card))
    monkeypatch.setattr("sys.argv", ["verify_card.py", "Sol Ring"])

    exit_code = verify_card.main()

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "🃏" in out and "Sol Ring" in out


def test_main_prints_not_found_and_returns_1(monkeypatch, capsys):
    monkeypatch.setattr(
        verify_card, "fetch_card", lambda name: (False, {"details": "not found"})
    )
    monkeypatch.setattr("sys.argv", ["verify_card.py", "Not A Real Card"])

    exit_code = verify_card.main()

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "❌" in out
    assert "Not A Real Card" in out
    assert "not found" in out

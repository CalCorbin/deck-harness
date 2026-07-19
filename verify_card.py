#!/usr/bin/env python3
"""Look up a single Magic: The Gathering card on Scryfall by exact name.

Usage:
    python verify_card.py "Sol Ring"
"""

import argparse
import json
import shutil
import sys
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request

SCRYFALL_NAMED = "https://api.scryfall.com/cards/named"
USER_AGENT = "deck-harness-verifier/1.0"

TABLE_ROWS = [
    ("🃏", "Name", "name"),
    ("💠", "Mana Cost", "mana_cost"),
    ("📜", "Type", "type_line"),
    ("⭐", "Rarity", "rarity"),
    ("📦", "Set", "set_display"),
    ("📝", "Text", "oracle_text"),
    ("💵", "Price (USD)", "price_usd"),
]


def fetch_card(name):
    """Query Scryfall for an exact card name.

    Returns (found: bool, data: dict). data is the full card object when found,
    otherwise {"details": <error/suggestion message>}.
    """
    query = urllib.parse.urlencode({"exact": name})
    req = urllib.request.Request(
        f"{SCRYFALL_NAMED}?{query}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return True, json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                try:
                    detail = json.load(e).get("details", "not found")
                except ValueError:
                    detail = "not found"
                return False, {"details": detail}
            if e.code == 429:
                time.sleep(2**attempt)
                continue
            return False, {"details": f"HTTP {e.code}"}
        except urllib.error.URLError as e:
            return False, {"details": f"network error: {e.reason}"}
    return False, {"details": "rate limited (HTTP 429)"}


def _face_field(data, field):
    """Return data[field], falling back to the first card_face for double-faced cards."""
    value = data.get(field)
    if value:
        return value
    faces = data.get("card_faces") or [{}]
    return faces[0].get(field, "")


def _card_values(data):
    """Flatten a Scryfall card object into the display strings render_card_table needs."""
    usd = (data.get("prices") or {}).get("usd")
    set_code = data.get("set", "").upper()
    set_name = data.get("set_name", "")
    return {
        "name": data.get("name", ""),
        "mana_cost": _face_field(data, "mana_cost"),
        "type_line": data.get("type_line", ""),
        "rarity": data.get("rarity", ""),
        "set_display": f"{set_name} ({set_code})" if set_code else set_name,
        "oracle_text": _face_field(data, "oracle_text"),
        "price_usd": f"${usd}" if usd else "n/a",
    }


def render_card_table(data):
    """Render a bordered, emoji-labeled table of card details. Pure formatting, no I/O."""
    values = _card_values(data)
    label_col = max(len(f"{emoji} {label}") for emoji, label, _ in TABLE_ROWS)
    terminal_width = shutil.get_terminal_size(fallback=(100, 24)).columns
    value_col = max(min(terminal_width, 100) - label_col - 7, 20)

    def border(left, junction, right):
        return left + "─" * (label_col + 2) + junction + "─" * (value_col + 2) + right

    lines = [border("┌", "┬", "┐")]
    for emoji, label, key in TABLE_ROWS:
        label_text = f"{emoji} {label}".ljust(label_col)
        wrapped = textwrap.wrap(values[key], width=value_col) or [""]
        lines.append(f"│ {label_text} │ {wrapped[0].ljust(value_col)} │")
        for extra in wrapped[1:]:
            lines.append(f"│ {' ' * label_col} │ {extra.ljust(value_col)} │")
        lines.append(border("├", "┼", "┤"))
    lines[-1] = border("└", "┴", "┘")

    return "\n".join(lines)


def render_not_found(name, detail):
    """Render the not-found failure message. Pure formatting, no I/O."""
    return f'❌ "{name}" not found on Scryfall.\n   {detail}'


def main():
    ap = argparse.ArgumentParser(description="Verify a single MTG card against Scryfall.")
    ap.add_argument("name", help="Exact card name to look up")
    args = ap.parse_args()

    found, data = fetch_card(args.name)
    if found:
        print(render_card_table(data))
        return 0

    print(render_not_found(args.name, data.get("details", "not found")))
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

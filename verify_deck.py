#!/usr/bin/env python3
"""Verify every Magic: The Gathering card in a markdown deck file exists on Scryfall.

Deck line format (one card per line):

    <count> <card name>

Lines that don't start with a number (headers, blanks, comments) are skipped.

Usage:
    python verify_deck.py decks/morska.md
    python verify_deck.py decks/morska.md --json report.json
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SCRYFALL_NAMED = "https://api.scryfall.com/cards/named"
# Scryfall asks for 50-100ms between requests. Use 100ms to be polite.
REQUEST_DELAY = 0.1
USER_AGENT = "deck-harness-verifier/1.0"

# Matches "1 Sol Ring", "5 Forest", "10x Island" -> count, name
LINE_RE = re.compile(r"^\s*(\d+)\s*x?\s+(.+?)\s*$")


def parse_deck(path):
    """Return list of (count, name) tuples parsed from the deck file."""
    cards = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = LINE_RE.match(line)
            if m:
                cards.append((int(m.group(1)), m.group(2)))
    return cards


def check_card(name):
    """Query Scryfall for an exact card name.

    Returns (found: bool, detail: str). detail is the canonical name when found,
    otherwise the error/suggestion message.
    """
    query = urllib.parse.urlencode({"exact": name})
    req = urllib.request.Request(
        f"{SCRYFALL_NAMED}?{query}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.load(resp)
            return True, data.get("name", name)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                try:
                    body = json.load(e)
                    detail = body.get("details", "not found")
                except (ValueError, json.JSONDecodeError):
                    detail = "not found"
                return False, detail
            if e.code == 429:
                # Rate limited: back off and retry.
                time.sleep(2 ** attempt)
                continue
            return False, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            return False, f"network error: {e.reason}"
    return False, "rate limited (HTTP 429)"


def main():
    ap = argparse.ArgumentParser(description="Verify MTG deck cards against Scryfall.")
    ap.add_argument("deck", help="Path to the markdown deck file")
    ap.add_argument("--json", metavar="FILE", help="Write a JSON report to FILE")
    args = ap.parse_args()

    cards = parse_deck(args.deck)
    if not cards:
        print(f"No card lines found in {args.deck}", file=sys.stderr)
        return 1

    print(f"Checking {len(cards)} unique card lines against Scryfall...\n")

    results = []
    missing = []
    for count, name in cards:
        found, detail = check_card(name)
        results.append({"count": count, "name": name, "found": found, "detail": detail})
        if found:
            print(f"  OK   {count:>2} {name}")
        else:
            print(f"  FAIL {count:>2} {name}  -> {detail}")
            missing.append(name)
        time.sleep(REQUEST_DELAY)

    print(f"\n{len(cards) - len(missing)}/{len(cards)} verified.")
    if missing:
        print(f"{len(missing)} not found:")
        for name in missing:
            print(f"  - {name}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print(f"\nJSON report written to {args.json}")

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Look up a single Magic: The Gathering card on Scryfall by exact name.

Usage:
    python verify_card.py "Sol Ring"
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

SCRYFALL_NAMED = "https://api.scryfall.com/cards/named"
USER_AGENT = "deck-harness-verifier/1.0"


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

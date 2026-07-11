# deck-harness

Agentic harness for crafting and storing Magic: The Gathering decks. Decks live as markdown files; a verification script checks every card against the [Scryfall](https://scryfall.com) API.

## Table of Contents

- [Setup](#setup)
- [Codebase Map](#codebase-map)
- [Verifying a Deck](#verifying-a-deck)
- [Deck File Format](#deck-file-format)
- [Adding a New Deck](#adding-a-new-deck)

---

## Setup

Python 3.8+ required. No third-party dependencies — stdlib only.

```bash
git clone https://github.com/CalCorbin/deck-harness.git
cd deck-harness
```

---

## Codebase Map

```
deck-harness/
├── verify_deck.py      # Verification script (parse → check → report)
└── decks/
    └── morska.md       # Morska, the Unpredictable commander deck
```

Rate-limit handling: 100ms delay between every request; exponential backoff (up to 4 attempts) on HTTP 429.

---

## Verifying a Deck

```bash
# Print results to stdout
python verify_deck.py decks/morska.md
```

Sample output:

```
Checking 99 unique card lines against Scryfall...

  OK    1 Sol Ring
  OK    5 Forest
  FAIL  1 Typo Card Name  -> Card not found

98/99 verified.
1 not found:
  - Typo Card Name
```

Exit code is `0` when all cards verified, `1` if any failed.

---

## Deck File Format

Decks are markdown files in `decks/`. Lines matching `<count> [x] <card name>` are parsed; headers, blanks, and comments are ignored.

```markdown
# Morska, the Unpredictable

## Commanders
1 Morska, the Unpredictable

## Ramp
1 Sol Ring
1x Arcane Signet
5 Forest
```

---

## Adding a New Deck

1. Create `decks/<deck-name>.md` using the format above.
2. Run `python verify_deck.py decks/<deck-name>.md` to catch typos.
3. Commit the file.

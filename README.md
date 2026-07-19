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

Python 3.11+ required.

```bash
git clone https://github.com/CalCorbin/deck-harness.git
cd deck-harness
make be.setup            # creates .venv, installs dev dependencies, installs deck-harness in editable mode
source .venv/bin/activate  # puts verify-deck / verify-card on PATH
```

---

## Codebase Map

```
deck-harness/
├── src/deck_harness/
│   ├── verify_deck.py      # Verification script (parse → check → report)
│   └── verify_card.py      # Single-card lookup CLI (fetch → render → report)
├── pyproject.toml          # Package metadata, entry points, ruff/pytest/coverage config
├── requirements-dev.txt    # Dev dependencies (ruff, pytest, pytest-cov)
├── Makefile                # Top-level make entrypoint
├── .make/
│   ├── backend.mk          # be.setup, be.lint, be.test targets
│   ├── cards.mk            # card.verify target
│   └── base.mk              # help target
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       └── pull-request.yml  # CI: ruff lint + pytest on every PR
├── docs/
│   └── python-style.md     # Coding standards and lint instructions
├── tests/                  # pytest suite (100% coverage gate)
└── decks/
    └── morska.md           # Morska, the Unpredictable commander deck
```

Rate-limit handling: 100ms delay between every request; exponential backoff (up to 4 attempts) on HTTP 429.

---

## Verifying a Deck

```bash
# Print results to stdout
verify-deck decks/morska.md
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
2. Run `verify-deck decks/<deck-name>.md` to catch typos.
3. Commit the file.

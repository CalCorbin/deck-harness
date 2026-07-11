# How Python Is Written in This Repo

All Python in this repo — written by humans or agents — follows the Zen of Python. These aren't suggestions; they are the decision criteria when choices arise.

## The Zen of Python

```
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
```

(`import this` in any Python REPL to verify.)

## What This Means in Practice

**Explicit over implicit** — name things clearly. No mystery return values, no magic defaults that change behavior silently.

**Simple over complex** — if a function needs a comment explaining what it does, it is probably doing too much. Split it.

**Flat over nested** — prefer early returns and guard clauses over deeply indented condition trees.

**Errors never pass silently** — catch only what you intend to handle. Log or re-raise everything else. A bare `except: pass` is a bug.

**Refuse to guess** — when input is ambiguous, raise a clear error. Don't infer intent and proceed.

**One obvious way** — when adding a new capability, check if the existing code already has a pattern for it. Extend that pattern rather than introducing a second one.

**If it's hard to explain, it's a bad idea** — this applies to function signatures, data structures, and module organization equally.

## For Agents

When generating or modifying Python in this repo:

- Prefer stdlib over third-party libraries unless the gain is substantial.
- Do not introduce a helper function unless it reduces cognitive load for a reader — DRY alone is not justification.
- Match the style and structure of surrounding code before proposing a new pattern.
- If a new pattern is unavoidable, document the decision in `docs/` before the change lands.

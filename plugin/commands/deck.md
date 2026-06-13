---
description: List your Wait & Learn decks or switch the active language (Pro unlocks more).
argument-hint: [language or deck name]
---

Your decks (or the result of switching) is below. Show the user ONLY that output,
verbatim, with no commentary. If it says no decks found, suggest running
`/wait-and-learn:setup` first.

```!
bun "$HOME/.wait-and-learn/runtime/deck.mjs" "$ARGUMENTS" 2>/dev/null || node "$HOME/.wait-and-learn/runtime/deck.mjs" "$ARGUMENTS" 2>/dev/null
```

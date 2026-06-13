---
description: Install Agora flashcards into Claude Code. Default = status line (always visible, with grading). "/agora:setup spinner" = show the deck only in the thinking spinner instead.
argument-hint: "[spinner]"
---

Set up Agora's language flashcards for this user.

Mode: if the user passed `spinner` (i.e. `$ARGUMENTS` is `spinner`), install spinner
mode (the active deck shows only in Claude Code's thinking spinner; the status
line is left as Claude Code's default). Otherwise install the default status-line
mode (the flashcard runs in the status line, with the reveal rhythm and grading).

Run exactly this command and show the user its full output. Try bun first, fall
back to node, and pass the argument through:

```bash
bun "${CLAUDE_PLUGIN_ROOT}/setup.mjs" $ARGUMENTS 2>/dev/null || node "${CLAUDE_PLUGIN_ROOT}/setup.mjs" $ARGUMENTS
```

The script copies the runtime to `~/.agora/runtime/`, backs up the user's
`~/.claude/settings.json` before writing, and records the chosen mode. Do not
edit any files yourself; the script does everything.

After it runs, tell the user briefly: restart Claude Code to load it. In
status-line mode, grade the shown word with `/agora:wl got` / `/agora:wl missed`.
In spinner mode there is no grading (the spinner is passive); switch language with
`/agora:deck <language>`.

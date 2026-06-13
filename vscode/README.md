# Wait & Learn: Flashcards while Claude thinks

Turns Claude Code's "thinking" spinner into language practice. While Claude
generates a response, the spinner shows a flashcard from your deck
(`hola → hello`) instead of the stock `Discombobulating…` verbs. Free, no ads,
no account, nothing leaves your machine.

## How it works

Claude Code's VS Code panel keeps its thinking verbs hardcoded in its own
bundle, with no settings hook to change them. So this extension patches that
verb pool with your active deck's `front → back` pairs. The change is:

- **Reversible.** The original verbs are backed up before the first patch.
  "Wait & Learn: Disable" restores them byte-for-byte, and the extension also
  restores them when it shuts down, so an uninstall never leaves Claude Code
  modified.
- **Self-healing.** When Claude Code updates, its bundle is rewritten and the
  patch is re-applied on the next VS Code start.
- **Safe.** The patched bundle is still valid JavaScript; if the extension
  can't confidently locate the verb pool, it changes nothing.

## Commands

- **Wait & Learn: Switch Language** — pick Spanish, French, or German.
- **Wait & Learn: Disable** — restore Claude Code's own thinking verbs.
- **Wait & Learn: Enable** — re-apply the flashcards.

After enabling or switching, reload the window (or restart the Claude Code
panel) so it picks up the new verbs.

## Note

This extension modifies the installed Claude Code extension's files on disk.
That is the only way to reach the VS Code thinking spinner (unlike the terminal
CLI, which has a supported `spinnerVerbs` setting). It is reversible and
self-healing, but it depends on Claude Code's internal layout and may need an
update if that layout changes.

The richer flashcard experience (tap-to-reveal, spaced repetition, grading)
lives in the companion browser extension and Claude Code terminal status line.

MIT licensed. Not affiliated with Anthropic.

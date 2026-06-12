// Wait & Learn - Claude Code status line.
// Shows a rotating language flashcard from the SAME deck the browser extension
// uses, so the terminal's "thinking" time becomes passive vocab exposure.
// Configure it with a short refreshInterval so the word rotates during waits
// (see the "Terminal" section of the README). Run with bun.
//
// Fail-silent: on any error it prints nothing rather than break the status bar.
import fs from "fs";
import os from "os";
import path from "path";
import { createRequire } from "module";

try {
  const require = createRequire(import.meta.url);

  // Same deck file the extension bundles (module.exports = the deck object).
  const deckPath = path.join(import.meta.dir, "..", "decks", "spanish-starter.js");
  const deck = require(deckPath);
  const cards = deck && Array.isArray(deck.cards) ? deck.cards : [];
  if (!cards.length) process.exit(0);

  // Read session_id from the JSON Claude Code pipes on stdin, to key a
  // per-session rotation counter (concurrent sessions rotate independently).
  let sessionId = "default";
  try {
    const raw = fs.readFileSync(0, "utf8");
    if (raw) {
      const j = JSON.parse(raw);
      if (j && j.session_id) sessionId = String(j.session_id);
    }
  } catch (e) {}

  // Advance a persisted counter each run so the card rotates over time/turns.
  const counterFile = path.join(os.tmpdir(), `wl-statusline-${sessionId}.idx`);
  let n = 0;
  try { n = parseInt(fs.readFileSync(counterFile, "utf8"), 10) || 0; } catch (e) {}
  try { fs.writeFileSync(counterFile, String(n + 1)); } catch (e) {}

  const card = cards[n % cards.length];

  // ANSI: dim label + arrow, bold cyan target word.
  const dim = "\x1b[2m", bold = "\x1b[1m", cyan = "\x1b[36m", reset = "\x1b[0m";
  const lang = String(deck.lang || "").toUpperCase();
  process.stdout.write(
    `${dim}📘 ${lang}${reset} ${bold}${cyan}${card.front}${reset} ${dim}→ ${card.back}${reset}`
  );
} catch (e) {
  // fail silent: print nothing rather than break the status line
}

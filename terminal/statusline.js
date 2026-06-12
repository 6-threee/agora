// Wait & Learn - Claude Code status line.
// Shows a rotating language flashcard from the SAME deck the browser extension
// uses, with real spaced repetition (shared scheduler) and a passive recall
// rhythm: it shows the word alone first ("el perro · ?"), then reveals the
// translation on the next refresh ("el perro -> the dog"), then moves on.
// Grade the shown word with the `wl` command (see grade.js) to feed real SRS.
//
// The persisted rhythm always reflects the card CURRENTLY on screen, so `wl got`
// / `wl missed` grade exactly what you see.
//
// Configure with a short refreshInterval so it rotates during waits (README).
// Fail-silent: prints nothing on error rather than break the status bar.
import fs from "fs";
import { deck, Scheduler, loadSrs, saveSrs, loadRhythm, saveRhythm, entries } from "./store.js";

// How many refreshes the revealed answer lingers before auto-advancing if you
// do not grade it. With refreshInterval 3, 2 = the answer shows for ~6s.
const REVEAL_TICKS = 2;

try {
  // Drain stdin (Claude Code pipes session JSON); we do not need it here.
  try { fs.readFileSync(0, "utf8"); } catch (e) {}

  if (!deck || !Scheduler || !Array.isArray(deck.cards) || !deck.cards.length) process.exit(0);

  const byId = {};
  deck.cards.forEach(function (c) { byId[c.id] = c; });
  const deckId = deck.id || "deck";
  const now = Date.now();

  const srs = loadSrs(deckId);
  function pickId() { return Scheduler.pickNext(entries(srs), now); }

  // Advance from the previous (displayed) state to the state to show THIS run.
  const prev = loadRhythm();
  let cur;
  if (prev.deckId !== deckId || !prev.cardId || !byId[prev.cardId]) {
    cur = { deckId: deckId, cardId: pickId(), phase: "front", revealCount: 0 };
  } else if (prev.phase === "front") {
    cur = { deckId: deckId, cardId: prev.cardId, phase: "reveal", revealCount: 0 };
  } else {
    const rc = (prev.revealCount || 0) + 1;
    if (rc >= REVEAL_TICKS) {
      // Exposure memory: mark the finished card seen (updates lastSeen only, no
      // box change). pickNext's lastSeen tiebreak then surfaces a different,
      // less-recently-seen card next, so the deck rotates rather than repeating.
      srs[prev.cardId] = Scheduler.markSeen(srs[prev.cardId], now);
      saveSrs(deckId, srs);
      cur = { deckId: deckId, cardId: pickId() || prev.cardId, phase: "front", revealCount: 0 };
    } else {
      cur = { deckId: deckId, cardId: prev.cardId, phase: "reveal", revealCount: rc };
    }
  }
  if (!cur.cardId || !byId[cur.cardId]) process.exit(0); // empty deck guard

  const card = byId[cur.cardId];

  // Render the current phase.
  const dim = "\x1b[2m", bold = "\x1b[1m", cyan = "\x1b[36m", reset = "\x1b[0m";
  const lang = String(deck.lang || "").toUpperCase();
  let out;
  if (cur.phase === "front") {
    out = `${dim}📘 ${lang}${reset} ${bold}${cyan}${card.front}${reset} ${dim}· ?${reset}`;
  } else {
    out = `${dim}📘 ${lang}${reset} ${bold}${cyan}${card.front}${reset} ${dim}→${reset} ${card.back}`;
  }
  process.stdout.write(out);

  // Persist the state that is now on screen (so grading targets this card).
  saveRhythm(cur);
} catch (e) {
  // fail silent: print nothing rather than break the status line
}

// Agora - write the deck into Claude Code's thinking spinner (the supported
// `spinnerVerbs` setting, CC 2.1.143+) for "spinner mode". Used by the deck
// switcher; the installer does its own settings.json handling (it also manages
// the status line, with backup + ours-detection). Node + bun.
// Fail-soft: returns false (never throws) when settings.json is missing,
// unparseable, or unwritable, so it can never break a caller.
import fs from "fs";
import os from "os";
import path from "path";

const SETTINGS = path.join(os.homedir(), ".claude", "settings.json");

function read() {
  try { return JSON.parse(fs.readFileSync(SETTINGS, "utf8")); } catch (e) { return null; }
}

function writeAtomic(obj) {
  const tmp = SETTINGS + ".agora-tmp." + process.pid;
  try {
    fs.writeFileSync(tmp, JSON.stringify(obj, null, 2) + "\n");
    fs.renameSync(tmp, SETTINGS);
    return true;
  } catch (e) {
    try { fs.unlinkSync(tmp); } catch (e2) {}
    return false;
  }
}

// One "front → back" string per card - the words shown in the thinking spinner.
export function verbsForDeck(deck) {
  if (!deck || !Array.isArray(deck.cards)) return [];
  return deck.cards
    .filter(function (c) { return c && c.front && c.back; })
    .map(function (c) { return c.front + " → " + c.back; });
}

// Set spinnerVerbs (replace mode) from `verbs`. Touches ONLY spinnerVerbs; never
// the status line (the installer owns that, with backup + ours-detection).
// Returns true on success.
export function applySpinner(verbs) {
  const s = read();
  if (!s) return false;
  s.spinnerVerbs = { mode: "replace", verbs: Array.isArray(verbs) ? verbs : [] };
  return writeAtomic(s);
}

// Remove our spinnerVerbs (used when switching back to status-line mode).
export function clearSpinner() {
  const s = read();
  if (!s) return false;
  if (!s.spinnerVerbs) return true;
  delete s.spinnerVerbs;
  return writeAtomic(s);
}

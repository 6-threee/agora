// Wait & Learn - list your decks or switch the active one.
//   deck            list available decks (→ marks the active one)
//   deck <word>     switch active deck, matched by language code, id, or name
// Pro decks appear here once their files are in ~/.wait-and-learn/decks/.
import fs from "fs";
import os from "os";
import path from "path";
import { decks, deck as activeDeck, saveRhythm } from "./store.mjs";

const arg = String(process.argv.slice(2).join(" ") || "").trim().toLowerCase();
const cfgPath = path.join(os.homedir(), ".wait-and-learn", "config.json");

function readCfg() { try { return JSON.parse(fs.readFileSync(cfgPath, "utf8")) || {}; } catch (e) { return {}; } }
function writeCfg(o) {
  try {
    fs.mkdirSync(path.dirname(cfgPath), { recursive: true });
    const tmp = cfgPath + ".tmp." + process.pid;
    fs.writeFileSync(tmp, JSON.stringify(o));
    fs.renameSync(tmp, cfgPath);
    return true;
  } catch (e) { try { fs.unlinkSync(cfgPath + ".tmp." + process.pid); } catch (e2) {} return false; }
}

try {
  if (!decks || !decks.length) {
    console.log("Wait & Learn: no decks found. Run /wait-and-learn:setup first.");
    process.exit(0);
  }

  if (!arg) {
    const lines = decks.map(function (d) {
      const mark = (activeDeck && d.id === activeDeck.id) ? "→" : " ";
      return ` ${mark} ${d.name}  (${d.lang}, ${d.cards.length} cards)`;
    });
    const pro = decks.length > 1 ? "" : "\nUnlock more languages with Wait & Learn Pro.";
    console.log("Your decks:\n" + lines.join("\n") + "\n\nSwitch with: /wait-and-learn:deck <language>" + pro);
    process.exit(0);
  }

  // Match by language code, exact id, then name/id substring.
  const match = decks.find(function (d) { return (d.lang || "").toLowerCase() === arg; })
    || decks.find(function (d) { return d.id.toLowerCase() === arg; })
    || decks.find(function (d) { return (d.name || "").toLowerCase().indexOf(arg) !== -1; })
    || decks.find(function (d) { return d.id.toLowerCase().indexOf(arg) !== -1; });

  if (!match) {
    console.log(`No deck matches "${arg}". Run /wait-and-learn:deck to list them.`);
    process.exit(0);
  }

  const cfg = readCfg();
  cfg.activeDeck = match.id;
  if (!writeCfg(cfg)) {
    console.log("Wait & Learn: couldn't save your deck choice (disk write failed).");
    process.exit(0);
  }
  saveRhythm({}); // start the next refresh fresh on the new deck
  console.log(`\x1b[32m✓\x1b[0m active deck: ${match.name} (${match.lang}, ${match.cards.length} cards)`);
} catch (e) {
  console.log("Wait & Learn: deck switch failed.");
}

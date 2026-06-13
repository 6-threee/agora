// Deck loading for the VS Code extension. Reuses the same deck JSON the browser
// extension and CLI plugin ship, bundled flat into decks/. Each deck module
// exports { id, name, lang, cards: [{ front, back, example }] }.

const DECKS = {
  spanish: require("../decks/spanish-starter.js"),
  french: require("../decks/french-starter.js"),
  german: require("../decks/german-starter.js")
};

function getDeck(key) {
  return DECKS[key] || DECKS.spanish;
}

// Build the Claude Code "thinking verb" strings from a deck: one "front -> back"
// pair per card. The spinner picks one at random each thinking cycle, so the
// learner sees rotating vocabulary while Claude generates. Capped so the
// injected array stays a sane size.
function verbsFromDeck(deck, max) {
  const cards = deck && Array.isArray(deck.cards) ? deck.cards : [];
  const limit = typeof max === "number" ? max : 60;
  const verbs = [];
  for (const c of cards) {
    if (!c || !c.front || !c.back) continue;
    verbs.push(String(c.front) + " → " + String(c.back));
    if (verbs.length >= limit) break;
  }
  return verbs;
}

module.exports = { DECKS, getDeck, verbsFromDeck };

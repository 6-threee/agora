"""Convert the free bundled Portuguese deck (decks/pt.js) from Brazilian to
European Portuguese in place, preserving the curated 500-word progression and
card ids. Only Brazilian-specific vocab/examples change; pan-Portuguese cards
keep their front. Writes decks/pt.js (a .brazilian-bak was made first)."""
import json, os, subprocess, sys
from lib.llm import ask, chunks
from lib.vocab import parse_vocab_json

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DECK = os.path.join(REPO, "decks", "pt.js")

# Pull the existing cards out of the JS module via node.
cards_json = subprocess.check_output(
    ["node", "-e", f'console.log(JSON.stringify(require({DECK!r}).cards))'],
    text=True)
src = json.loads(cards_json)
print(f"loaded {len(src)} cards from free deck", flush=True)

CONVERT_PROMPT = """You are converting Brazilian Portuguese flashcards to EUROPEAN
PORTUGUESE (Portugal). For EACH input card, output one JSON object with the SAME
"id" and these fields:
- "id": copy the input id EXACTLY
- "front": if the word/phrase is the same in Portugal, keep it. If Portugal uses a
  different everyday word, replace it with the Portugal one (examples:
  onibus->autocarro, trem->comboio, celular->telemovel, banheiro->casa de banho,
  cafe da manha->pequeno-almoco, geladeira->frigorifico, xicara->chavena,
  suco->sumo, tchau->adeus/chau, terno->fato, meias->peugas where natural).
- "back": the English meaning (keep it; adjust only if the front changed).
- "example": rewrite as a natural EUROPEAN PORTUGUESE sentence. Use informal "tu"
  for singular you (NOT Brazilian "voce" as default), Portugal vocabulary and
  phrasing, and European spelling. Never mention Brazil; if the source says
  "Brasil" use "Portugal".
- "exampleEn": the English translation of your new example.

Output a JSON array of these objects and NOTHING else: no markdown, no code
fences, no commentary. Same number of cards as the input, ids preserved.

Cards (JSON):
{cards}
"""

def convert_batch(batch):
    payload = json.dumps(batch, ensure_ascii=False)
    text = ask(CONVERT_PROMPT.format(cards=payload))
    # reuse the tolerant JSON extractor, then map back to dicts with ids
    text = text.strip()
    a, b = text.find("["), text.rfind("]")
    if a != -1 and b > a:
        text = text[a:b + 1]
    import re
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return []

out, by_id = [], {}
batches = list(chunks(src, 100))
for i, group in enumerate(batches, 1):
    got = convert_batch(group)
    for o in got:
        if o.get("id") and o.get("front") and o.get("back"):
            by_id[o["id"]] = o
    print(f"batch {i}/{len(batches)}: have {len(by_id)}/{len(src)}", flush=True)

# Rebuild in original order/ids; fall back to source card if a card failed to convert.
converted, missing = [], 0
for c in src:
    o = by_id.get(c["id"])
    if o:
        converted.append({"id": c["id"], "front": o["front"], "back": o["back"],
                          "example": o.get("example", ""), "exampleEn": o.get("exampleEn", "")})
    else:
        converted.append(c); missing += 1
print(f"converted {len(converted)-missing}, kept-original {missing}", flush=True)

deck = {"id": "bundled:portuguese", "name": "Portuguese 500", "lang": "pt", "cards": converted}
body = "// Agora deck. Free.\nvar deck = " + json.dumps(deck, ensure_ascii=False, indent=2) + ";\n"
footer = (
    'if (typeof module !== "undefined" && module.exports) module.exports = deck;\n'
    'if (typeof window !== "undefined") { var WL = (window.WL = window.WL || {}); '
    '(WL.__decks = WL.__decks || []).push(deck); }\n'
)
# match the existing free-deck footer if present; otherwise the above is compatible
with open(DECK, "w", encoding="utf-8") as f:
    f.write(body + footer)
print(f"WROTE {DECK}", flush=True)

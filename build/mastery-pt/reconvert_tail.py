"""Re-convert the free-deck cards that failed in the last batch of convert_free_deck.py
(ids pt-0401..pt-0500 kept their Brazilian text). Small batches for reliability;
merge back into decks/pt.js by id."""
import json, os, subprocess, glob, re
from lib.llm import ask, chunks

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DECK = os.path.join(REPO, "decks", "pt.js")
BAK = sorted(glob.glob(DECK + ".brazilian-bak-*"))[-1]

cur = json.loads(subprocess.check_output(["node","-e",f'console.log(JSON.stringify(require({DECK!r}).cards))'],text=True))
src = json.loads(subprocess.check_output(["node","-e",f'console.log(JSON.stringify(require({BAK!r}).cards))'],text=True))
by_id = {c["id"]: c for c in cur}

# Target = cards still identical to the Brazilian original (never converted).
src_by_id = {c["id"]: c for c in src}
targets = [c for c in src if by_id.get(c["id"], {}).get("example") == c.get("example")]
print(f"{len(targets)} cards still un-converted -> re-converting in small batches", flush=True)

PROMPT = """Convert these Brazilian Portuguese flashcards to EUROPEAN PORTUGUESE (Portugal).
For EACH input card output one JSON object with the SAME "id":
- "id": copy exactly
- "front": keep if pan-Portuguese; else the Portugal word (onibus->autocarro, trem->comboio,
  celular->telemovel, banheiro->casa de banho, aplicativo->aplicacao, tela->ecra, etc.)
- "back": English meaning (adjust only if front changed)
- "example": rewrite as natural EUROPEAN PORTUGUESE using informal "tu" (never Brazilian "voce"
  as default), Portugal vocabulary/phrasing/spelling; never mention Brazil.
- "exampleEn": English translation of the new example.
JSON array only, no markdown, no commentary, ids preserved.

Cards (JSON):
{cards}
"""

def convert(batch):
    t = ask(PROMPT.format(cards=json.dumps(batch, ensure_ascii=False))).strip()
    a,b = t.find("["), t.rfind("]")
    if a!=-1 and b>a: t=t[a:b+1]
    t = re.sub(r",(\s*[}\]])", r"\1", t)
    try: return json.loads(t)
    except json.JSONDecodeError: return []

fixed = 0
for group in chunks(targets, 20):
    for o in convert(group):
        if o.get("id") and o.get("front") and o.get("back") and o.get("example"):
            by_id[o["id"]] = {"id":o["id"],"front":o["front"],"back":o["back"],
                              "example":o["example"],"exampleEn":o.get("exampleEn","")}
            fixed += 1
    print(f"  fixed so far: {fixed}", flush=True)

# rebuild in original order
cards = [by_id[c["id"]] for c in src]
deck = {"id":"bundled:portuguese","name":"Portuguese 500","lang":"pt","cards":cards}
body = "// Agora deck. Free.\nvar deck = " + json.dumps(deck, ensure_ascii=False, indent=2) + ";\n"
footer = ('if (typeof module !== "undefined" && module.exports) module.exports = deck;\n'
          'if (typeof window !== "undefined") { var WL = (window.WL = window.WL || {}); '
          '(WL.__decks = WL.__decks || []).push(deck); }\n')
open(DECK,"w",encoding="utf-8").write(body+footer)
print(f"re-converted {fixed}; WROTE {DECK}", flush=True)

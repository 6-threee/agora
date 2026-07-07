"""Expand the Mexican slang set with more words AND multi-word slang phrases,
merge into dist/slang.json, then reassemble the slang product and Mastery
(both use slang.json)."""
import json, subprocess, sys
from lib.llm import ask
from lib.vocab import parse_vocab_json

cards = json.load(open("dist/slang.json", encoding="utf-8"))
have = {c["front"] for c in cards}

EXPAND_PROMPT = """You are expanding the slang section of a EUROPEAN PORTUGUESE
(Portugal) deck for adult learners. Authentic calao and giria actually used IN
PORTUGAL, never Brazilian slang.

Output {n} European Portuguese {desc}. For EACH, output one JSON object:
- "front": the Portugal slang word or expression
- "back": English meaning (short; add "(vulgar)" or "(very informal)" when useful)
- "example": a natural European Portuguese sentence using it
- "exampleEn": the English translation

JSON array only, no markdown, no commentary, no duplicates. Do NOT repeat any of
these already-included terms: {avoid}
Variation tag (ignore in output): {tag}
"""

ANGLES = [
    ("slang EXPRESSIONS and multi-word phrases as said in Portugal (que se foda, "
     "nao faz mal, esta-se bem, bue da fixe, a bater a bota, nem penses, deixa "
     "andar, ta-se, qual e a cena, bora la, foda-se pa)", "phrases-1"),
    ("more Portugal slang expressions, comebacks, and reactions people say out loud", "phrases-2"),
    ("everyday Portugal slang words for people, money, work, and partying (gajo, "
     "gaja, malta, pa, chavalo, guito, massa, cunha, curro, bebedeira, copos, "
     "borga, farra, cota for parents, pinga)", "words-life"),
    ("younger / internet Portuguese (Portugal) slang and playful insults", "words-youth"),
]

for desc, tag in ANGLES:
    avoid = ", ".join(sorted(have))
    got = parse_vocab_json(ask(EXPAND_PROMPT.format(n=50, desc=desc, avoid=avoid, tag=tag)))
    added = 0
    for c in got:
        if c.front not in have:
            have.add(c.front); cards.append(c.__dict__); added += 1
    print(f"{tag}: +{added} (total {len(cards)})", flush=True)
    json.dump(cards, open("dist/slang.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"DONE slang: {len(cards)} cards", flush=True)

print("\n===== reassemble slang + mastery =====", flush=True)
subprocess.run([sys.executable, "build.py", "slang"])
subprocess.run([sys.executable, "build.py", "mastery"])

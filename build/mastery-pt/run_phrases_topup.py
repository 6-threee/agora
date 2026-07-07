"""Top up the European Portuguese phrases deck to match the Spanish target (>=305,
Spanish ships 299). Fresh Portugal angles, dedup against existing, then reassemble
the Phrases product."""
import json, subprocess, sys
from lib.llm import ask
from lib.vocab import parse_vocab_json

TARGET = 305
cards = json.load(open("dist/phrases.json", encoding="utf-8"))
have = {c["front"] for c in cards}
print(f"start: {len(cards)} phrases", flush=True)

TOPUP_PROMPT = """You are adding to a EUROPEAN PORTUGUESE (Portugal) phrases deck.
Everything must be how people actually talk in PORTUGAL: informal "tu" (not
Brazilian "voce"), Portugal wording and courtesy forms. Do NOT use Brazilian phrasing.

Output {n} useful European Portuguese {desc}. For EACH, output one JSON object:
- "front": the European Portuguese phrase
- "back": its English meaning
- "example": a natural European Portuguese sentence or short exchange using it
- "exampleEn": the English translation

JSON array only, no markdown, no commentary, no duplicates. Do NOT repeat any of
these already-included phrases: {avoid}
Variation tag (ignore in output): {tag}
"""

ANGLES = [
    ("phrases for work, school, and daily errands in Portugal (pharmacy, post office, "
     "bank, doctor, phone/internet, appointments)", "daily-errands"),
    ("phrases for making plans, invitations, and socialising in Portugal (cafe, bar, "
     "football, beach, dinner, meeting friends)", "social-plans"),
    ("polite requests, apologies, and phone/service phrases as said in Portugal", "polite-service"),
    ("feelings, opinions, agreeing and disagreeing, and everyday reactions in Portugal", "opinions-reactions"),
]

for desc, tag in ANGLES:
    if len(cards) >= TARGET:
        break
    avoid = ", ".join(sorted(have))
    got = parse_vocab_json(ask(TOPUP_PROMPT.format(n=40, desc=desc, avoid=avoid, tag=tag)))
    added = 0
    for c in got:
        if c.front not in have:
            have.add(c.front); cards.append(c.__dict__); added += 1
    print(f"{tag}: +{added} (total {len(cards)})", flush=True)
    json.dump(cards, open("dist/phrases.json", "w", encoding="utf-8"), ensure_ascii=False)

print(f"DONE phrases: {len(cards)} cards", flush=True)
print("\n===== reassemble phrases =====", flush=True)
subprocess.run([sys.executable, "build.py", "phrases"])

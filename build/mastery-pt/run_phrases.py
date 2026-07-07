"""Spanish Phrases add-on (separate $19 product). Blends conversational, travel,
and idiom phrases as rich cards. Saves to dist/phrases.json."""
import json, os
from lib.llm import ask
from lib.vocab import parse_vocab_json

os.makedirs("dist", exist_ok=True)

PHRASE_PROMPT = """You are building a EUROPEAN PORTUGUESE (Portugal) phrases
flashcard deck for learners. Everything must be how people actually talk in
PORTUGAL: Portugal wording, informal "tu" (not Brazilian "voce" as default),
Portugal expressions and courtesy forms (se faz favor, faca favor, com licenca,
bom proveito, de nada, esta bem, pois). Do not use Brazilian phrasing.

Output {n} useful European Portuguese {desc}. For EACH, output one JSON object:
- "front": the European Portuguese phrase
- "back": its English meaning
- "example": a natural European Portuguese sentence or short exchange using the phrase
- "exampleEn": the English translation of that example

Output a JSON array and NOTHING else: no markdown, no code fences, no
commentary. No duplicates. Variation tag (ignore in output): {tag}
"""

CATEGORIES = [
    ("everyday conversational phrases as spoken in Portugal: greetings, small talk, "
     "ordering a bica/coffee and food, asking directions, reactions, and Portugal "
     "filler chunks like 'pronto', 'pois', 'entao', 'a serio', 'epa', 'tipo', 'ora bem'",
     ["greetings-smalltalk", "reactions", "connectors"]),
    ("travel and survival phrases for a trip to Portugal: airport, hotel, cafes and "
     "pastelarias and restaurants, apanhar o comboio/autocarro/eletrico, taxi, "
     "markets and shopping, and emergencies",
     ["airport-hotel", "food-shopping-emergency"]),
    ("common PORTUGAL idioms and colorful expressions (ficar em aguas de bacalhau, "
     "pao pao queijo queijo, muitos anos a virar frangos, ir com os porcos, ora "
     "bolas), with the figurative meaning in the back field",
     ["idioms-a", "idioms-b"]),
]

cards, seen = [], set()
for desc, tags in CATEGORIES:
    for tag in tags:
        text = ask(PHRASE_PROMPT.format(n=50, desc=desc, tag=tag))
        for c in parse_vocab_json(text):
            if c.front not in seen:
                seen.add(c.front); cards.append(c)
        print(f"{tag}: total {len(cards)}", flush=True)
        json.dump([c.__dict__ for c in cards],
                  open("dist/phrases.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"DONE phrases: {len(cards)} cards -> dist/phrases.json")

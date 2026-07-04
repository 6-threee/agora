"""Spanish Phrases add-on (separate $19 product). Blends conversational, travel,
and idiom phrases as rich cards. Saves to dist/phrases.json."""
import json, os
from lib.llm import ask
from lib.vocab import parse_vocab_json

os.makedirs("dist", exist_ok=True)

PHRASE_PROMPT = """You are building a MEXICAN SPANISH phrases flashcard deck for
learners. Everything must be how people actually talk in MEXICO: Mexican wording,
"ustedes" never "vosotros", Mexican expressions and courtesy forms (mande, ahorita,
que tenga bonito dia). Do not use Spain phrasing.

Output {n} useful Mexican Spanish {desc}. For EACH, output one JSON object:
- "front": the Mexican Spanish phrase
- "back": its English meaning
- "example": a natural Mexican Spanish sentence or short exchange using the phrase
- "exampleEn": the English translation of that example

Output a JSON array and NOTHING else: no markdown, no code fences, no
commentary. No duplicates. Variation tag (ignore in output): {tag}
"""

CATEGORIES = [
    ("everyday conversational phrases as spoken in Mexico: greetings, small talk, "
     "ordering food/drinks, asking directions, reactions, and Mexican filler "
     "chunks like 'o sea', 'la neta', 'ni modo', 'ahorita', 'que onda'",
     ["greetings-smalltalk", "reactions", "connectors"]),
    ("travel and survival phrases for a trip to Mexico: airport, hotel, taquerias "
     "and restaurants, taxi/Uber, markets and shopping, and emergencies",
     ["airport-hotel", "food-shopping-emergency"]),
    ("common MEXICAN idioms, dichos, and colorful expressions (no manches, me vale, "
     "aguas, echar la mano), with the figurative meaning in the back field",
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

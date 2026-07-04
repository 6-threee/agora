"""Spanish Phrases add-on (separate $19 product). Blends conversational, travel,
and idiom phrases as rich cards. Saves to dist/phrases.json."""
import json, os
from lib.llm import ask
from lib.vocab import parse_vocab_json

os.makedirs("dist", exist_ok=True)

PHRASE_PROMPT = """You are building a Spanish phrases flashcard deck for learners.

Output {n} useful Spanish {desc}. For EACH, output one JSON object:
- "front": the Spanish phrase
- "back": its English meaning
- "example": a natural Spanish sentence or short exchange using the phrase
- "exampleEn": the English translation of that example

Output a JSON array and NOTHING else: no markdown, no code fences, no
commentary. No duplicates. Variation tag (ignore in output): {tag}
"""

CATEGORIES = [
    ("everyday conversational phrases: greetings, small talk, ordering, asking "
     "directions, reactions, and connective filler chunks like 'o sea', "
     "'de hecho', 'la verdad es que'", ["greetings-smalltalk", "reactions", "connectors"]),
    ("travel and survival phrases: airport, hotel, restaurant, taxi, shopping, "
     "and emergencies", ["airport-hotel", "food-shopping-emergency"]),
    ("common idioms and colorful expressions (modismos), with the figurative "
     "meaning in the back field", ["idioms-a", "idioms-b"]),
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

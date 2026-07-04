"""Generate a Spanish slang + profanity set as rich cards (for adult learners),
folded into the Mastery deck at assembly. Saves to dist/slang.json."""
import json, os
from lib.llm import ask, chunks
from lib.vocab import parse_vocab_json

os.makedirs("dist", exist_ok=True)

SLANG_PROMPT = """You are building the slang and profanity section of a Spanish
vocabulary deck for adult learners. These are words people actually hear.

Output {n} common Spanish slang terms, curse words, insults, and vulgar
expressions (mix mild to strong; include some regional ones). For EACH, output
one JSON object:
- "front": the Spanish term or expression
- "back": its English meaning (short; add a brief note in parentheses when
  useful, e.g. "(vulgar)", "(Spain)", "(Mexico)")
- "example": one natural Spanish sentence using it
- "exampleEn": the English translation of that sentence

Output a JSON array and NOTHING else: no markdown, no code fences, no
commentary. No duplicates. Batch tag (ignore in output): {tag}
"""

cards, seen = [], set()
# two batches with distinct tags to reduce overlap between calls
for tag in ("everyday-slang-and-mild", "stronger-and-regional"):
    text = ask(SLANG_PROMPT.format(n=70, tag=tag))
    for c in parse_vocab_json(text):
        if c.front not in seen:
            seen.add(c.front); cards.append(c)
    print(f"{tag}: total {len(cards)}", flush=True)
    json.dump([c.__dict__ for c in cards],
              open("dist/slang.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"DONE slang: {len(cards)} cards -> dist/slang.json")

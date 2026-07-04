import json, re
from lib.schema import Card
from lib.llm import ask, chunks

PROMPT = """You are building a MEXICAN SPANISH vocabulary flashcard deck.

For EACH Spanish word form below, output one JSON object with:
- "front": the exact Spanish word form as given
- "back": its most common English translation as used in Mexico (short; if Mexico
  prefers a different everyday word, note it briefly, e.g. "car (Mex: carro)")
- "example": one natural sentence in MEXICAN Spanish (Mexican vocabulary and
  phrasing; use "ustedes", never "vosotros")
- "exampleEn": the English translation of that sentence

Output a JSON array of these objects and NOTHING else: no markdown, no code
fences, no commentary. Keep "front" identical to the input form.

Word forms:
{words}
"""

def parse_vocab_json(text):
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text).strip()
    # extract the JSON array even if the model wrapped it in prose
    a, b = text.find("["), text.rfind("]")
    if a != -1 and b > a:
        text = text[a:b + 1]
    # tolerate trailing commas before } or ]
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    cards = []
    for o in data:
        if all(k in o and str(o[k]).strip() for k in ("front", "back")):
            cards.append(Card(o["front"], o["back"],
                              o.get("example", ""), o.get("exampleEn", "")))
    return cards

def generate_vocab(forms, batch=100):
    cards = []
    for group in chunks(forms, batch):
        text = ask(PROMPT.format(words="\n".join(group)))
        cards += parse_vocab_json(text)
    return cards

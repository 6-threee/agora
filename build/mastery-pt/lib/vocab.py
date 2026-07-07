import json, re
from lib.schema import Card
from lib.llm import ask, chunks

PROMPT = """You are building a EUROPEAN PORTUGUESE (Portugal) vocabulary flashcard deck.

For EACH Portuguese word form below, output one JSON object with:
- "front": the exact Portuguese word form as given
- "back": its most common English translation as used in PORTUGAL (short; if
  Portugal prefers a different everyday word than Brazil, use the Portugal one,
  e.g. "bus (autocarro)", "phone (telemóvel)", "train (comboio)")
- "example": one natural sentence in EUROPEAN PORTUGUESE (Portugal vocabulary and
  phrasing; informal "tu" for singular you, never Brazilian "você" as default;
  use Portugal words: autocarro, comboio, telemóvel, casa de banho, pequeno-almoço,
  fixe, giro, rapaz/rapariga; European spelling and phrasing)
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

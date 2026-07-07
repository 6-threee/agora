"""Full vocab stage: generate rich cards for the top 2000 forms, batch 100,
saving incrementally to dist/vocab.json so a mid-run failure keeps progress."""
import json, os
from lib.frequency import top_forms
from lib.vocab import PROMPT, parse_vocab_json
from lib.llm import ask, chunks

DATA = "data/pt_top_words.csv"
os.makedirs("dist", exist_ok=True)

forms = top_forms(2000, DATA)
batches = list(chunks(forms, 100))
cards = []
for i, group in enumerate(batches, 1):
    text = ask(PROMPT.format(words="\n".join(group)))
    got = parse_vocab_json(text)
    cards += got
    print(f"batch {i}/{len(batches)}: +{len(got)} parsed (total {len(cards)})", flush=True)
    json.dump([c.__dict__ for c in cards],
              open("dist/vocab.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"DONE vocab: {len(cards)} cards -> dist/vocab.json")

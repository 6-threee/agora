"""Verb stage: lemmatize the top 2000 forms to infinitives, then conjugate
(present + preterite), saving incrementally to dist/verbs.json and dist/conj.json.
Run after run_vocab.py finishes (avoid two concurrent claude -p storms)."""
import json, os
from lib.frequency import top_forms
from lib.verbs import LEMMA_PROMPT, CONJ_PROMPT, TENSE_LINES, lines_to_cards
from lib.llm import ask, chunks, parse_arrow_lines

DATA = "data/es_top_words.csv"
os.makedirs("dist", exist_ok=True)
forms = top_forms(2000, DATA)

# Stage A: lemmatize forms to unique infinitives
infs, seen = [], set()
lemma_batches = list(chunks(forms, 100))
for i, group in enumerate(lemma_batches, 1):
    text = ask(LEMMA_PROMPT.format(words="\n".join(group)))
    for line in text.splitlines():
        w = line.strip().lstrip("0123456789.)-•* ").strip()
        if w and " " not in w and w.endswith(("ar", "er", "ir")) and w not in seen:
            seen.add(w); infs.append(w)
    print(f"lemma batch {i}/{len(lemma_batches)}: {len(infs)} infinitives", flush=True)
    json.dump(infs, open("dist/verbs.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"lemmas done: {len(infs)}")

# Stage B: conjugate present + preterite
block = "\n".join(TENSE_LINES[t] for t in ("present", "preterite"))
conj_batches = list(chunks(infs, 20))
pairs, cards = [], []
for i, group in enumerate(conj_batches, 1):
    text = ask(CONJ_PROMPT.format(tenses=block, words="\n".join(group)))
    pairs += parse_arrow_lines(text)
    cards = lines_to_cards(pairs)
    print(f"conj batch {i}/{len(conj_batches)}: {len(cards)} cards", flush=True)
    json.dump([c.__dict__ for c in cards],
              open("dist/conj.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"DONE conj: {len(cards)} cards -> dist/conj.json")

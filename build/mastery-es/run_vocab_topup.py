"""Top up the Mexican vocab: regenerate only the forms missing from dist/vocab.json
(the ones lost to parse failures), smaller batches for reliability, merge, then
reassemble the Mastery deck."""
import json, subprocess, sys
from lib.frequency import top_forms
from lib.vocab import PROMPT, parse_vocab_json
from lib.llm import ask, chunks

cards = json.load(open("dist/vocab.json", encoding="utf-8"))
have = {c["front"] for c in cards}
forms = top_forms(2000, "data/es_top_words.csv")
missing = [f for f in forms if f not in have]
print(f"{len(cards)} have, {len(missing)} missing -> topping up", flush=True)

batches = list(chunks(missing, 30))
for i, group in enumerate(batches, 1):
    got = parse_vocab_json(ask(PROMPT.format(words="\n".join(group))))
    added = 0
    for c in got:
        if c.front not in have:
            have.add(c.front); cards.append(c.__dict__); added += 1
    print(f"batch {i}/{len(batches)}: +{added} (total {len(cards)})", flush=True)
    json.dump(cards, open("dist/vocab.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"DONE vocab: {len(cards)} cards", flush=True)

print("\n===== reassemble mastery =====", flush=True)
subprocess.run([sys.executable, "build.py", "mastery"])

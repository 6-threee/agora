from lib.llm import ask, chunks
from lib.schema import validate

VERIFY_PROMPT = """You are checking Spanish flashcards for errors. For each card
below (format: front ||| back), reply on its own line:
<front> | OK        if the translation/gloss is correct and natural
<front> | BAD: <reason>   if it is wrong
Check accents, wrong meaning, and wrong verb conjugation. Reply only these lines.

Cards:
{cards}
"""

def parse_verdicts(text):
    v = {}
    for line in text.splitlines():
        if "|" not in line:
            continue
        front, verdict = line.split("|", 1)
        front, verdict = front.strip(), verdict.strip()
        if not front:
            continue
        v[front] = verdict.upper().startswith("OK")
    return v

def verify(cards, sample=1.0, batch=40):
    errs = list(validate(cards))
    # deterministic stride sample so conjugations (sample=1.0) get full coverage
    step = max(1, int(1 / sample)) if sample > 0 else len(cards) + 1
    subset = cards[::step]
    for group in chunks(subset, batch):
        payload = "\n".join(f"{c['front']} ||| {c['back']}" for c in group)
        verdicts = parse_verdicts(ask(VERIFY_PROMPT.format(cards=payload)))
        for c in group:
            if verdicts.get(c["front"]) is False:
                errs.append(f"QC flagged {c['id']}: {c['front']} -> {c['back']}")
    return errs

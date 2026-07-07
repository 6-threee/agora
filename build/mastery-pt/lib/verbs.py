from lib.schema import Card
from lib.llm import ask, chunks, parse_arrow_lines

LEMMA_PROMPT = """From the European Portuguese word forms below, list the infinitive
of every one that is a verb form. One infinitive per line, no duplicates, no
commentary, no words that are not verbs.

Forms:
{words}
"""

TENSE_LINES = {
    "present":   "- Present indicative (presente do indicativo): eu, tu, ele/ela, nos, vos, eles",
    "preterite": "- Preterite (preterito perfeito simples): the same six persons",
    "future":    "- Future (futuro do indicativo): the same six persons",
}

CONJ_PROMPT = """You are a EUROPEAN PORTUGUESE (Portugal) conjugation generator.

For each Portuguese infinitive below, output these tense sets, using CORRECT
irregular forms where they apply (do not regularize irregular verbs). Use the
standard European Portuguese conjugation:
{tenses}

Output one conjugation per line and nothing else:
<portuguese form> → <english gloss with subject pronoun>
Use "you (informal)" for tu, "he/she" for ele/ela, "we" for nos, "you all" for
vos, "they" for eles. No headers, no blank lines, no markdown, no commentary.

Infinitives:
{words}
"""

def lemmatize_verbs(forms, batch=40):
    infs = []
    for group in chunks(forms, batch):
        text = ask(LEMMA_PROMPT.format(words="\n".join(group)))
        for line in text.splitlines():
            w = line.strip().lstrip("0123456789.)-•* ").strip()
            if w and " " not in w and w.endswith(("ar", "er", "ir", "or")):
                infs.append(w)
    seen, out = set(), []
    for w in infs:
        if w not in seen:
            seen.add(w); out.append(w)
    return out

def lines_to_cards(pairs):
    seen, cards = set(), []
    for sp, en in pairs:
        if sp in seen:
            continue
        seen.add(sp)
        cards.append(Card(sp, en))
    return cards

def conjugate(infinitives, tenses=("present", "preterite"), batch=10):
    block = "\n".join(TENSE_LINES[t] for t in tenses)
    pairs = []
    for group in chunks(infinitives, batch):
        text = ask(CONJ_PROMPT.format(tenses=block, words="\n".join(group)))
        pairs += parse_arrow_lines(text)
    return lines_to_cards(pairs)

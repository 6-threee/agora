"""Assemble Agora deck products from saved stage artifacts in dist/.

Products:
  mastery  <- vocab.json + slang.json + conj.json  (Spanish Mastery)
  phrases  <- phrases.json                          (Spanish Phrases)

Each product: assign sequential ids, validate + QC, emit deck .js, import
readme, and Gumroad zip.

Usage: python3 build.py [mastery|phrases|all]   (default: all)
"""
import json, os, sys, zipfile
from lib.schema import Card, assign_ids, validate
from lib.qc import verify

HERE = os.path.dirname(__file__)
DIST = os.path.join(HERE, "dist")

ATTRIBUTION = """## Attribution
Word frequency data is derived from the OpenSubtitles2018 corpus via
orgtre/top-open-subtitles-sentences, used under CC BY 3.0.
"""

PRODUCTS = {
    "mastery": {
        "sources": ["vocab.json", "slang.json", "conj.json"],
        "name": "Spanish Mastery",
        "deck_id": "paid:spanish-mastery",
        "basename": "es-mastery-2000",
        "price": 29,
        "blurb": "About 2,000 core Spanish words (with example sentences), a "
                 "slang and profanity section, and about 10,000 verb conjugations, "
                 "as a single importable Agora deck.",
    },
    "phrases": {
        "sources": ["phrases.json"],
        "name": "Spanish Phrases",
        "deck_id": "paid:spanish-phrases",
        "basename": "es-phrases",
        "price": 19,
        "blurb": "Hundreds of useful Spanish phrases (everyday conversation, "
                 "travel and survival, and common idioms), each with an example "
                 "in context, as an importable Agora deck.",
    },
    "slang": {
        "sources": ["slang.json"],
        "name": "Mexican Slang",
        "deck_id": "paid:mexican-slang",
        "basename": "es-slang",
        "price": 19,
        "blurb": "Real Mexican slang, expressions, and profanity that people "
                 "actually use, each with an example in context. How Mexicans "
                 "actually talk, as an importable Agora deck. Adult content.",
    },
}

def emit_deck_js(cards, name, deck_id):
    deck = {"id": deck_id, "name": name, "lang": "es", "cards": cards}
    body = "var deck = " + json.dumps(deck, ensure_ascii=False, indent=2) + ";\n"
    # Footer matches the bundled decks so the file loads in both the Node plugin
    # (module.exports) and the browser extension (window.WL). Without it,
    # ~/.agora/decks require() returns nothing and the deck never appears.
    footer = (
        'if (typeof module !== "undefined" && module.exports) module.exports = deck;\n'
        'if (typeof window !== "undefined") { var WL = (window.WL = window.WL || {}); '
        '(WL.__decks = WL.__decks || []).push(deck); }\n'
    )
    return body + footer

def _readme(name, basename, blurb):
    return (f"# {name} deck for Agora\n\n{blurb}\n\n"
            "## Import\n"
            "1. Open Agora settings (extension) or run the Agora import command (Claude Code plugin).\n"
            f"2. Load the file {basename}.js as a custom deck.\n"
            f"3. Switch your active language to {name}.\n\n"
            + ATTRIBUTION)

def _load(path):
    with open(path, encoding="utf-8") as f:
        return [Card(**o) for o in json.load(f)]

def build_product(key, qc_sample=0.1):
    p = PRODUCTS[key]
    raw = []
    for s in p["sources"]:
        path = os.path.join(DIST, s)
        if not os.path.exists(path):
            print(f"  note: {s} missing, skipping")
            continue
        raw += _load(path)
    if not raw:
        raise SystemExit(f"No source cards for {key}. Run the generators first.")

    # Dedupe by front across sections, keeping the first (richest) occurrence.
    # Source order sets priority: vocab > slang > conj, so cards with example
    # sentences win over lean conjugation forms of the same word.
    seen, deduped = set(), []
    for c in raw:
        if c.front in seen:
            continue
        seen.add(c.front)
        deduped.append(c)
    dropped = len(raw) - len(deduped)
    if dropped:
        print(f"[{key}] deduped {dropped} overlapping fronts ({len(raw)} -> {len(deduped)})")
    cards = assign_ids(deduped)

    # Hard gate: structural errors (dupes, empty fields) block packaging.
    structural = validate(cards)
    if structural:
        print(f"[{key}] {len(structural)} structural errors block packaging:")
        for e in structural[:50]:
            print("  ", e)
        raise SystemExit(f"Fix structural issues before packaging {key}.")

    # Soft gate: LLM quality flags are reported for review, not blocking
    # (the verify pass has false positives). validate() inside is now a no-op.
    quality = verify(cards, sample=qc_sample)
    if quality:
        flag_path = os.path.join(DIST, f"qc-flags-{key}.txt")
        with open(flag_path, "w", encoding="utf-8") as f:
            f.write("\n".join(quality))
        print(f"[{key}] QC flagged {len(quality)} cards for review (not blocking) -> {flag_path}")

    deck_path = os.path.join(DIST, p["basename"] + ".js")
    with open(deck_path, "w", encoding="utf-8") as f:
        f.write(emit_deck_js(cards, p["name"], p["deck_id"]))
    readme_path = os.path.join(DIST, f"README-{key}.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(_readme(p["name"], p["basename"], p["blurb"]))
    zip_path = os.path.join(DIST, p["basename"] + ".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(deck_path, p["basename"] + ".js")
        z.write(readme_path, "README.md")
    print(f"[{key}] {len(cards)} cards -> {deck_path}")
    print(f"[{key}] zip -> {zip_path}")

def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    keys = list(PRODUCTS) if which == "all" else [which]
    for k in keys:
        build_product(k)

if __name__ == "__main__":
    main()

"""Regenerate all content as European Portuguese (Portugal), then assemble the decks.
Sequential (no concurrent claude -p storms). Each generator saves incrementally.
"""
import json, subprocess, sys

def run(script):
    print(f"\n===== {script} =====", flush=True)
    r = subprocess.run([sys.executable, script])
    if r.returncode != 0:
        sys.exit(f"{script} failed (exit {r.returncode})")

# 1-4: generate vocab, verbs/conjugations, slang, phrases with the Portugal prompts
run("run_vocab.py")
run("run_verbs.py")
run("run_slang.py")
run("run_phrases.py")

# 5: conjugations. European Portuguese keeps "tu" but drops "vos" (archaic/liturgical),
# exactly as Mexican Spanish drops "vosotros". Both are tagged by the "you all" gloss.
conj = json.load(open("dist/conj.json", encoding="utf-8"))
ep = [c for c in conj if "you all" not in c["back"].lower()]
json.dump(ep, open("dist/conj.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"\nconj: dropped vos forms {len(conj)} -> {len(ep)}", flush=True)

# 6: assemble all products (QC + zips)
print("\n===== assemble =====", flush=True)
subprocess.run([sys.executable, "build.py", "all"])

"""Regenerate all content as Mexican Spanish, then assemble both decks.
Sequential (no concurrent claude -p storms). Each generator saves incrementally.
"""
import json, subprocess, sys

def run(script):
    print(f"\n===== {script} =====", flush=True)
    r = subprocess.run([sys.executable, script])
    if r.returncode != 0:
        sys.exit(f"{script} failed (exit {r.returncode})")

# 1-3: regenerate vocab, slang, phrases with the Mexican prompts
run("run_vocab.py")
run("run_slang.py")
run("run_phrases.py")

# 4: conjugations are identical in Mexico except vosotros (Spain-only). Drop the
# vosotros forms, identifiable by the "you all" gloss.
conj = json.load(open("dist/conj.json", encoding="utf-8"))
mex = [c for c in conj if "you all" not in c["back"].lower()]
json.dump(mex, open("dist/conj.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"\nconj: dropped vosotros forms {len(conj)} -> {len(mex)}", flush=True)

# 5: assemble both products (QC + zips)
print("\n===== assemble =====", flush=True)
subprocess.run([sys.executable, "build.py", "all"])

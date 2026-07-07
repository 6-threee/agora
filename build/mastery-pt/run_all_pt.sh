#!/bin/bash
# Full European Portuguese deck build: base generation + vós-drop + assemble,
# then vocab top-up and slang expansion to match the Mexican card counts.
cd /Users/jonathanluis/Desktop/agora/build/mastery-pt || exit 1
mkdir -p dist
echo "=== BUILD START $(date '+%F %T %Z') ==="
python3 run_portugal.py     || { echo "run_portugal FAILED"; exit 1; }
python3 run_vocab_topup.py  || echo "vocab_topup non-fatal error"
python3 run_slang_expand.py || echo "slang_expand non-fatal error"
python3 build.py all        || { echo "final assemble FAILED"; exit 1; }
echo "=== BUILD DONE $(date '+%F %T %Z') ==="
echo "--- card counts ---"
for f in dist/vocab.json dist/conj.json dist/slang.json dist/phrases.json; do
  [ -f "$f" ] && printf "%s: " "$f" && python3 -c "import json,sys; print(len(json.load(open('$f'))))"
done
ls -la dist/*.js dist/*.zip 2>/dev/null

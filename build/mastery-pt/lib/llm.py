import subprocess

ARROW = "→"
MODEL = "claude-sonnet-5"

def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]

def parse_arrow_lines(text):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if ARROW not in line:
            continue
        left, right = line.split(ARROW, 1)
        left, right = left.strip(), right.strip()
        if left and right:
            out.append((left, right))
    return out

def ask(prompt, model=MODEL):
    res = subprocess.run(["claude", "-p", prompt, "--model", model],
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {res.stderr[:400]}")
    return res.stdout

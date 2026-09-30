"""Extract citation contexts for citation-audit Step 2.
Prints the contexts JSON to stdout (shell-redirect to .aris/citation-audit/contexts.json)."""
import json, pathlib

CITE_OPEN = "\\" + "cite{"
files = ["main.tex"] + sorted(str(p) for p in pathlib.Path("sections").glob("*.tex"))
contexts = []
for f in files:
    lines = open(f, encoding="utf-8").read().splitlines()
    for i, line in enumerate(lines, 1):
        start = 0
        while True:
            i0 = line.find(CITE_OPEN, start)
            if i0 < 0:
                break
            i1 = line.find("}", i0)
            keys = line[i0 + len(CITE_OPEN):i1].split(",")
            lo, hi = max(0, i - 2), min(len(lines), i + 1)
            ctx = " ".join(l.strip() for l in lines[lo:hi])
            for key in keys:
                contexts.append({"key": key.strip(), "file": f, "line": i,
                                 "context": ctx[:400]})
            start = i1

keys = sorted(set(c["key"] for c in contexts))
print(f"unique cited keys: {len(keys)}", file=__import__("sys").stderr)
print("CTX_JSON_BEGIN")
print(json.dumps(contexts, indent=1, ensure_ascii=False))
print("CTX_JSON_END")


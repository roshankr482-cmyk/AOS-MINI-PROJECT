"""Pure-Python port of backend/algorithms.c + wasm_api.c (same results, same JSON).
Used automatically on Windows when no C compiler (gcc) is installed, so the project
runs with only Python. If kernelx.dll exists, the real C engine is used instead."""
import re

NAMES = ["FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK"]
MAX_REQ = 100000

def _parse(s):
    toks = [t for t in re.split(r"[,\s]+", s.strip()) if t]
    if not toks or len(toks) > MAX_REQ:
        return None
    out = []
    for t in toks:
        if not re.fullmatch(r"[+-]?\d+", t):
            return None
        v = int(t)
        if v < -1000000 or v > 1000000:
            return None
        out.append(v)
    return out

def _sweep(r, head, lo, hi, d, mode):
    s = sorted(r)
    L = [x for x in s if x < head]
    H = [x for x in s if x >= head]
    path = []                      # (pos, served)
    add = lambda p, v: path.append((p, v))
    cur = head
    def go(p, v):
        nonlocal cur
        add(p, v); cur = p
    if d:
        for x in H: go(x, 1)
        if mode == 0:
            if cur != hi: go(hi, 0)
            for x in reversed(L): go(x, 1)
        elif mode == 1:
            if cur != hi: go(hi, 0)
            if L:
                go(lo, 0)
                for x in L: go(x, 1)
        elif mode == 2:
            for x in reversed(L): go(x, 1)
        else:
            for x in L: go(x, 1)
    else:
        for x in reversed(L): go(x, 1)
        if mode == 0:
            if cur != lo: go(lo, 0)
            for x in H: go(x, 1)
        elif mode == 1:
            if cur != lo: go(lo, 0)
            if H:
                go(hi, 0)
                for x in reversed(H): go(x, 1)
        elif mode == 2:
            for x in H: go(x, 1)
        else:
            for x in reversed(H): go(x, 1)
    return path

def _sstf(r, head):
    used = [False] * len(r); cur = head; path = []
    for _ in r:
        b = -1
        for i, x in enumerate(r):
            if not used[i] and (b < 0 or abs(x - cur) < abs(r[b] - cur)):
                b = i
        used[b] = True; cur = r[b]; path.append((cur, 1))
    return path

def run(alg, reqs, head, lo, hi, d):
    if alg < 0 or alg >= 6:
        return {"error": "Unknown algorithm"}
    r = _parse(reqs or "")
    if not r:
        return {"error": "Request list is empty or contains an invalid value"}
    if lo >= hi or head < lo or head > hi:
        return {"error": "Invalid cylinder range or head position"}
    if any(x < lo or x > hi for x in r):
        return {"error": "A request is outside the cylinder range"}
    if alg == 0: path = [(x, 1) for x in r]
    elif alg == 1: path = _sstf(r, head)
    else: path = _sweep(r, head, lo, hi, 1 if d else 0, alg - 2)
    steps, cur, total = [], head, 0
    for p, v in path:
        sk = abs(p - cur); total += sk; cur = p
        steps.append({"p": p, "s": sk, "v": v})
    return {"name": NAMES[alg], "id": alg, "head": head, "min": lo, "max": hi,
            "total": total, "avg": round(total / len(r), 4), "n": len(r), "steps": steps}

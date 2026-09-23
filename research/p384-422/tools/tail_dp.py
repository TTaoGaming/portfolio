#!/usr/bin/env python3
"""Is the low-192-bit tail optimal for its digit set, and can a small digit-set change beat it?

Model (same structure as the 422 chain): prefix builds a digit dictionary and 4095 = 2^12-1; the scaffold
x12 -> x192 costs 180S + 4M; the low 192 bits of n-2 cost 192 squarings plus one multiplication per window.
The tail adds digit d at bit p after the doubling for p (acc = 2*acc + d), so the low bits must equal
sum(d_i * 2^p_i) over distinct positions; carries are allowed, so windows may overlap.

  dp      minimum tail additions for a dictionary (exact DP over positions with a carry state)
  search  greedy local search over the dictionary: add a digit a+b (1 multiplication) when it saves >= 2
          windows, drop a digit when nothing needs it and the window count does not rise.
Every improved recipe is re-verified with p384chain.check + modcheck before it is reported.

Usage:  python3 tail_dp.py [--search]
"""
from __future__ import annotations

import argparse
import itertools
import json

import p384chain as pc

LOW = pc.TARGET & ((1 << 192) - 1)
SCAFFOLD_OPS = 184  # 180S + 4M


def dp(bits: int, digits: set[int], width: int = 192):
    """Minimum number of additions to write `bits` as sum(d_i * 2^p_i), d_i in digits, distinct p_i < width.

    This is exactly what the left-to-right tail computes (acc = 2*acc + d at position p), carries included:
    windows may overlap. Low-to-high DP; state c = carry from digits placed below p (always < max digit).
    Returns (count, {position: digit}).
    """
    ds = sorted(digits)
    layer = {0: (0, None)}          # carry -> (adds, backpointer)
    back = []
    for p in range(width):
        b = (bits >> p) & 1
        nxt = {}
        for c, (k, _) in layer.items():
            for d in [0] + ds:
                t = c + d
                if (t & 1) != b:
                    continue
                c2, k2 = (t - b) >> 1, k + (d != 0)
                if c2 not in nxt or k2 < nxt[c2][0]:
                    nxt[c2] = (k2, (c, d))
        back.append(nxt)
        layer = nxt
    if 0 not in layer:
        return 10**9, {}
    wins, c = {}, 0
    for p in range(width - 1, -1, -1):
        prev_c, d = back[p][c][1]
        if d:
            wins[p] = d
        c = prev_c
    return layer[0][0], wins


def closure(prefix, needed):
    """Prefix rows (in order) needed to produce every value in `needed`."""
    parents = {a + b: (a, b) for a, b in prefix}
    keep, stack = set(), list(needed)
    while stack:
        v = stack.pop()
        if v == 1 or v in keep:
            continue
        keep.add(v); stack.extend(parents[v])
    return [(a, b) for a, b in prefix if a + b in keep]


def cost(prefix, digits):
    rows = closure(prefix, set(digits) | {pc.BASE})
    wins, tail = dp(LOW, set(digits))
    return len(rows) + SCAFFOLD_OPS + 192 + wins, rows, tail


def recipe_counts(prefix, tail):
    rows = pc.build(prefix, pc.BASE, pc.SCAFFOLD, tail)
    res = pc.check(rows, expected_counts=None, expected_sha=None)
    pc.modcheck(rows, trials=50)
    return res


def search(max_rounds=20):
    prefix = list(pc.PREFIX)
    digits = set(pc.TAIL.values())
    best, _, _ = cost(prefix, digits)
    log = [f"start {best} ops, digits {sorted(digits)}"]
    for _ in range(max_rounds):
        improved = False
        avail = {1} | {a + b for a, b in prefix}
        # try adding one new digit a+b (costs 1 multiplication, or 1 squaring if a == b)
        for a, b in itertools.combinations_with_replacement(sorted(avail), 2):
            v = a + b
            if v in avail or v >= 1 << 16:
                continue
            c, _, _ = cost(prefix + [(a, b)], digits | {v})
            if c < best:
                prefix, digits, best, improved = prefix + [(a, b)], digits | {v}, c, True
                log.append(f"add {v}={a}+{b}: {c} ops")
                break
        # try dropping a digit
        for d in sorted(digits):
            if d == 1:
                continue
            c, _, _ = cost(prefix, digits - {d})
            if c <= best - 1 or (c == best and d not in {pc.BASE}):
                if c < best or c == best:
                    if c < best:
                        log.append(f"drop {d}: {c} ops")
                        digits, best, improved = digits - {d}, c, True
                        break
        if not improved:
            break
    total, rows, tail = cost(prefix, digits)
    return total, rows, tail, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--search", action="store_true")
    a = ap.parse_args()
    digits = set(pc.TAIL.values())
    n_min, _ = dp(LOW, digits)
    print(json.dumps({"tail_windows_used": len(pc.TAIL), "tail_windows_min_for_this_digit_set": n_min,
                      "tail_is_optimal_for_its_digits": n_min == len(pc.TAIL)}))
    if a.search:
        total, rows, tail, log = search()
        print("\n".join(log))
        if total < 422:
            res = recipe_counts(rows, tail)
            print("IMPROVED (verified)", json.dumps(res))
            print(json.dumps({"prefix": rows, "tail": {str(k): v for k, v in sorted(tail.items(), reverse=True)}}))
        else:
            print(f"no improvement found by this local search (best {total})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""P-384 scalar inversion addition chain: one recipe, every export, every check.

The recipe (prefix, 2^192-1 scaffold, low-192 tail) is the single source of truth.
From it this script builds the chain and runs the checks below, then writes the exports:

  check        structure: strict ascending values, prior parents, exact sums, exact target n-2, S/M counts,
               canonical certificate SHA-256
  modcheck     the chain evaluated on real scalars mod n: result == pow(a, n-2, n) and a*result == 1 (mod n)
  exports      certificate.txt (value a b), CSV with parent step indices, addchain/chain_422.acc,
               ring/ring-style Rust (drop-in p384_scalar_inv_to_mont), all regenerated from the recipe

Usage:  python3 p384chain.py check | modcheck [--trials N] | export OUTDIR | all OUTDIR
Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973", 16)
TARGET = N - 2
S_COST = 0.8  # squaring cost relative to a multiplication (Brian Smith's weighting)

# ---- the 422 recipe (identical to verify.py / verify.js / verify.cpp) -------------------------------------
PREFIX = [(1, 1), (2, 1), (3, 3), (6, 6), (12, 12), (24, 24), (48, 48), (96, 96), (192, 3), (195, 195), (390, 390),
          (780, 780), (1560, 3), (1563, 192), (1755, 192), (1755, 780), (2535, 2), (2535, 1560)]
BASE = 4095                      # 2^12 - 1, the seed of the all-ones scaffold
SCAFFOLD = (12, 24, 48, 96)      # x12 -> x24 -> x48 -> x96 -> x192
TAIL = {186: 1, 181: 1563, 167: 1563, 162: 4095, 151: 2535, 148: 4095, 141: 1563, 135: 1947, 132: 1, 123: 2537,
        115: 3, 112: 4095, 103: 1563, 94: 195, 86: 1563, 78: 1947, 72: 2535, 60: 1947, 53: 2535, 50: 3, 34: 1563,
        29: 1755, 25: 4095, 23: 1755, 13: 2537, 7: 4095, 3: 1, 0: 2537}
EXPECTED_SHA256 = "5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70"
EXPECTED_COUNTS = (422, 382, 40)


def build(prefix=PREFIX, base=BASE, scaffold=SCAFFOLD, tail=TAIL, low_bits=192):
    """Rows (value, a, b) in order. Raises AssertionError on any structural violation."""
    rows, seen = [], {1}

    def add(a, b):
        assert a in seen and b in seen, f"parent not yet computed: {a}, {b}"
        o = a + b
        assert o not in seen and a < o and b < o, f"not a new, larger value: {o}"
        rows.append((o, a, b)); seen.add(o)
        return o

    for a, b in prefix:
        add(a, b)
    assert base in seen
    x = base
    for k in scaffold:
        start = x
        for _ in range(k):
            x = add(x, x)
        x = add(x, start)
    assert x == (1 << (12 + sum(scaffold))) - 1
    for pos in range(low_bits - 1, -1, -1):
        x = add(x, x)
        if pos in tail:
            x = add(x, tail[pos])
    return rows


def counts(rows):
    s = sum(1 for _, a, b in rows if a == b)
    return len(rows), s, len(rows) - s


def certificate(rows) -> bytes:
    return "".join(f"{o} {a} {b}\n" for o, a, b in rows).encode()


def check(rows, expected_counts=EXPECTED_COUNTS, expected_sha=EXPECTED_SHA256) -> dict:
    seen, prev = {1}, 1
    for o, a, b in rows:
        assert a in seen and b in seen and o == a + b and o > prev and a < o and b < o
        seen.add(o); prev = o
    assert prev == TARGET, "final value is not n-2"
    c = counts(rows)
    if expected_counts:
        assert c == expected_counts, c
    sha = hashlib.sha256(certificate(rows)).hexdigest()
    if expected_sha:
        assert sha == expected_sha, sha
    total, s, m = c
    return {"ops": total, "S": s, "M": m, "weighted": round(s * S_COST + m, 3), "sha256": sha}


def modcheck(rows, trials=200, seed=384) -> int:
    """Evaluate the chain on actual scalars: value v holds a^v mod n."""
    rnd = random.Random(seed)
    for t in range(trials):
        a = 2 + rnd.randrange(N - 3) if t else 2
        p = {1: a}
        for o, x, y in rows:
            p[o] = p[x] * p[y] % N
        inv = p[TARGET]
        assert inv == pow(a, N - 2, N) and a * inv % N == 1
    return trials


def csv_rows(rows):
    idx = {1: 0}
    out = ["step,op,left,right,value"]
    for i, (o, a, b) in enumerate(rows, 1):
        out.append(f"{i},{'S' if a == b else 'M'},{idx[a]},{idx[b]},{o}")
        idx[o] = i
    return "\n".join(out) + "\n"


def _bname(v):
    return "_" + format(v, "b")


def to_acc(prefix=PREFIX, base=BASE, scaffold=SCAFFOLD, tail=TAIL, low_bits=192):
    """addchain (github.com/mmcloughlin/addchain) script. Verify with: addchain eval addchain/chain_422.acc"""
    name = {1: "1"}
    lines = []
    for a, b in prefix:
        o = a + b
        name[o] = _bname(o)
        rhs = f"2*{name[a]}" if a == b else f"{name[a]} + {name[b]}"
        lines.append(f"{name[o]:<16}= {rhs}")
    width = 12
    prev = name[base]
    for k in scaffold:
        width += k
        lines.append(f"{'x' + str(width):<16}= {prev} << {k} + {prev}")
        prev = "x" + str(width)
    last, cur, i = low_bits, prev, 0
    items = sorted(tail.items(), reverse=True)
    for pos, d in items[:-1]:
        i += 1
        lines.append(f"{'t' + str(i):<16}= {cur} << {last - pos} + {name[d]}")
        cur, last = "t" + str(i), pos
    pos, d = items[-1]
    tail_shift = pos  # doublings after the last window
    expr = f"{cur} << {last - pos} + {name[d]}"
    if tail_shift:
        expr = f"({expr}) << {tail_shift}"
    lines.append(f"{'return':<16}  {expr}")
    return "\n".join(lines) + "\n"


def to_ring_rust(prefix=PREFIX, base=BASE, scaffold=SCAFFOLD, tail=TAIL, low_bits=192) -> str:
    """A drop-in body for ring's `p384_scalar_inv_to_mont` (src/ec/suite_b/ops/p384.rs), same helper functions."""
    digits = sorted(set(tail.values()))
    const = {d: f"B_{format(d, 'b')}" for d in digits}
    L = []
    w = L.append
    w("fn p384_scalar_inv_to_mont(a: Scalar<R>, cpu: cpu::Features) -> Scalar<R> {")
    w("    // Fermat: a**-1 (mod n) == a**(n - 2) (mod n).")
    c = counts(build(prefix, base, scaffold, tail, low_bits))
    w(f"    // Addition chain: {c[0]} = {c[1]} squarings + {c[2]} multiplications (research/p384-422, generated by tools/p384chain.py).")
    w("")
    w("    // mul, sqr, sqr_mut, sqr_mul, sqr_mul_acc: unchanged from ring (see src/ec/suite_b/ops/p384.rs).")
    w("")
    for i, d in enumerate(digits):
        w(f"    const {const[d]}: usize = {i}; // {d}")
    w(f"    const DIGIT_COUNT: usize = {len(digits)};")
    w("")
    w("    let mut d = [Scalar::zero(); DIGIT_COUNT];")
    w(f"    d[{const[1]}] = a;")
    ref = {1: f"&d[{const[1]}]"}
    for a, b in prefix:
        o = a + b
        rhs = f"sqr({ref[a]}, cpu)" if a == b else f"mul({ref[a]}, {ref[b]}, cpu)"
        if o in const:
            w(f"    d[{const[o]}] = {rhs}; // {o}")
            ref[o] = f"&d[{const[o]}]"
        else:
            w(f"    let b_{format(o, 'b')} = &{rhs}; // {o}")
            ref[o] = f"b_{format(o, 'b')}"
    width, prev = 12, ref[base]
    for k in scaffold:
        width += k
        nm = f"x{width}"
        if width == 12 + sum(scaffold):
            w(f"    let mut acc = sqr_mul({prev}, {k}, {prev}, cpu); // 2^{width} - 1")
        else:
            w(f"    let {nm} = &sqr_mul({prev}, {k}, {prev}, cpu); // 2^{width} - 1")
        prev = nm
    items = sorted(tail.items(), reverse=True)
    w("")
    w("    // Low 192 bits of n - 2: (squarings, digit) windows, left to right.")
    w("    #[allow(clippy::cast_possible_truncation)]")
    w(f"    static REMAINING_WINDOWS: [(u8, u8); {len(items)}] = [")
    last = low_bits
    for pos, dg in items:
        w(f"        ({last - pos}, {const[dg]} as u8),")
        last = pos
    w("    ];")
    w("    for &(squarings, digit) in &REMAINING_WINDOWS[..] {")
    w("        sqr_mul_acc(&mut acc, LeakyWord::from(squarings), &d[usize::from(digit)], cpu);")
    w("    }")
    if last:
        w(f"    for _ in 0..{last} {{ sqr_mut(&mut acc, cpu); }}")
    w("")
    w("    acc")
    w("}")
    return "\n".join(L) + "\n"


def simulate_ring_rust(src: str) -> tuple[int, int, int]:
    """Re-read the emitted Rust and evaluate it on exponents (a tiny interpreter for exactly the forms we emit)."""
    import re
    consts = {m[0]: int(m[1]) for m in re.findall(r"const (B_[01]+): usize = (\d+);", src)}
    dval = {i: None for i in consts.values()}
    env, S, M = {}, 0, 0

    def val(tok):
        tok = tok.strip().lstrip("&")
        m = re.fullmatch(r"d\[(B_[01]+)\]", tok)
        return dval[consts[m[1]]] if m else env[tok]

    for line in src.splitlines():
        line = line.split("//")[0].strip()
        if m := re.fullmatch(r"d\[(B_[01]+)\] = a;", line):
            dval[consts[m[1]]] = 1
        elif m := re.fullmatch(r"(?:d\[(B_[01]+)\]|let (\w+)) = &?sqr\((.+), cpu\);", line):
            v = 2 * val(m[3]); S += 1
            if m[1]: dval[consts[m[1]]] = v
            else: env[m[2]] = v
        elif m := re.fullmatch(r"(?:d\[(B_[01]+)\]|let (\w+)) = &?mul\((.+), (.+), cpu\);", line):
            v = val(m[3]) + val(m[4]); M += 1
            if m[1]: dval[consts[m[1]]] = v
            else: env[m[2]] = v
        elif m := re.fullmatch(r"let (?:mut )?(\w+) = &?sqr_mul\((.+), (\d+), (.+), cpu\);", line):
            k = int(m[3]); env[m[1]] = val(m[2]) * (1 << k) + val(m[4]); S += k; M += 1
    acc = env["acc"]
    for k, digit in re.findall(r"\((\d+), (B_[01]+) as u8\)", src):
        acc = acc * (1 << int(k)) + dval[consts[digit]]; S += int(k); M += 1
    if m := re.search(r"for _ in 0\.\.(\d+) \{ sqr_mut", src):
        acc <<= int(m[1]); S += int(m[1])
    assert acc == TARGET, "emitted Rust does not compute n-2"
    return S + M, S, M


def export(outdir: Path) -> dict:
    (outdir / "addchain").mkdir(parents=True, exist_ok=True)
    (outdir / "ring").mkdir(parents=True, exist_ok=True)
    rows = build()
    (outdir / "certificate.txt").write_bytes(certificate(rows))
    (outdir / "chain_422.csv").write_text(csv_rows(rows))
    (outdir / "addchain" / "chain_422.acc").write_text(to_acc())
    rust = to_ring_rust()
    (outdir / "ring" / "ring_p384_scalar_inv_to_mont_422.rs").write_text(rust)
    sim = simulate_ring_rust(rust)
    return check(rows) | {"modcheck_trials": modcheck(rows), "ring_rust_simulated": sim}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "modcheck", "export", "all"])
    ap.add_argument("outdir", nargs="?", default=".")
    ap.add_argument("--trials", type=int, default=200)
    a = ap.parse_args(argv)
    rows = build()
    if a.cmd == "check":
        print("PASS", json.dumps(check(rows)))
    elif a.cmd == "modcheck":
        print(f"PASS modcheck {modcheck(rows, a.trials)} random scalars: chain(a) == a^(n-2) mod n and a*chain(a) == 1")
    else:
        print("PASS", json.dumps(export(Path(a.outdir))))


if __name__ == "__main__":
    sys.exit(main())

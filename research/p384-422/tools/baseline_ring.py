#!/usr/bin/env python3
"""Recount ring's own P-384 scalar inversion chain from source, so the comparison is reproducible.

Reads `p384_scalar_inv_to_mont` from ring's src/ec/suite_b/ops/p384.rs (pass the file path), evaluates it on
exponents, checks it computes n-2, and prints its squaring/multiplication counts.
Pinned source used in the README: briansmith/ring @ 840167e18e4fa837eb48de46500454a616a15a6e.

Usage:  python3 baseline_ring.py path/to/p384.rs
"""
import re
import sys

N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973", 16)


def recount(src: str):
    body = src[src.index("fn p384_scalar_inv_to_mont"):]
    body = body[: body.index("\n}\n") + 3]
    consts = {m[0]: int(m[1]) for m in re.findall(r"const (B_[01]+): usize = (\d+);", body)}
    val = {name: int(name[2:], 2) for name in consts}          # B_110001 -> 49
    env, S, M = {}, 0, 0

    def v(tok):
        tok = tok.strip().lstrip("&")
        m = re.fullmatch(r"d\[(B_[01]+)\]", tok)
        return val[m[1]] if m else env[tok]

    have = {"B_1"}
    for line in body.splitlines():
        line = line.split("//")[0].strip()
        if m := re.fullmatch(r"(?:d\[(B_[01]+)\]|let (\w+)) = &?sqr\((.+), cpu\);", line):
            x = 2 * v(m[3]); S += 1
        elif m := re.fullmatch(r"(?:d\[(B_[01]+)\]|let (\w+)) = &?mul\((.+), (.+), cpu\);", line):
            x = v(m[3]) + v(m[4]); M += 1
        elif m := re.fullmatch(r"let (?:mut )?(\w+) = &?sqr_mul\((.+), (\d+), (.+), cpu\);", line):
            env[m[1]] = v(m[2]) * (1 << int(m[3])) + v(m[4]); S += int(m[3]); M += 1
            continue
        else:
            continue
        if m[1]:
            assert x == val[m[1]], f"{m[1]} computed {x}"
            have.add(m[1])
        else:
            env[m[2]] = x
    acc = env["acc"]
    for k, digit in re.findall(r"\(([\d +]+), (B_[01]+) as u8\)", body):
        k = sum(int(t) for t in k.split("+"))
        assert digit in have
        acc = acc * (1 << k) + val[digit]; S += k; M += 1
    assert acc == N - 2, "ring chain does not evaluate to n-2"
    return S + M, S, M


if __name__ == "__main__":
    total, s, m = recount(open(sys.argv[1]).read())
    print(f"PASS ring p384_scalar_inv_to_mont computes n-2: {total} = {s}S + {m}M, weighted(s=0.8) = {s * 0.8 + m:.1f}")

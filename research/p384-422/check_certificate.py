#!/usr/bin/env python3
"""Independent, dependency-free check of a P-384 n-2 addition chain."""

import hashlib
import json
import re
import sys
from pathlib import Path

N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973", 16)
EXPECTED_SHA256 = "5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70"
ROW = re.compile(r"[1-9][0-9]{0,119} [1-9][0-9]{0,119} [1-9][0-9]{0,119}")


def verify(path: Path) -> dict:
    raw = path.read_bytes()
    if not raw or len(raw) > 512_000 or not raw.endswith(b"\n") or b"\r" in raw:
        raise ValueError("size or LF newline")
    lines = raw.decode("ascii").split("\n")[:-1]
    if len(lines) > 1024:
        raise ValueError("operation limit")
    known = {1}
    previous = 1
    squarings = 0
    for index, line in enumerate(lines, 1):
        if ROW.fullmatch(line) is None:
            raise ValueError(f"row syntax {index}")
        output, left, right = map(int, line.split(" "))
        if left not in known or right not in known:
            raise ValueError(f"unavailable parent {index}")
        if output <= previous or output in known:
            raise ValueError(f"not strictly increasing {index}")
        if left >= output or right >= output or left + right != output:
            raise ValueError(f"incorrect sum {index}")
        known.add(output)
        previous = output
        squarings += left == right
    if previous != N - 2:
        raise ValueError("wrong P-384 scalar inversion target")
    multiplications = len(lines) - squarings
    if (len(lines), squarings, multiplications) != (422, 382, 40):
        raise ValueError("wrong operation counts")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("certificate SHA-256 differs")
    return {
        "valid": True,
        "operations": len(lines),
        "squarings": squarings,
        "other_multiplications": multiplications,
        "weighted_0_8": "345.6",
        "target_hex": hex(previous),
        "sha256": digest,
    }


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("usage: python verify.py certificate.txt")
        print(json.dumps(verify(Path(sys.argv[1])), sort_keys=True))
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1) from None

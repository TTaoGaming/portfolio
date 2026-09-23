#!/usr/bin/env python3
"""Run independent checkers and targeted corruptions without installed packages."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.txt"


def command(argv: list[str]) -> dict:
    run = subprocess.run(argv, cwd=HERE, text=True, capture_output=True, check=False)
    output = run.stdout.strip() if run.returncode == 0 else run.stderr.strip()
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"checker emitted invalid JSON: {argv[0]}: {output[:300]}") from exc
    return {"exit_code": run.returncode, "result": parsed}


def variants(raw: bytes) -> dict[str, bytes]:
    lines = raw.splitlines(keepends=True)
    missing = lines.copy()
    missing[0], missing[1] = missing[1], missing[0]
    wrong_sum = lines.copy()
    wrong_sum[1] = b"3 1 1\n"
    duplicate = lines.copy()
    duplicate[1] = duplicate[0]
    swapped_parents = lines.copy()
    for index, line in enumerate(lines):
        output, left, right = line.decode("ascii").strip().split(" ")
        if left != right:
            swapped_parents[index] = f"{output} {right} {left}\n".encode("ascii")
            break
    return {
        "missing_parent": b"".join(missing),
        "wrong_sum": b"".join(wrong_sum),
        "duplicate_output": b"".join(duplicate),
        "wrong_target": b"".join(lines[:-1]),
        "different_valid_certificate_hash": b"".join(swapped_parents),
        "wrong_line_endings": raw.replace(b"\n", b"\r\n"),
    }


def main() -> dict:
    raw = CERTIFICATE.read_bytes()
    rows = raw.decode("ascii").splitlines()
    values = ("1\n" + "\n".join(line.split(" ")[0] for line in rows) + "\n").encode("ascii")
    if values != (HERE / "values.txt").read_bytes():
        raise AssertionError("values.txt differs from certificate output column")
    node = shutil.which("node")
    checkers = {"python": [sys.executable, str(HERE / "check_certificate.py")]}
    if node:
        checkers["node"] = [node, str(HERE / "check_certificate.mjs")]
    positives = {}
    for name, argv in checkers.items():
        result = command([*argv, str(CERTIFICATE)])
        if result["exit_code"] != 0 or result["result"].get("valid") is not True:
            raise AssertionError(f"{name} refused original certificate: {result}")
        positives[name] = result["result"]
    shared = {"operations", "squarings", "other_multiplications", "weighted_0_8", "target_hex", "sha256"}
    if len(positives) > 1 and len({tuple(result[key] for key in sorted(shared)) for result in positives.values()}) != 1:
        raise AssertionError("independent checker outputs differ")
    negatives = {}
    path = HERE / f".negative-{os.getpid()}.txt"
    if not path.resolve().is_relative_to(HERE.resolve()):
        raise AssertionError("temporary file escaped package directory")
    try:
        for label, altered in variants(raw).items():
            path.write_bytes(altered)
            negatives[label] = {}
            for name, argv in checkers.items():
                result = command([*argv, str(path)])
                if result["exit_code"] == 0 or result["result"].get("valid") is not False:
                    raise AssertionError(f"{name} accepted {label}: {result}")
                negatives[label][name] = result["result"]["error"]
    finally:
        path.unlink(missing_ok=True)
    return {
        "schema": "p384.brian.polyglot.check.v1",
        "observed_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "python_version": sys.version.split()[0],
        "node_version": subprocess.check_output([node, "--version"], text=True).strip() if node else "UNAVAILABLE",
        "positive": positives,
        "negative": negatives,
        "negative_checks_passed": sum(len(v) for v in negatives.values()),
        "values_projection_matches": True,
        "external_verification": "NOT_CLAIMED",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, help="write JSON receipt to this path")
    args = parser.parse_args()
    result = main()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")

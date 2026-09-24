"""Recalculate the descriptive ARM64 timing statistics from arm64_pairs.csv."""
import csv
from pathlib import Path
from statistics import median

rows = list(csv.DictReader(Path(__file__).with_name("arm64_pairs.csv").open(newline="")))
assert len(rows) == 160
assert {(int(r["run"]), int(r["pair"])) for r in rows} == {
    (run, pair) for run in range(1, 5) for pair in range(40)
}

def describe(part):
    base = [int(r["baseline_ns"]) / int(r["reps"]) / 1000 for r in part]
    candidate = [int(r["candidate_ns"]) / int(r["reps"]) / 1000 for r in part]
    paired_gain = [100 * (b - c) / b for b, c in zip(base, candidate)]
    return {
        "blocks": len(part),
        "candidate_faster": sum(g > 0 for g in paired_gain),
        "median_paired_gain_pct": round(median(paired_gain), 3),
        "median_baseline_us": round(median(base), 3),
        "median_candidate_us": round(median(candidate), 3),
    }

print("all", describe(rows))
for run in range(1, 5):
    print(f"run_{run}", describe([r for r in rows if int(r['run']) == run]))

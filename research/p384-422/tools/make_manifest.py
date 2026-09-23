#!/usr/bin/env python3
"""Write MANIFEST.json: the machine-readable register of this packet (for agents, mirrors and quorum).

packet_sha256 = sha256 over the sorted lines "<sha256>  <path>\n" of every packet file, excluding
MANIFEST.json itself and quorum verdicts (quorum/*.json), so verdicts can cite the packet they checked.
The same bytes can be mirrored to GitHub, Cloudflare and Arweave and checked against this digest.
"""
import hashlib
import json
from pathlib import Path

import p384chain as pc

HERE = Path(__file__).resolve().parent.parent  # research/p384-422


def packet_files():
    for p in sorted(HERE.rglob("*")):
        rel = p.relative_to(HERE).as_posix()
        if p.is_dir() or rel == "regenerated.txt" or "__pycache__" in rel or rel == "MANIFEST.json" or (rel.startswith("quorum/") and rel.endswith(".json")):
            continue
        yield rel, hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    files = dict(packet_files())
    digest = hashlib.sha256("".join(f"{h}  {f}\n" for f, h in sorted(files.items())).encode()).hexdigest()
    rows = pc.build()
    res = pc.check(rows)
    m = {
        "schema": "hfo.review_packet.v1",
        "packet": "p384-scalar-inversion-422",
        "packet_sha256": digest,
        "status": "CANDIDATE_OPEN_FOR_REVIEW",
        "target": {"curve": "NIST P-384", "modulus": "group order n", "n_hex": format(pc.N, "x"), "exponent": "n-2",
                   "use": "scalar inversion by Fermat: a^-1 = a^(n-2) mod n"},
        "result": {"ops": res["ops"], "squarings": res["S"], "multiplications": res["M"], "weighted_s_0_8": res["weighted"],
                   "certificate": {"file": "certificate.txt", "sha256": res["sha256"], "format": "one row per op: value left right"}},
        "baselines": [
            {"source": "ring p384_scalar_inv_to_mont @840167e18e4fa837eb48de46500454a616a15a6e", "S": 382, "M": 48, "total": 430,
             "how": "recounted by tools/baseline_ring.py", "evidence": "baselines/ring_840167e_recount.txt"},
            {"source": "Brian Smith, Elliptic Curve Inversion Addition Chains (2017-05-31); ring 0.17.14", "S": 381, "M": 52, "total": 433,
             "url": "https://briansmith.org/ecc-inversion-addition-chains-01"},
            {"source": "mmcloughlin/addchain v0.4.0 search", "total": 434, "evidence": "baselines/addchain_v0.4.0_search_n-2.txt"},
        ],
        "checks": [
            {"id": "python", "cmd": "python3 verify.py", "expect": "PASS 422 382S 40M sha256=" + res["sha256"]},
            {"id": "node", "cmd": "node verify.js", "expect": "PASS 422 382S 40M sha256=" + res["sha256"]},
            {"id": "cpp", "cmd": "g++ -std=c++17 -O2 verify.cpp -o v && ./v", "expect": "PASS 422 382S 40M"},
            {"id": "fast", "cmd": "python3 check.py", "expect": "certificate, projections and six negative controls pass"},
            {"id": "recipe", "cmd": "python3 tools/p384chain.py check", "expect": "PASS"},
            {"id": "mod_n", "cmd": "python3 tools/p384chain.py modcheck --trials 200", "expect": "PASS modcheck 200"},
            {"id": "addchain", "cmd": "addchain eval addchain/chain_422.acc", "expect": "total: 422 doubles: 382 adds: 40"},
            {"id": "ring_ecdsa", "cmd": "git apply ring/ring_840167e_p384_422.patch && cargo test --release --test ecdsa_tests",
             "expect": "7 passed; 0 failed", "at": "briansmith/ring@840167e"},
            {"id": "tail_dp", "cmd": "python3 tools/tail_dp.py", "expect": "tail_is_optimal_for_its_digits: true"},
        ],
        "claim_boundary": ["candidate only", "no global optimality claim", "no novelty claim beyond the public baselines listed",
                           "no native speed or side-channel claim beyond the ring code it replaces", "no external acceptance yet"],
        "quorum": {"families_required": ["anthropic", "openai", "moonshot", "google"], "verdicts": "quorum/*.json",
                   "rule": "four distinct families CONFIRMED, no open CONTRADICTED"},
        "mirrors": {"github": "https://github.com/TTaoGaming/portfolio/pull/1", "cloudflare": None, "arweave": None},
        "files": files,
    }
    (HERE / "MANIFEST.json").write_bytes((json.dumps(m, indent=1) + "\n").encode("utf-8"))
    print(digest)


if __name__ == "__main__":
    main()

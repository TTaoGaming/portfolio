# Independent ARM64 timing of the P-384 scalar inverse candidate

Observed 2026-09-24 UTC. This is a test-only appendix to the frozen 422-operation packet at `2c8c62d350a1f3bb60ee824c9ae3d6d04e63eaf5`. It does not modify `research/p384-422/` or change that packet's hash.

## Result and claim boundary

On an Oracle ARM64 VM (Neoverse-N1, 2 vCPUs, Linux aarch64, Rust/Cargo 1.93.0), the patched `ring@840167e18e4fa837eb48de46500454a616a15a6e` passed its 12 P-384 library tests. The benchmark build also passed 4 filtered ECDSA library tests and 7 ECDSA integration tests. An independently written, same-binary paired benchmark compared the original `p384_scalar_inv_to_mont` with the replacement from patch SHA-256 `87cffbd989c075123d8b3d5e993ca208337c81d064cdacbbe1f0c619735e33c9`.

Four runs each timed 40 alternating-order pairs of 1,000 inversions. The median paired improvement was **1.92%** over 160 pairs; 153 pairs favored the replacement. Per-run medians were 1.91%, 1.88%, 1.92%, and 1.91%. The medians of block time per inversion were 76.88 µs baseline and 75.42 µs replacement. The complete block measurements are in [`arm64_pairs.csv`](arm64_pairs.csv), SHA-256 `e11e75b1fd0a8d0dd8fe56abfd25f27cc7555a631c260a86f551b55d2ff1924a`.

This supports a speed improvement for this inversion function on this ARM64 VM. It does not establish a speedup on other CPUs or a measurable ECDSA sign/verify speedup. This VM is shared, was not CPU-pinned, and no side-channel or production readiness assessment was made. Each timed call used the same nonzero scalar (7); the inversion exponent is fixed. The test also compares the two outputs before timing. The first three runs used an equivalent test source; the fourth was a fresh-worktree replay of the exact `inject_bench.py` in this folder.

## Reproduce on a disposable `ring` clone

Download the two small files directly: the [frozen patch](https://raw.githubusercontent.com/TTaoGaming/portfolio/2c8c62d350a1f3bb60ee824c9ae3d6d04e63eaf5/research/p384-422/ring/ring_840167e_p384_422.patch) and [`inject_bench.py`](inject_bench.py). Check their SHA-256 hashes: patch `87cffbd989c075123d8b3d5e993ca208337c81d064cdacbbe1f0c619735e33c9`, script `bf56b8fde8af28c5e9d21ca09addeeee5903ff11adc524f88fb3520dea861d40`.

```sh
git clone https://github.com/briansmith/ring.git ring-p384-bench
cd ring-p384-bench
git checkout 840167e18e4fa837eb48de46500454a616a15a6e
git apply --check /path/to/ring_840167e_p384_422.patch
git apply /path/to/ring_840167e_p384_422.patch
python3 /path/to/inject_bench.py
cargo test --release --lib independent_p384_speed::paired_scalar_inversion -- --nocapture --test-threads=1
```

The script reads the original function from the pinned commit, renames it as the baseline, and adds a test-only paired benchmark alongside the patched function. Both functions are marked `#[inline(never)]` for comparison. The test checks equal outputs, warms both functions, and alternates AB/BA order. It prints one `HFO_PAIR` row per timing block. No benchmark code or baseline function is part of the proposed production patch.

The frozen [certificate and verifier](../p384-422/README.md) establish the abstract 422-operation chain separately from these runtime measurements.

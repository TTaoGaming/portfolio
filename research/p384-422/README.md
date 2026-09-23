# P-384 scalar inversion: 422-operation review candidate

This folder is a self-contained addition chain for the P-384 scalar subgroup
order `n` raised to `n - 2`. It is a candidate for review, not a claim of
optimality, novelty, production speed, side-channel safety, or acceptance by
`ring`.

## Fastest check

Run from this folder with Python 3.9 or later:

```sh
python3 check.py
```

No Python packages or network access are needed. `check.py` checks the frozen
certificate independently in Python and, if installed, Node.js; checks that
`values.txt` matches it; and confirms that both checkers reject six altered
certificates. Its JSON output names every check and the coverage actually run.
On Windows, use `python check.py`.

The expected result is `422 = 382S + 40M`, weighted cost `0.8S + M = 345.6`,
ending exactly at the P-384 subgroup order minus two. The certificate's SHA-256
is `5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70`.

## Files and independent routes

| File | Purpose |
| --- | --- |
| `certificate.txt` | Frozen 422-row chain. Each ASCII decimal line is `output left_parent right_parent` followed by LF. The implicit initial exponent is `1`. |
| `values.txt` | Initial `1` and the certificate output column, one value per line. |
| `TEST_VECTOR.json` | Modulus, target, counts, score, and frozen digest. |
| `check_certificate.py`, `check_certificate.mjs` | Independent parsers of the frozen certificate; neither imports a generator. |
| `verify.py`, `verify.js`, `verify.cpp` | Separate reconstructions from the compact prefix, scaffold, and tail schedule. |
| `check.py` | Positive readback and six negative controls in each available parser. |

For individual checks:

```sh
python3 check_certificate.py certificate.txt
node check_certificate.mjs certificate.txt
python3 verify.py --emit regenerated.txt
node verify.js
g++ -std=c++17 -O2 verify.cpp -o verify_cpp && ./verify_cpp
```

The C++ reconstructor needs Boost.Multiprecision headers; it has no link-time
Boost dependency. The committed certificate lets a reviewer inspect or use the
chain without running any generator. The reconstructor output is checked
against the same target, counts, and (for Python and Node) digest.

## Construction and accounting

The 16-operation star prefix reaches `4095`:

`1,2,3,6,12,24,48,96,192,195,390,780,1560,1563,1755,2535,4095`.

Two retained helpers are `1947 = 1755 + 192` and `2537 = 2535 + 2`.
The `M12 -> M24 -> M48 -> M96 -> M192` scaffold follows. The remaining
192-bit tail uses these `bit_position:digit` additions:

```text
186:1, 181:1563, 167:1563, 162:4095, 151:2535, 148:4095,
141:1563, 135:1947, 132:1, 123:2537, 115:3, 112:4095,
103:1563, 94:195, 86:1563, 78:1947, 72:2535, 60:1947,
53:2535, 50:3, 34:1563, 29:1755, 25:4095, 23:1755,
13:2537, 7:4095, 3:1, 0:2537
```

The prefix costs `10S + 6M`, helpers `2M`, scaffold `180S + 4M`,
and tail `192S + 28M`: **382S + 40M = 422**.

## Comparison and use boundary

At [`ring` commit 840167e](https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p384.rs),
`p384_scalar_inv_to_mont` has, by source-level count, `382S + 48M = 430`:
digit preparation `3S + 9M`, six scaffold `sqr_mul` calls `187S + 6M`,
and 33 remaining windows `192S + 33M`. Under this operation-count model,
the candidate uses eight fewer unequal-parent multiplications and the same
number of squarings. That is a comparison to this pinned revision only; it
does not measure native runtime or establish a drop-in `ring` patch.

The certificate is the review object. Mapping its retained intermediates to
`ring`'s `Scalar<R>` variables, checking representation and aliasing, and
benchmarking on target platforms remain integration work.

[NEXT_SEARCH.md](NEXT_SEARCH.md) is a separate, optional one-page map of
explored and open search directions and a measured-compute protocol.

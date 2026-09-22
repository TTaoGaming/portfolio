# P-384 scalar inversion: 425-operation review candidate

**Author:** Tommy Tai. **Status:** internally checked; independent review pending.
This is a research-review package, not a production cryptography library or an accepted record.

## Start here

- [One-page review](P384_425_Review.pdf)
- [Exact chain](p384_scalar_inversion_425.txt): 425 lines of `output_exponent left_exponent right_exponent`.
- [Numerically sorted chain](p384_scalar_inversion_425_sorted.txt): equivalent ordering for parsers requiring increasing values.
- [Haskell expression](P384Scalar425.hs): optional representation; the file comment describes the original 2026-09-21 packaging pass. It was subsequently compiled and replayed on 2026-09-22 using Brian Smith's exact attached Haskell framework.
- [Brian Smith Haskell framework replay](verification/brian_haskell_replay_2026-09-22.md): fresh GHC replay using the exact `ECCInversionAdditionChains.lhs` and `AdditionChainComputation.lhs` files from Brian's email.
- [Reproduction and checks](verification/): source only. No compiled binaries, credentials, or private correspondence.

## Precise claim

For the P-384 scalar group order

```
n = 0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973
```

the canonical sequence constructs **n - 2** using **380 squarings and 45 other multiplications (425 total)**. Exponent 1 is the only free starting value; precomputation is included. Each row satisfies `output = left + right`, and both input exponents have already been constructed. No operation is unused. The sequence can be applied to nonzero scalar-field elements to compute inversion; zero has no inverse.

The identified comparison is the scalar-inversion implementation in [ring at commit 840167e](https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p384.rs#L160): 382 squarings + 48 other multiplications, 430 total. The candidate reduces both counts by 2 and 3 respectively. This fixed comparison is not an exhaustive prior-art survey.

## Verify without an AI system

Download this directory's files, keeping the `verification/` subdirectory. For the smallest exact replay, Python 3.10+ is enough:

```sh
python verification/verify_python.py p384_scalar_inversion_425.txt
```

Optional independent implementation replays:

```sh
node verification/verify_node.mjs p384_scalar_inversion_425.txt
g++ -std=c++17 -O2 verification/verify_cpp.cpp -o /tmp/p384-check
/tmp/p384-check p384_scalar_inversion_425.txt
```

The C++ checker needs Boost headers. To rerun the full candidate-only test panel (Python, Node, g++, Boost; OpenSSL parameter cross-check when available):

```sh
python verification/check_review_package.py
```

The supplied [test receipt](verification/results.json) records 3 exact-integer implementations agreeing on the endpoint/counts, 20 negative controls rejected by each implementation (60 total), and 1,413 nonzero modular-inversion examples. Wrong-target but internally valid chains are included among the negative controls. The receipt is an internal execution record, not external certification. The full test command overwrites its local `verification/results.json` with the new execution record.

A fresh 2026-09-22 replay also compiled this candidate with **Brian Smith's exact two Haskell source attachments** and used his `AdditionChainComputation` measurements. It returned `target_matches=True`, `r=425`, `d=380`, and `f=45`. As a control, Brian's historical P-384 scalar chain contained in the attached `ECCInversionAdditionChains.lhs` returned `433 = 381 + 52`. That historical attachment is distinct from the newer `ring` implementation Brian cited as `430 = 382 + 48`. See the [full replay receipt](verification/brian_haskell_replay_2026-09-22.md).

The compact [recipe](verification/recipe425.py) and [data-only expander](verification/recipe_evaluator.py) regenerate the canonical sequence. On systems where text output uses CRLF, normalize output to ASCII LF before comparing the byte hash.

## Method and limitations

The candidate came from AI-assisted evolutionary search over small precomputation dictionaries and an overlapping positive-digit tail representation. The recipe documents reconstruction, not every historical search trajectory or model call. Further search can explore new intermediate values and joint tail/dictionary changes while preserving a fixed target and evaluator.

The package does **not** prove shortest-chain optimality, global novelty, measured native-code speedup, side-channel safety, or suitability for production use. The checkers are different implementations but are still internally prepared; review of their assumptions and of this precise claim is welcome. No outside acceptance or endorsement is claimed.

## Integrity

Canonical SHA-256:

```
14da9fd3bfa7e3e615c78c5d6cf73dc0262ea3ff65eb29553be502de37f0df05
```

All distributed file hashes are listed in [SHA256SUMS](SHA256SUMS). This web package replaces a rejected email attachment bundle; the mathematical certificate is unchanged. No archive needs to be attached to email.

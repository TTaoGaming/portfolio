# P-384 scalar inversion: 421-operation review candidate

**Tommy Tai · 25 September 2026 UTC**

This is a frozen addition chain for the P-384 scalar subgroup order `n` raised to `n − 2`. It follows [Brian Smith's P-384 scalar-inversion work](https://briansmith.org/ecc-inversion-addition-chains-01). The certificate uses **421 operations = 380 squarings + 41 other multiplications**. On the `0.8 × squarings + multiplications` yardstick, its cost is **345.0**.

| Chain | Squarings | Other multiplications | Total | 0.8S + M |
| --- | ---: | ---: | ---: | ---: |
| This candidate | 380 | 41 | 421 | 345.0 |
| [Earlier 422 candidate](https://github.com/TTaoGaming/portfolio/pull/3) | 382 | 40 | 422 | 345.6 |
| [Brian's published 2017 chain](https://briansmith.org/ecc-inversion-addition-chains-01) | 381 | 52 | 433 | 356.8 |

## Two-minute check

The [certificate](certificate.txt) is the review object. Each line is `output left_parent right_parent`, in decimal, with an implicit starting exponent of `1`. Each output must equal the sum of two earlier exponents.

Download this folder or clone the repository, then run with Python 3.9 or later:

```sh
python3 research/p384-421/check.py
```

On Windows use `python`. The [checker](check.py) has no dependencies or network calls. It checks the SHA-256 of the exact certificate bytes, every parent and sum, the target exponent, the operation counts, four fixed modular inversion inputs, and rejection of four altered certificates. Expected output contains `"valid": true`, `"operations": 421`, `"squarings": 380`, and `"other_multiplications": 41`.

Certificate SHA-256: `844866b0703ef55ca41fc616a7226fe6d8aca3022ead18cdaec1e0911422e02e`.

## Verification status and limits

The frozen bytes passed the bundled checker on 25 September 2026. A separate Kimi/Moonshot run wrote its own checker, confirmed the 421/380/41 counts and `n − 2` target, replayed the result, and rejected three altered inputs. That is **one outside-family review**, not a completed multi-family quorum. The bundled checker is part of this packet and should be treated as author-supplied.

This is a candidate addition chain. It does not establish novelty, global optimality, constant-time or side-channel safety, a production-ready `ring` patch, or a speed improvement. The earlier 422 candidate has separate implementation and timing evidence; those results do not transfer to this 421 certificate. Deeper independent and implementation verification can follow.

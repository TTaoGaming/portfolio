# P-384 scalar inversion — 422-operation review candidate

Frozen reviewer packet for the P-384 scalar inverse exponent `n - 2`.

## Candidate

- operations: **422**
- squarings: **382**
- other multiplications: **40**
- weighted score at squaring cost `s = 0.8`: **345.6**
- canonical decimal-row certificate SHA-256: `5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70`

Research status: **candidate**. No claim of global optimality, prior-art novelty, native production speedup, side-channel properties, or external acceptance.

The target is the P-384 scalar modulus `n` documented in Brian Smith's `ring` implementation, minus two:
https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p384.rs

## Construction

16-operation star chain to `4095`:

`1,2,3,6,12,24,48,96,192,195,390,780,1560,1563,1755,2535,4095`

Paid retained helpers:

- `1947 = 1755 + 192`
- `2537 = 2535 + 2`

Then the standard `M12 -> M24 -> M48 -> M96 -> M192` scaffold.

Low-192 tail additions (`bit_position:digit`):

`186:1, 181:1563, 167:1563, 162:4095, 151:2535, 148:4095, 141:1563, 135:1947, 132:1, 123:2537, 115:3, 112:4095, 103:1563, 94:195, 86:1563, 78:1947, 72:2535, 60:1947, 53:2535, 50:3, 34:1563, 29:1755, 25:4095, 23:1755, 13:2537, 7:4095, 3:1, 0:2537`

Accounting:

- base chain: `10S + 6M`
- helpers: `2M`
- M12→M192 scaffold: `180S + 4M`
- tail: `192S + 28M`
- total: **`382S + 40M = 422`**

## Verify

Three independently implemented exact reconstructors are included:

```bash
python3 verify.py --emit certificate_422.txt
node verify.js
g++ -std=c++17 -O2 verify.cpp -o verify_cpp && ./verify_cpp
```

Each rebuilds the chain and checks strict increasing outputs, prior/smaller parents, exact sums, exact final P-384 `n-2` target, and exact operation counts. Python and Node also assert the canonical row SHA-256 above.

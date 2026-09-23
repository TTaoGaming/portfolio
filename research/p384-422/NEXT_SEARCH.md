# P-384 addition-chain search map

This is an optional planning note. The [certificate](certificate.txt) and
[checks](README.md#fastest-check) establish this candidate's arithmetic; this
note does not establish optimality or any search-wide negative result.

## Frozen judge

Start at exponent `1`. Each operation adds two previously obtained exponents;
the result must increase strictly. Finish at the P-384 subgroup order `n-2`.
Record `(S, M, 0.8S + M, S + M)` and the full decimal-row certificate. A
prospective improvement needs independent Python and Node replay and a lower
weighted cost or a Pareto improvement in `(S, M)` against `(382, 40)`.

## Where the local search has concentrated

The construction in this packet uses a 16-operation prefix to `4095`, two
retained helpers, the `M12 -> M192` scaffold, and a low-192-bit tail. Local
search notes report variants of the prefix, helper insertions, retained
scaffold ancestors, and tail reuse. The last extra helper attempts traded one
new helper multiplication for one saved tail multiplication. Those are
correlated, bounded experiments, not a proof that any region is exhausted.

## Three next islands

1. **Joint schedule search:** vary prefix, retained helpers, scaffold
   boundaries, and tail digits together instead of freezing the dictionary.
2. **General DAGs:** allow useful non-star intermediates to feed distant parts
   of the chain, rather than only the current accumulator.
3. **Different decomposition:** vary split points and retained bases instead
   of requiring the `M12 -> M192` scaffold.

For a comparable pilot, pre-register a seed and evaluator version and run one
bounded batch of 100 *unique valid* genotypes per island. Record generated,
deduplicated, valid, independently verified, improved, CPU time, and cost.
Keep 20% of a fixed budget for validation and follow-up. A batch succeeds only
if a frozen certificate improves the stated judge and survives independent
replay. Local mutant counts without common denominators and costs cannot be
turned into credible success probabilities.

After the pilots, allocate one batch at a time by sampling each island's
success probability from an explicitly stated prior/posterior and dividing
by its measured cost per batch (Thompson sampling). An illustrative
`Beta(1,9)` prior can initialize each island; it is a planning assumption,
not a result inferred from the current search. Stop or change islands at
each budget checkpoint. Preserve every failed batch's denominator so later
allocation reflects evidence rather than the volume of search attempts.

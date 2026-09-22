# Brian Smith Haskell framework replay — 2026-09-22

Purpose: fresh verification of the canonical P-384 scalar-inversion candidate using the exact two Haskell source files attached by Brian Smith in his 2026-09-14 email.

## Inputs

- Brian attachment `ECCInversionAdditionChains.lhs`
  - SHA-256: `41b36ecf60024771f4d0ea1d81ece718b68b03a86125243fe1fe0db6ab0318cb`
- Brian attachment `AdditionChainComputation.lhs`
  - SHA-256: `8d2b2a9fc10f259eed267b166000b09c9ed6b539856cf080bf28a54375f5b86f`
- Candidate Haskell serialization `P384Scalar425.hs`
  - SHA-256: `fc89a745124cf0679b7dfe60a4e870535e7ff4591a37faf5ad62ffa70b04a219`
- Canonical candidate `p384_scalar_inversion_425.txt`
  - SHA-256: `14da9fd3bfa7e3e615c78c5d6cf73dc0262ea3ff65eb29553be502de37f0df05`

## Environment

- GHC 9.8.4, official Haskell release bundle
- Release bundle SHA-256 matched the publisher's SHA256SUMS before use.
- Execution host: Linux ARM64.
- Brian's exact `AdditionChainComputation` definitions of `denote`, `r`, `d`, and `f` were used.

## Fresh output

```text
candidate_denote=39402006196394479212279040100143613805079739270465446667946905279627659399113263569398956308152294913554433653942641
candidate_target_matches=True
candidate_r=425
candidate_d=380
candidate_f=45
brian_control_denote=39402006196394479212279040100143613805079739270465446667946905279627659399113263569398956308152294913554433653942641
brian_control_target_matches=True
brian_control_r=433
brian_control_d=381
brian_control_f=52
```

Fresh output SHA-256: `4bab7a583c5d00e0b39be92567a5c4b62279c70e8db5b0a8cea12095c02148b7`.

## Interpretation

Brian's own Haskell computation framework confirms that the candidate reaches the exact P-384 scalar group-order-minus-two exponent and measures it as **425 total operations = 380 doubles/squarings + 45 non-doubling adds/multiplications**.

As a control, the historical P-384 scalar chain contained in Brian's attached `ECCInversionAdditionChains.lhs` reaches the same endpoint and measures **433 = 381 + 52** in that framework.

That historical attachment is distinct from the newer `ring` implementation Brian cited in his email, which he described as **430 = 382 squarings + 48 multiplications**. This replay does not claim to execute or reconstruct that newer `ring` chain.

## Claim ceiling

This is a fresh internal replay using Brian's exact attached checker sources. It is strong reproducibility evidence, but it is not Brian's independent verification, external acceptance, proof of global optimality, proof of novelty, or a native performance benchmark.

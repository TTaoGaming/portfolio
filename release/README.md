# Public research snapshot v1

`p384-422-public-snapshot-v1.json` is an immutable-publication candidate. It
contains Tommy Tai's already-published article and the frozen 422-row P-384
certificate, with source commit IDs, UTC timestamps, and SHA-256 digests. It
contains no local paths, email addresses, Slack content, or credential values.

Build it with `python release/build_capsule.py --packet-root <portfolio PR #1
checkout> --blog-root . --output release/p384-422-public-snapshot-v1.json`.
The expected payload is 80,747 bytes with SHA-256
`e43ffcf70c09e4fa50870c346d6e421c4916b63c1b97f63e91b6db32b379bf75`.
The certificate inside has SHA-256
`5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70`.

One unauthenticated ArDrive Turbo free-tier upload attempt was rejected with
HTTP 402 at `2026-09-23T22:09:41.653Z`. The service quoted 23,624 micro-USDC.
No transaction ID or public GET-back exists. The receipt records
`REJECTED_PAYMENT_REQUIRED`; **this snapshot is not on the Permaweb**.
Do not infer permanent publication from this local file or GitHub copy.

The upload adapter accepts only a payload below 100,000 bytes and an
unauthenticated client, with no paid wallet. If a funded route is separately
authorized, bind a positive spend ceiling, preserve the exact payload hash,
make one attempt, and verify the returned transaction by public GET and hash.

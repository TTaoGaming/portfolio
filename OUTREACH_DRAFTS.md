# P-384 pull outreach — UTC log and draft copy

## Published

| UTC | Surface | URL | Receipt |
| --- | --- | --- | --- |
| 2026-09-23 21:49:16 | Tommy Tai research blog | https://tommytai.dev/posts/p384-422/ | Cloudflare Pages deployment `65f2003c-cad4-433f-9137-b3c286ffc1f1` completed at `21:49:16.544286Z`; HTTPS 200; Pages custom domain, verification, and validation read back active. |

The article is the authored anchor. The review packet and certificate are in
https://github.com/TTaoGaming/portfolio/pull/1. The blog source is draft PR
https://github.com/TTaoGaming/portfolio/pull/2.

## First social post — draft, not sent

**LinkedIn version**

I published a reproducible P-384 scalar inversion candidate today: a
422-operation addition chain (382 squarings, 40 other multiplications).

The complete certificate and Python, Node, and C++ checks are public. I used
AI-assisted search to find candidates and deterministic verification to decide
which result to freeze. The post explains the method, the evidence, and what
the operation count does *not* establish. I would welcome independent review,
especially from people familiar with addition chains or `ring` integration.

Research note: https://tommytai.dev/posts/p384-422/

Review packet: https://github.com/TTaoGaming/portfolio/pull/1

**X version**

I published a reproducible P-384 scalar inversion candidate: 422 operations
(382S + 40M). Frozen certificate + Python/Node/C++ checks are public. This is
an arithmetic result, not a speed or optimality claim. Independent review
welcome. https://tommytai.dev/posts/p384-422/

## This week's proposed follow-ups — not scheduled

| UTC target | Topic | Evidence anchor |
| --- | --- | --- |
| 2026-09-24 16:00 | How to check the 422-row certificate in one command | `python3 check.py` in PR #1 |
| 2026-09-26 16:00 | What AI-assisted search proposed and what deterministic verification proved | Blog method section and `NEXT_SEARCH.md` |
| 2026-09-27 16:00 | Invite independent arithmetic and integration review | Blog and PR #1 |

No social post or scheduled platform action is represented as complete until
the exact platform URL and UTC send time are appended here.

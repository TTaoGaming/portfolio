---
title: Verification log — FIELD_GUIDE.md
status: PROPOSE-ONLY. Grep-verified against source on 2026-08-05. No source files edited.
---

# Verification log

Method: every claim/citation used in `FIELD_GUIDE.md` was grep-matched against the actual source
files in `C:\Dev\hfo_gen_133_forge\areas\coordination\heritage_manifest_gen134\` — the taxonomy
(`FAILURE_MODE_TAXONOMY.md`, v1.1.0, 59 closed ids), the falsification audit
(`FALSIFICATION_AUDIT.md`), and the manifest (`capacity_manifest_ALL_SOURCES.v8.jsonl`, 1,006 data
atoms + 2 header/bootstrap rows = 1,008 lines total). Nothing below was invented; every row
quoted in the guide is reproduced here with its source location and match count.

| # | Mode in guide | Source row / doc | Match | Verified |
|---|---|---|---|---|
| 1 | M1_frame_override — "zero warm network" | `FAILURE_MODE_TAXONOMY.md` M1 row | `grep -c "zero warm network"` → 1 | ✅ |
| 1b | M1_frame_override — "kickstart the hive" | manifest row `thindeep_g106_incident_kickstart_disobedience` | `grep -c` → 1 | ✅ |
| 2 | M2_false_green — "5e PHB Ch.7" | manifest row `attridx_5_007_l100_raw_hallucination_invented_a_log2_s` | `grep -c "5e PHB Ch.7"` → 1 | ✅ |
| 3 | M7_x_shaped_y — research treadmill / 0 sends | manifest row `m7_research_treadmill` | `grep -c` → 1 | ✅ |
| 4 | RH_fake_green — gen-95 pong, 176/176 green, mutation_score 0 | manifest row `gen95_pong_gold_deployed_mutation_zero` | `grep -c` → 1 | ✅ |
| 4b | RH_fake_green — self-caught, staged workflow YAML | manifest row `attridx_1_016_self_caught_fake_green_i_committed_the_e` | `grep -c "attridx_1_016"` → 1 | ✅ |
| 5 | RH_phantom_citation — fb07f523, 7 gens / 839 files, recompute mismatch | manifest rows `geno_fb07f523_cross_gen_null_gene` + `g130_fb07f523_null_gene` (+1 more mention) | `grep -c` → 3 total mentions | ✅ |
| 6 | RH_destructive_shortcut — gen-114 `rm -rf`, ADR-0008 | manifest row `g114_rm_rf_founding_incident_most_significant` | `grep -c` → 1 | ✅ |
| 7 | M_FALSE_ABSENT — HopeOS, 998 docs / 127MB DuckDB | `FALSIFICATION_AUDIT.md` §1a + §1g (2 independent audit passes) | `grep -c "hfo_memory.duckdb"` → 2 | ✅ |
| 7b | M_FALSE_ABSENT — audit tally, 26 reclassified FALSE_ABSENT, 0 traced to timeout | `FALSIFICATION_AUDIT.md` §3 Tally table | `grep -c "Reclassified \*\*FALSE_ABSENT"` → 1 (table header); full counts read directly from §3 | ✅ |
| 8 | M10_silent_capability_regression — "fired once in 47h" | manifest row `attridx_1_042_silently_degraded_self_reports_active_ho` | `grep -c` → 1 | ✅ |
| 9 | M14_self_consistency_as_verification — cross-family Codex correction | `FAILURE_MODE_TAXONOMY.md` S4_cross_family_review row + M14 row | `grep -c "S4_cross_family_review"` → 1 | ✅ |
| 10 | RH_privileged_without_lease — largest single finding, gen-130 audit | `FAILURE_MODE_TAXONOMY.md` RH-series table | `grep -c "RH_privileged_without_lease"` → 1 | ✅ |

**Mode count claimed in the guide's closer:** "10 of 59 named failure/reward-hack modes." The
taxonomy's own frontmatter states 59 closed ids (M1–M18 + `M_FALSE_ABSENT` + RH-series + S-series
+ R-series + G-series). Counted directly from the taxonomy's own section headers and confirmed
against the manifest's `failure_mode_id` value distribution (52 distinct non-null ids observed
across 1,006 atoms, via `python3` frequency count on 2026-08-05).

**Atom count claimed in the guide's frontmatter:** "1,006 atoms." This is a direct correction —
the task brief that requested this guide said "843+ atoms," which is a stale figure from an
earlier manifest draft (v8's own header row states an **attribution** ceiling of "261 of 843
rows carry an attributable model_family" — that 843 is a sub-count for one field, not the total
row count). The actual, current, counted total in `capacity_manifest_ALL_SOURCES.v8.jsonl` is
**1,006 data atoms** (1,008 lines total, minus 2 header/bootstrap rows), confirmed by direct
Python line-count and JSON-parse on 2026-08-05. This guide uses the counted number, not the
brief's stale one.

## honest_flaw

- **Taxonomy provenance caveat carried forward, not resolved.** The taxonomy itself states that
  M10–M18 (which includes M10, M14, and M_FALSE_ABSENT — three of the ten modes in this guide)
  are `⚠️PROPOSED`, not yet operator-ratified, and were derived by a Claude-Opus-5 lane from
  failures largely committed by Claude-family lanes — the taxonomy's own document calls this
  "the M14 conformation exactly" and asks for a cross-family review pass before treating M10–M18
  as settled. This guide presents them as-is, with that caveat now stated here rather than hidden.
  M1–M9 and the RH-series (used for 5 of the 10 modes: M1, M2, M7, RH_fake_green,
  RH_phantom_citation, RH_destructive_shortcut, RH_privileged_without_lease) are already
  operator-facing canon and do not carry this caveat.
- **The "26 reclassified FALSE_ABSENT, 0 traced to timeout" tally (mode 7) is itself audit-pass
  output, not independently re-run by this guide-writing pass.** It is quoted from
  `FALSIFICATION_AUDIT.md` §3 verbatim; this guide did not re-execute the 8 parallel falsification
  passes, only grepped that they exist and say what's quoted.
- **fb07f523 (mode 5) is described as "a completely different hash" — the actual two values
  (`fb07f523` vs `15e89641`) are visually and numerically unrelated, confirmed by direct string
  comparison; not a rounding or truncation artifact.**
- **This guide does not claim the 10 selected modes are the 10 most important or most frequent.**
  Frequency counted directly from the manifest: `RH_fake_green` (24 rows), `M_FALSE_ABSENT` (22
  rows), and `M12_scaffold_abandoned_mid_flight` (23 rows, not covered in this guide) are among the
  most-populated non-`unclassified`/non-`not_applicable` ids. Mode selection here favored
  **one strong, checkable receipt per mode** and topical spread (the task brief's named examples
  plus a mix of behavioral/mechanistic/absence modes) over raw frequency ranking.
- **No source files were modified, moved, or deleted to produce this guide or this verification
  log** — read-only grep/Python passes only, per the PROPOSE-ONLY instruction. `world_effects_taken: 0`.

*Truthful-red > false-green.*

# Non-USD Cross Data Population — Sprint 001 Summary

**Branch:** `research-nonusd-cross-data-population-001`
**Date:** 2026-05-29
**Type:** data population + validation. No factor discovery, no front-gate
screen, no campaign, no strategy, no approval. Freeze intact.

## 1. Branch

`research-nonusd-cross-data-population-001` (off clean `origin/main` tip
`245bde2`).

## 2. Commit hashes by phase

| Phase | Hash | Deliverable |
|-------|------|-------------|
| 0 | `e17c60b` | baseline audit + plan |
| 1 | `d3649b7` | ingestion plan |
| 2 | `44c752a` | M1 ingestion (8 crosses) |
| 3 | `96b9f93` | data validation |
| 4 | `be17651` | materialization |
| 5 | `32540c5` | cost baseline (descriptive) |
| 6 | `d71988d` | data readiness review |
| 7 | `e3f56cb` | next prompt |
| 8 | (this commit) | final validation + summary |

## 3. Instruments ingested

All eight first-wave crosses — 4 required + 4 optional (all feasible):
EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY (required); NZD_JPY, EUR_CHF, GBP_CHF,
EUR_AUD (optional). Window 2021-05-26 → 2026-05-26 (matched to the majors'
M1 horizon). OANDA practice, read-only, candle endpoint only.

## 4. Row counts (M1, read back from store)

| Cross | M1 rows |
|-------|---------|
| EUR_GBP | 1,823,232 |
| EUR_JPY | 1,841,779 |
| GBP_JPY | 1,852,770 |
| AUD_JPY | 1,857,000 |
| NZD_JPY | 1,845,840 |
| EUR_CHF | 1,811,686 |
| GBP_CHF | 1,838,790 |
| EUR_AUD | 1,849,425 |
| **total** | **14,720,522** |

Single `fetch_batch_id` per cross, 100% `data_hash`, **0 duplicate
timestamps, 0 bid>ask, 0 non-positive spreads**. Counts sit in the majors'
band (~1.83M avg).

## 5. Coverage results

`validate_nonusd_cross_data.py --scope all`: `metadata_check: PASS`, **8/8
ingested**, `not_ingested: []`. Hard-integrity checks all zero. Quality
status `WARN` on 7/8 (benign FX-closure missing-minute heuristic — a control
major, USD_JPY, also WARNs), `PASS` on EUR_AUD. `h4_consistency` WARN =
no native H4 (M1-only, expected). On-the-fly M1→TF coverage ratios match
the expected 1/5, 1/15, 1/60, 1/240 fractions.

## 6. Materialization results

M5/M15/H1/H4M1 materialized for all 8 crosses (source `m1_materialized`,
config hash `f9b7246b79a0635c` = same as majors). Totals: M5 2,871,688 /
M15 925,019 / H1 213,774 / H4M1 40,403 = **4,050,884 derived bars**.
Independent `--verify-only` re-derivation: **PASS 8/8 across all 4
timeframes — 0 OHLC mismatches, 0 missing, 0 extra, expected==stored
everywhere.** 100% `fetch_batch_id`; timestamps aligned to the M1 window.
(The first materialize run was killed during its verify pass after writes
completed; the independent verify confirms correctness regardless.)

## 7. Cost-baseline findings (descriptive only)

Measured M1 spreads (pips): crosses are **wider and less stable** than the
comparable majors.

- Cross median spread **1.4–3.1p** vs majors **1.3–1.9p**.
- Cross p99 **8.4–19.9p** vs majors **4.9–11.8p**; cross spread-volatility
  (std) **1.3–3.2p** vs majors **0.65–1.5p**.
- **EUR_GBP (1.4p)** is the only near-major-cost cross; AUD_JPY (1.9p) /
  EUR_CHF (1.6p) moderate; **GBP_JPY (3.1p), EUR_AUD (2.6p), NZD_JPY (2.5p),
  GBP_CHF (2.2p)** carry a higher cost wall with fat tails.
- Session shape mirrors the majors (tightest london, widest overlap).
- Confirms the standing thesis: crosses are a **breadth/replication
  expansion, not a cost fix** — the cost wall is *higher* than the majors
  the programme was already cost-defeated on. **No edge claim is made.**

## 8. Readiness decision

`DATA_READY_FOR_DISCOVERY_PLANNING`. All first-wave crosses are populated,
validated, materialized (parity PASS), and cost-profiled to the major-pair
standard. Factor discovery is **technically justified to PLAN on real data**
— but is **not performed and not authorized** by this sprint.

## 9. Was any campaign created?

**No.** No CAMPAIGN_032, no campaign of any kind.

## 10. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`; freeze
gate confirms loops refuse every configured strategy.

## 11. Do paper/demo/live remain blocked?

**Yes.** No strategy approved; freeze gate PASS; live financing blocker
unchanged.

## 12. Recommended next sprint

**Cross factor-discovery PLANNING only** (branch
`research-nonusd-cross-factor-discovery-planning-001`): a design document,
pre-screen/pre-campaign/pre-strategy, opening from the measured cost
reality, prioritizing C1 *fresh independent replication* + data-blocked
breadth families, with the cost-realism gate up front and explicit stop
criteria. See `NEXT_PROMPT_AFTER_NONUSD_CROSS_DATA_POPULATION.md`.

## 13. Files to review first

1. `docs/research/NONUSD_CROSS_DATA_VALIDATION_RESULT.md` — integrity + spreads.
2. `docs/research/NONUSD_CROSS_MATERIALIZATION_RESULT.md` — parity PASS.
3. `docs/research/NONUSD_CROSS_COST_BASELINE.md` — measured cost vs majors.
4. `docs/research/NONUSD_CROSS_DATA_READINESS_REVIEW.md` — readiness decision.
5. `docs/research/NEXT_PROMPT_AFTER_NONUSD_CROSS_DATA_POPULATION.md` — what's next.

## Validation results (Phase 8)

- `pytest tests/ -q` → **2440 passed, 3 skipped** (local-data skips; no code
  changed this sprint).
- `ruff check src scripts tests` → **4 errors, all pre-existing** in
  `scripts/run_edge_discovery_vol_managed_tsmom.py` (C031).
- `check_research_freeze.py` → **ALL CHECKS PASSED**.
- `validate_research_archive.py` → **ALL CHECKS PASSED**.
- `scan_artifacts_for_secrets.py` → **PASSED**.
- `git status --short` → clean.

## Success criterion (met)

The first-wave non-USD crosses are populated (14.72M M1 rows), validated
(integrity clean), materialized (4.05M derived bars, parity PASS), and
cost-profiled (measured spreads vs majors) — so future research can begin
from real data rather than infrastructure assumptions. No strategy,
campaign, factor screen, or trading logic was created; only compact
manifests and docs are committed (no raw datasets).

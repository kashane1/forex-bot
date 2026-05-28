# USD_JPY London Compression-Continuation Confirmation 001 — Summary

**Sprint:** `usdjpy-london-compression-continuation-confirmation-001`
**Branch:** `research-usdjpy-london-compression-continuation-confirmation-001` (branched
from the compression/expansion diagnostic tip `cd8e27c`, per instruction).
**Date:** 2026-05-28
**Outcome:** read-only confirmation diagnostic. **No campaign, no C024, no C023 execution,
no strategy, no verdict change, no approval, TEST sealed, paper/demo/live blocked.**

---

## 1. What this sprint did

Subjected the single surviving lead from the compression/expansion line — post-compression
**London-session breakout continuation** — to a strict, overfit-hardened confirmation:
realistic cost variants, an intrabar protective-stop model (absent before), and a
multiple-testing haircut. The lead **failed**, so the verdict is `PAUSE_STRATEGY_RESEARCH`.

## 2. Commit hashes by phase

| phase | hash | what |
|---|---|---|
| 0 | `2add067` | branch, audit, baseline, plan |
| 1 | `8dabae0` | locked lead definition |
| 2 | `0ef16f3` | confirmation simulator + result |
| 3 | `a2125e5` | robustness/falsification |
| 4 | `8e74537` | readiness decision (PAUSE) |
| 5 | (this commit) | final validation + summary |

## 3. Files changed by phase

- **0:** `docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_CONFIRMATION_001_PLAN.md`
- **1:** `docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_LOCKED_DEFINITION.md`
- **2:** `scripts/confirm_usdjpy_london_compression_continuation.py`,
  `research/usdjpy_london_compression_continuation/confirmation_summary.json`,
  `docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_CONFIRMATION_RESULT.md`, `.gitignore`
- **3:** `docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_ROBUSTNESS.md`
- **4:** `docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_READINESS_DECISION.md`
- **5:** this summary

Scope: `docs/research/`, `scripts/`, `research/`, `.gitignore` only. **No** `src/`,
broker/executor/order/live, or `configs/` changes.

## 4. Locked lead definition

USD_JPY M15, **London session only**, compressed (≥3 of 4 percentile features
{range,ATR,bandwidth,realized-vol} ≤ 0.20), **first prior-16-bar-range break continuation**,
horizons **h16 & h32**, train+validation only, TEST sealed. Frozen in Phase 1 before any
re-analysis; no session/horizon/cut/filter search permitted.

## 5. Dataset coverage & TEST seal

95,756 M15 bars (read-only research DB), 2021-06-01..2025-06-29; **3,065** London
compressed-continuation trades. **TEST 2025-07+ sealed** — loader hard-bounds to
`< 2025-07-01`; no raw TEST reads.

## 6. Cost assumptions

Round-trip pips: **optimistic 2.2** (~1 spread + 0.5 slip), **base 4.4** (2× median 1.7 +
1.0 slip), **conservative 5.8** (2× p90 1.9 + 2.0 slip); whipsaw charges one extra
round-trip. (The prior sprint's "+2.2/+6.1" was at base, no stop.)

## 7. Stop assumptions

Intrabar protective stops, adverse-first (conservative): **none / range 1.0× / range 1.5×
/ ATR 1.0×**. Entry at the broken level; exit at stop or horizon close, whichever first.

## 8. h16/h32 train/validation results

No-stop, base cost (reproduces the prior lead): h16 **+1.04 / +3.04**, h32 **+2.21 /
+6.12** (train/val). **With any protective stop, base cost:** h16 −5.94/−6.30 (range1.0×),
h32 −6.97/−7.70 — strongly negative on both splits at both horizons. Conservative cost,
no stop: h16 train **−0.65** (flips negative).

## 9. Robustness checks

11 checks run. Decisive failures: **stop model destroys it** (#10), **conservative cost
flips h16 train negative** (#9/#2), **year robustness** — the effect is concentrated in
trend years 2022 (train) & 2024 (val) and is negative/flat in 2021/2023/2025 (#4/kill #8),
**multiple-testing haircut removes significance** in realistic configs. Clean: London-only
(no rollover/off-hours contamination), sample adequate (n≈690–850/split), TEST untouched.

## 10. Multiple-testing haircut result

Bonferroni ×12 (1 of 12 prior cells). No-stop base: h16 fails both splits (adj-p 1.0 /
0.977); h32 fails on **train** (adj-p 1.0), passes val (0.041). Only h32 at the
*unrealistic* optimistic cost passes both. **Haircut removes significance in every
realistic configuration.**

## 11. Readiness decision

**`PAUSE_STRATEGY_RESEARCH`.** Fails 4 of 8 strict gates (2, 3, 5, 6) including the
decisive intrabar-stop gate. The compression→expansion family is now fully explored and
exhausted as an internal lead.

## 12–16. Invariants (verified Phase 5)

| # | check | expected | actual |
|---|---|---|---|
| 12 | C023 executed? | no | **no** |
| 13 | C024 created? | no | **no** |
| 14 | Any verdict changed? | no | **no** (`validate_research_archive` PASS) |
| 15 | Any strategy approved? | no | **no** (`approved: []`) |
| 16 | Paper/demo/live blocked? | yes | **yes** (freeze gate: loops refuse) |

Also: TEST untouched; no broker/executor changes; no OANDA mutation/order calls; no
credentials/DBs staged; no huge artifacts staged.

## 17. Tests & validation commands

- `pytest tests/ -q` → **2006 passed, 3 skipped.**
- `ruff check src tests scripts research` → **All checks passed.**
- `check_research_freeze.py` / `validate_research_archive.py` → **ALL CHECKS PASSED.**
- `scan_artifacts_for_secrets.py` → **PASSED** (pattern + value scan with `.env` loaded).
- `git status --short` → clean.

## 18. Pre-existing skips/failures

3 skips, all pre-existing data-absence (`test_cost_atlas` H4; 2× `test_compare_entries`
C008 CSVs). No failures.

## 19. Remaining blockers

- The London lead is falsified under realism → no internal compression/expansion lead
  remains.
- No internal USD_JPY price-structure lead currently survives a hardened test (C022/C023
  retired; microstructure entry/management closed; compression/expansion exhausted).
- No strategy approved; nothing paper/demo/live-eligible.

## 20. Exact files to review first

1. `docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_READINESS_DECISION.md` (verdict)
2. `docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_CONFIRMATION_RESULT.md` (result grid)
3. `docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_ROBUSTNESS.md` (falsification)
4. `docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_LOCKED_DEFINITION.md` (locked terms)
5. `scripts/confirm_usdjpy_london_compression_continuation.py` + `research/usdjpy_london_compression_continuation/confirmation_summary.json`

## 21. Recommended next sprint

Given `PAUSE_STRATEGY_RESEARCH`, the recommended next sprint is **not** a strategy lane.
Two defensible options (each a separate, later, non-campaign sprint):

- **`infra-external-data-overlays-for-blocked-theses-001`** — build the maintained
  economic-event calendar + timeline-aligned rates/risk (FRED) research features that the
  atlas scorecard flagged as blocking theses #7 (macro/calendar) and #8 (carry/rates/
  risk-off). Infrastructure only; no strategy, no campaign.
- **Hold/freeze** strategy research until a genuinely new, externally-sourced,
  structurally-distinct thesis with a mechanism appears (re-enter the external-thesis
  sourcing framework rather than mining USD_JPY price structure further).

No campaign, no C024, no approval follows from this sprint.

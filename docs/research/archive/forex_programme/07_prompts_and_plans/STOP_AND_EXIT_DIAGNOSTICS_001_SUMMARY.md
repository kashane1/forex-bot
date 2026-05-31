# Stop and Exit Diagnostics — Sprint 001 Summary

**Date:** 2026-05-26  
**Branch:** `research-stop-and-exit-diagnostics-001`  
**Base branch:** `research-c008-mean-reversion-post-mortem-001`

> **No strategy approved.** C008/C009 remain **REJECT**. CAMPAIGN_018 not created. No retuning. No new trade performance claims. All outputs `strategy_evidence: false`.

---

## 1. Branch name

`research-stop-and-exit-diagnostics-001`

## 2. Commit hashes by phase

| phase | commit | message |
|---:|---|---|
| 0 | `2b1a4d3` | docs: phase 0 stop and exit diagnostics plan and truth audit |
| 1 | `a783d27` | research: phase 1 exit artifact inventory |
| 2 | `7282380` | research: phase 2 cross-campaign exit pathology matrix |
| 3 | `4cd9279` | research: phase 3 C008/C009 focused exit forensics |
| 4 | `8108ac6` | research: phase 4 stop distance and MAE/MFE diagnostics |
| 5 | `02cacbb` | docs: phase 5 future exit research hypothesis classification |
| 6 | `3d61baa` | docs: phase 6 future exit research gate requirements |
| 7 | `b70fbe5` | docs: phase 7 archive and backlog updates |
| 8 | *(this commit)* | docs: phase 8 final summary and validation close-out |

## 3. Files changed by phase

| phase | key paths |
|---:|---|
| 0 | `STOP_AND_EXIT_DIAGNOSTICS_001_PLAN.md`, `scripts/run_exit_diagnostics.py` |
| 1 | `exit_artifact_inventory.json`, `EXIT_ARTIFACT_INVENTORY.md` |
| 2 | `cross_campaign_exit_matrix.json`, `.csv`, `CROSS_CAMPAIGN_EXIT_PATHOLOGY_MATRIX.md` |
| 3 | `c008_c009_exit_forensics.json`, `C008_C009_EXIT_FORENSICS.md` |
| 4 | `stop_distance_adverse_excursion.json`, `STOP_DISTANCE_AND_ADVERSE_EXCURSION_DIAGNOSTICS.md` |
| 5 | `FUTURE_EXIT_RESEARCH_HYPOTHESES.md` |
| 6 | `FUTURE_EXIT_RESEARCH_GATE.md` |
| 7 | `EVIDENCE_INDEX.md`, `FUTURE_RESEARCH_BACKLOG.md`, `EVIDENCE_MANIFEST.json` |
| 8 | this summary |

## 4. Exit artifact inventory status

**14/14 campaigns** have usable local trade lists after path fix for C011–C014 fold layouts.

| status | campaigns |
|---|---|
| DEDUP_SAFE | C015 deduped |
| NULL_BASELINE_REQUIRES_RERUN | C011 deduped |
| LIKELY_CONTAMINATED | C002–C004, C007–C010, C012–C014, C008, C009 |
| UNKNOWN | C016, C017 |

All scanned CSVs expose `exit_reason`, `bars_held`, `r_multiple`, `spread_paid`, `stop_price` where trades exist. `ambiguous_exit` / `gap_fill` on fold campaigns C010–C017 only.

## 5. Cross-campaign exit pathology findings

- **Stop/time sign split is not C008-specific.** C011 random-entry null shows stop −0.83R vs time +0.21R — same structural pattern without an edge thesis.
- **Hard-stop expectancy clusters near −0.75R to −0.95R** across families (MR, breakout, rotation, null).
- **Time exits positive but insufficient** to lift overall expectancy above zero in most campaigns (C010–C017, C015 deduped).
- **C008** (contaminated): 68% stops (−0.795R), 32% time (+1.880R).
- **Trailing-stop campaigns** (C002–C004, C007): ~80% trailing ≈ 0R; hard stops still −0.72R to −0.82R.
- **C009 midline target** replaced C008 time exits (41% target at +1.18R vs C008 time +1.88R).

## 6. C008/C009 exit forensic findings

- Train stops: 153 @ −0.802R; validation stops: 88 @ −0.785R — **stable across splits**.
- Train time: 62 @ +1.894R; validation time: 50 @ +1.827R; validation winners 44/44 via time exit.
- Stops/time exits **distributed across all pairs and major sessions** — no single cluster explains split.
- Spread ~1.5 pips in all buckets — **cost does not explain** stop/time divergence.
- C009 train overall **−0.025R** (worse than C008 train −0.017R); target exit **capped** trades that C008 would hold to 40-bar time exit.

## 7. Stop-distance / adverse-excursion findings

- Median stop distance: **~45.5 pips** (C008/C009, unchanged between variants).
- C008 stop exits: **58.9%** reached ≥1R favorable before stopping; **41.1%** never reached 1R favorable.
- C008 time exits: median **MFE 3.33R**, median **MAE 0.50R** — survivors reverted after adverse excursion.
- C009 target exits: median **MFE 1.83R** vs C008 time **3.33R** — quantifies winner capping.

## 8. MAE/MFE computed or blocked?

**Computed** for C008 (823 trades) and C009 (403 trades) from H4 deduped candles between entry and exit. R-normalized by entry–stop distance. Other campaigns not computed (would require per-campaign candle joins; out of sprint scope).

## 9. Retuning performed?

**No.**

## 10. New strategy campaign created?

**No.** CAMPAIGN_018 not created.

## 11. New trade performance claim?

**No** — descriptive diagnostics on existing REJECT campaign artifacts only.

## 12. Strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

## 13. CAMPAIGN_018 created?

**No.**

## 14. Paper/demo/live remain blocked?

**Yes.** No executor/broker changes. No OANDA order API calls.

## 15. Archive/freeze validation results

| check | result |
|---|---|
| `pytest tests/ -q` | **1653 passed** |
| `ruff check src tests scripts research` | **All checks passed** |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** (paper/demo loops refuse) |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** (398 evidence-index links resolve) |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** |
| `git status --short` | summary doc only (no secrets/bulk artifacts staged) |

## 16. Remaining blockers

| blocker | status |
|---|---|
| C008/C009 evidence **LIKELY_CONTAMINATED** | blocks promotion / precommit |
| Test lockbox | not opened |
| Financing on multi-day holds | unmodeled |
| Exit structure | unresolved — framework-wide stop/time artifact + C008-specific tail capture |
| Broad strategy search | **paused** |

## 17. Recommended next sprint and why

**`infra-deduped-c008-c009-rerun-forensic-only-001`**

Stop/time pathology is visible even in C011 null, but **C008/C009-specific forensics cannot support pre-registration** until a dedup-safe forensic replay reproduces exit-reason parity on frozen entries. Financing modeling and exit-hypothesis precommit are **deferred until** clean replay confirms artifact integrity.

Alternatives not selected:

- `research-exit-hypothesis-precommit-001` — hypotheses classified but blocked without clean ledger
- `research-financing-modeled-pnl-and-carry-readiness-001` — important for 40-bar holds but secondary to contamination
- `infra-backtrader-exit-parity-diagnostics-001` — not primary blocker (pathology visible in bespoke artifacts + null)
- `infra-cot-positioning-feature-ingest-001` — positioning not identified as primary exit failure mode

## 18. Files to review first

1. [`docs/research/CROSS_CAMPAIGN_EXIT_PATHOLOGY_MATRIX.md`](CROSS_CAMPAIGN_EXIT_PATHOLOGY_MATRIX.md) — is stop/time split C008-only?
2. [`docs/research/C008_C009_EXIT_FORENSICS.md`](C008_C009_EXIT_FORENSICS.md) — train/validation and C009 target capping
3. [`docs/research/STOP_DISTANCE_AND_ADVERSE_EXCURSION_DIAGNOSTICS.md`](STOP_DISTANCE_AND_ADVERSE_EXCURSION_DIAGNOSTICS.md) — MAE/MFE: bad entries vs tight stops
4. [`research/exit_diagnostics/cross_campaign_exit_matrix.json`](../../research/exit_diagnostics/cross_campaign_exit_matrix.json) — machine-readable matrix
5. [`docs/research/FUTURE_EXIT_RESEARCH_GATE.md`](FUTURE_EXIT_RESEARCH_GATE.md) — requirements before any exit campaign

---

## Sprint diagnostic questions — answers

| # | question | answer |
|---|---|---|
| 1 | C008 stop/time split unique? | **No** — visible in C010–C017, C015, C016, and **C011 null** |
| 2 | Stops too tight, badly placed, or bad entries? | **Mixed** — ~41–47% never 1R favorable; ~53–59% reached 1R then stopped |
| 3 | Time exits = delayed reversion or validation luck? | **Delayed reversion descriptively** (high MFE, 40-bar hold); not validation-only at framework level (null also time-positive) |
| 4 | C009 failed because midline capped winners? | **Yes descriptively** — target MFE ~1.83R vs C008 time ~3.33R; train worsened |
| 5 | Legitimate future exit hypotheses? | See [`FUTURE_EXIT_RESEARCH_HYPOTHESES.md`](FUTURE_EXIT_RESEARCH_HYPOTHESES.md) — pre-register on **new campaign ID**, not C008/C009 retune |

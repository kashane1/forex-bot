# USD_JPY Volatility-Compression → Expansion Diagnostic 001 — Summary

**Sprint:** `usdjpy-volatility-compression-expansion-diagnostic-001`
**Branch:** `research-usdjpy-volatility-compression-expansion-diagnostic-001` (branched
from the atlas sprint tip `78ab191`, per instruction — depends on the atlas docs/tooling).
**Date:** 2026-05-28
**Outcome:** read-only diagnostic. **No campaign, no C024, no C023 execution, no strategy,
no verdict change, no approval, TEST sealed, paper/demo/live blocked.**

---

## 1. What this sprint did

Tested whether intraday volatility-compression states on USD_JPY (M15) lead to
measurable, cost-surviving range expansion that could justify a future precommit design.
Built a pure, no-lookahead compression/expansion taxonomy module (+ tests), a read-only
train+validation dataset, a predeclared-bucket analysis, and a bounded monetization
diagnostic. Ended at a readiness decision.

## 2. Commit hashes by phase (this sprint)

| phase | hash | what |
|---|---|---|
| 0 | `c8aa2d7` | branch, audit, baseline, plan |
| 1 | `00cc998` | compression/expansion taxonomy module + 10 tests |
| 2 | `99fb59b` | diagnostic dataset (manifest + preview; parquet gitignored) |
| 3 | `f5fd654` | analysis result |
| 4 | `f87c8df` | monetization diagnostic |
| 5 | `0868b37` | readiness decision |
| 6 | (this commit) | final validation + summary |

(The branch descends from the atlas sprint; `git log main..HEAD` also shows the 7 atlas
commits `a13741e..78ab191`.)

## 3. Files changed by phase

- **0:** `docs/research/USDJPY_VOLATILITY_COMPRESSION_EXPANSION_DIAGNOSTIC_001_PLAN.md`
- **1:** `src/forex_bot/research/volatility_compression_expansion.py`,
  `tests/unit/test_volatility_compression_expansion.py`
- **2:** `scripts/build_usdjpy_volatility_compression_expansion_dataset.py`,
  `research/usdjpy_vol_compression_expansion/{dataset_manifest.json,feature_preview.csv}`,
  `.gitignore`
- **3:** `scripts/analyze_usdjpy_volatility_compression_expansion.py`,
  `research/usdjpy_vol_compression_expansion/analysis_summary.json`,
  `docs/research/USDJPY_VOLATILITY_COMPRESSION_EXPANSION_DIAGNOSTIC_RESULT.md`, `.gitignore`
- **4:** `scripts/analyze_usdjpy_compression_expansion_monetization.py`,
  `research/usdjpy_vol_compression_expansion/monetization_diagnostic.json`,
  `docs/research/USDJPY_COMPRESSION_EXPANSION_MONETIZATION_DIAGNOSTIC.md`
- **5:** `docs/research/USDJPY_VOLATILITY_COMPRESSION_EXPANSION_READINESS_DECISION.md`
- **6:** this summary

Scope: `docs/research/`, `scripts/`, `research/`, one new `src/forex_bot/research/` module
+ its test, `.gitignore`. **No** broker/executor/order/live/configs changes.

## 4. Dataset coverage & TEST seal

95,756 M15 bars, **2021-06-01 .. 2025-06-29**, train 59,852 / validation 35,904. **TEST
2025-07-01+ excluded** (builder hard-refuses `--end` past the lockbox; no code reads
2025-07+). Read-only research Postgres `market_data.candles`; full bid/ask + spread.

## 5. Compression definitions implemented

Decision-time, no-lookahead: (1) range trailing-percentile, (2) ATR trailing-percentile,
(3) Bollinger bandwidth trailing-percentile, (4) realized-vol trailing-percentile,
(5) inside-bar count. Consensus "compressed" = ≥3 of the 4 percentile features ≤ cut
(primary 0.20; grid 0.10/0.20/0.30). Causality proven by a truncation unit test.

## 6. Expansion labels implemented

Future bars (labels only), horizons 4/8/16/32: forward range, signed move, MFE, MAE,
breakout up/down/any, breakout follow-through, false-breakout. Tagged direction-agnostic
vs directional.

## 7. Strongest train/validation findings

- **Compression → SMALLER absolute future range** at every horizon, both splits, all
  cuts, all features (abs range ratio 0.78–0.93). This is **volatility clustering**, the
  opposite of the breakout thesis.
- **Proportional (range/ATR) expansion is real** (ratio 1.08–1.29 both splits) but not
  tradable on its own.
- **Direction is null** (p_up 0.44–0.53, sign-inconsistent across splits).
- **Only stable positive:** mildly elevated post-compression breakout follow-through at
  h16/h32 (both splits).

## 8. Session / cost sensitivity

No session makes direction predictable. Cost: rollover/off-hours are cost-hostile
(M5: 32.4% of compressed bars); active-session + no-rollover overlay reaffirmed. The one
positive monetization cell is London-session continuation (see §9).

## 9. Monetization diagnostic result

Net of an **optimistic** 4.4-pip round-trip: **aggregate monetizations FAIL** the
both-splits bar — M2 continuation −4.9/−1.5 (h16 train/val), M3 fade strongly negative,
M4 active-session −4.3/+0.01; all lose on train; whipsaw 0.27–0.43 is a major drag.
**One honestly-flagged LEAD (not edge):** post-compression **London-session continuation**
is positive on both splits at both horizons (+1.0/+3.0 h16, +2.2/+6.1 h32 train/val, win
rate ~0.54), with a coherent Tokyo-compression→London-open mechanism — but **post-hoc**
(1 of 12 cells), under optimistic cost, level-fill entry, no intrabar stop.

## 10. Readiness decision

**`MORE_DIAGNOSTICS_REQUIRED`.** Broad thesis NOT_READY/falsified for tradability; the
London lead earns at most **one** precommitted, overfit-hardened, realistic-cost
(slippage + intrabar stop + multiple-testing haircut) read-only confirmation, with a hard
kill → `PAUSE_STRATEGY_RESEARCH` on a null. Scored against 7 gates (1/2/5 fail for the
broad thesis; 2/3/5 unproven for London).

## 11–15. Invariants (verified Phase 6)

| # | check | expected | actual |
|---|---|---|---|
| 11 | C023 executed? | no | **no** (no result/gate-decision artifacts) |
| 12 | C024 created? | no | **no** (no `CAMPAIGN_024*`) |
| 13 | Any verdict changed? | no | **no** (`validate_research_archive` PASS) |
| 14 | Any strategy approved? | no | **no** (`approved: []`) |
| 15 | Paper/demo/live blocked? | yes | **yes** (freeze gate: loops refuse) |

Also: TEST window not touched; no broker/executor changes; no OANDA mutation/order calls;
no credentials/DBs staged; no huge artifacts staged (parquet gitignored).

## 16. Tests & validation commands run

- `pytest tests/ -q` → **2006 passed, 3 skipped** (1996 prior + 10 new module tests).
- `ruff check src tests scripts research` → **All checks passed.**
- `check_research_freeze.py` / `validate_research_archive.py` → **ALL CHECKS PASSED.**
- `scan_artifacts_for_secrets.py` → **PASSED** (pattern scan; value scan PASSED with
  `.env` loaded).
- `git status --short` → clean.

## 17. Pre-existing skips/failures

3 skips, all pre-existing data-absence (unchanged): `test_cost_atlas` (H4 store absent);
2× `test_compare_entries` (C008 CSVs absent). No failures.

## 18. Remaining blockers

- London-continuation lead is unproven under realistic execution (slippage, intrabar
  stop) and multiple-testing correction → gated behind the precommitted confirmation.
- Broad compression→expansion thesis is falsified for tradability.
- No strategy approved; nothing paper/demo/live-eligible.

## 19. Exact files to review first

1. `docs/research/USDJPY_VOLATILITY_COMPRESSION_EXPANSION_READINESS_DECISION.md` (decision)
2. `docs/research/USDJPY_VOLATILITY_COMPRESSION_EXPANSION_DIAGNOSTIC_RESULT.md` (analysis)
3. `docs/research/USDJPY_COMPRESSION_EXPANSION_MONETIZATION_DIAGNOSTIC.md` (monetization + London lead)
4. `src/forex_bot/research/volatility_compression_expansion.py` (taxonomy module)
5. `research/usdjpy_vol_compression_expansion/{analysis_summary,monetization_diagnostic}.json`

## 20. Recommended next sprint

`research-usdjpy-london-compression-continuation-confirmation-001` — a read-only,
precommitted, **overfit-hardened** confirmation of the single London-continuation lead:
realistic breakout-stop entry with slippage + explicit intrabar protective stop + measured
London spread + a multiple-testing haircut, on train+validation only, with a precommitted
kill criterion that flips to `PAUSE_STRATEGY_RESEARCH` if it does not clearly clear cost on
both splits. **Not** a campaign, **not** C024, **not** a precommit-design — one narrow
confirmation. If it passes, a *subsequent* sprint may design a precommitted campaign (and
only then is a campaign number discussed). If the operator prefers, `PAUSE_STRATEGY_RESEARCH`
remains a fully defensible alternative given the post-hoc, thin-margin nature of the lead.

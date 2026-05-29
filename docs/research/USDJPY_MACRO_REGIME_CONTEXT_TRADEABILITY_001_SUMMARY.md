# USD_JPY Macro-Regime Context Tradeability 001 — Summary

**Sprint:** `usdjpy-macro-regime-context-tradeability-001`
**Branch:** `research-usdjpy-macro-regime-context-tradeability-001` (branched from the
framing-correction tip `4f04a50`).
**Date:** 2026-05-28
**Outcome:** read-only slow-regime / no-trade-filter diagnostic. **No campaign, no C024,
no C023 execution, no strategy, no verdict change, no approval, TEST sealed,
paper/demo/live blocked, no fast-news/latency trading.**

---

## 1. What this sprint did

Tested — per the corrected framing — whether **slow, lookahead-safe** macro/rates/calendar
**context** classifies USD/JPY **tradeability** over M15 horizons (when not to trade; setup
survival), strictly as a no-trade filter / conditioner, never an entry. Built lookahead-safe
overlay infrastructure (FRED rates/risk regimes via as-of join + a public-schedule event
calendar), ran a tradeability-context diagnostic, robustness + latency-independence checks,
and ended at a readiness decision: **`PAUSE_STRATEGY_RESEARCH`**.

## 2. Commit hashes by phase

| phase | hash | what |
|---|---|---|
| 0 | `27b4408` | branch, audit, baseline, plan |
| 1 | `d1c06c1` | lookahead-safe overlay infra (module + tests + calendar fixture) |
| 2 | `d6b2913` | tradeability-context dataset + analysis + result |
| 3 | `9118160` | robustness + latency-independence |
| 4 | `14bf891` | readiness decision (PAUSE) |
| 5 | (this commit) | final validation + summary |

## 3. Files changed by phase

- **0:** `docs/research/USDJPY_MACRO_REGIME_CONTEXT_TRADEABILITY_001_PLAN.md`
- **1:** `src/forex_bot/research/macro_regime_context.py`,
  `tests/unit/test_macro_regime_context.py`,
  `research/usdjpy_macro_regime_context/event_calendar.json`
- **2:** `scripts/build_usdjpy_macro_regime_context_dataset.py`,
  `scripts/analyze_usdjpy_macro_regime_context.py`,
  `research/usdjpy_macro_regime_context/{context_manifest.json,analysis_summary.json}`,
  `docs/research/USDJPY_MACRO_REGIME_CONTEXT_RESULT.md`, `.gitignore`
- **3:** `docs/research/USDJPY_MACRO_REGIME_CONTEXT_ROBUSTNESS.md`
- **4:** `docs/research/USDJPY_MACRO_REGIME_CONTEXT_READINESS_DECISION.md`
- **5:** this summary

Scope: `docs/research/`, `scripts/`, `research/`, one new `src/forex_bot/research/` module
+ its test, `.gitignore`. **No** broker/executor/order/live/configs changes.

## 4. Data infra built + lookahead-safety proof

- **Module** `macro_regime_context.py`: loads FRED cache (US 2y/10y, VIX, SP500, broad USD)
  into **slow daily regime features** (level-percentile regimes, trend signs, 2s10s,
  composite risk-off); **as-of/lagged join** (default 1-day publication lag) to the M15
  index; **public-schedule event calendar** (NFP computed first-Friday exact + FOMC
  best-effort; CPI/BOJ deferred).
- **Lookahead-safety:** unit-tested as-of join (a bar at `t` sees only values with
  `date + lag ≤ t`); event windows use schedule dates only (outcome never used).
- **Latency-independence:** event-window effects are **identical at a 7-day vs 1-day lag**.

## 5. Dataset coverage & TEST seal

95,756 M15 bars, 2021-06-01..2025-06-29 (train 59,852 / val 35,904). 49 NFP + 33 FOMC
event windows. **TEST 2025-07+ sealed** — builder hard-refuses reads past the lockbox.

## 6. Tradeability-context findings (train AND validation)

- **Raw spread is FLAT (~1.6–1.7 pip median) across every macro/rates/risk/event cell** →
  no macro-based cost filter beyond the existing session/rollover one.
- **Whipsaw ≈ 0.50 in every context** → chop is not conditioned by slow macro regime.
- **spread/ATR varies only mechanically with volatility** (pre-event vol suppressed →
  higher; post-event vol elevated → lower) — direction-blind and time-of-day-redundant.
- **False-breakout conditioning is inconsistent** across splits.
- **Rate-differential regime is NON-IDENTIFIABLE** here: the slow US-rate regime is
  collinear with the 2021–2025 period/split (us_2y high = 52,324 train / 1,927 val; low =
  897 / 19,773), and the JP leg is absent.

## 7. Robustness checks

Lookahead audit clean; latency-independence confirmed (identical at 7-day lag); whipsaw
null; raw-spread null; rate-regime non-identifiable (period confound); risk-regime vol-only;
false-breakout inconsistent; sample sizes adequate (not the binding issue); no-trade-filter
not supported beyond session/rollover; TEST untouched.

## 8. Readiness decision

**`PAUSE_STRATEGY_RESEARCH`.** Method passes the slow/lookahead/latency/not-news/not-speed/
distinct gates (1–5, 8), but fails gates 6 (both-splits actionable signal) and 7 (no-trade
filter / conditioning) — there is no identifiable, actionable tradeability conditioning to
carry into a precommit.

## 9–13. Invariants (verified Phase 5)

| # | check | expected | actual |
|---|---|---|---|
| 9  | C023 executed? | no | **no** |
| 10 | C024 created? | no | **no** |
| 11 | Any verdict changed? | no | **no** (`validate_research_archive` PASS) |
| 12 | Any strategy approved? | no | **no** (`approved: []`) |
| 13 | Paper/demo/live blocked? | yes | **yes** (freeze gate: loops refuse) |

Also: TEST untouched; no broker/executor changes; no OANDA mutation/order calls; no
fast-news/latency logic; no credentials/DBs staged; no huge artifacts (parquet gitignored).

## 14. Tests & validation commands

- `pytest tests/ -q` → **2014 passed, 3 skipped** (2006 prior + 8 new macro-module tests).
- `ruff check src tests scripts research` → **All checks passed.**
- `check_research_freeze.py` / `validate_research_archive.py` → **ALL CHECKS PASSED.**
- `scan_artifacts_for_secrets.py` → **PASSED** (pattern + value scan with `.env` loaded).
- `git status --short` → clean.

## 15. Pre-existing skips/failures

3 skips, all pre-existing data-absence (`test_cost_atlas` H4; 2× `test_compare_entries`
C008 CSVs). No failures.

## 16. Remaining blockers

- No actionable slow-macro tradeability conditioning found → nothing to precommit.
- Rate-differential regime not identifiable without a multi-cycle history + JP rate leg.
- No internal USD/JPY lead survives a hardened test (price-structure families exhausted;
  macro-context lane now also null).
- No strategy approved; nothing paper/demo/live-eligible.

## 17. Exact files to review first

1. `docs/research/USDJPY_MACRO_REGIME_CONTEXT_READINESS_DECISION.md` (verdict)
2. `docs/research/USDJPY_MACRO_REGIME_CONTEXT_RESULT.md` (findings)
3. `docs/research/USDJPY_MACRO_REGIME_CONTEXT_ROBUSTNESS.md` (latency/robustness)
4. `src/forex_bot/research/macro_regime_context.py` + `tests/unit/test_macro_regime_context.py`
5. `research/usdjpy_macro_regime_context/{analysis_summary.json,event_calendar.json}`

## 18. Recommended next sprint

Given `PAUSE_STRATEGY_RESEARCH` (now reaffirmed by both the price-structure and macro-context
lanes), the recommended next step is **not** a strategy or diagnostic lane on existing data.
Options (each separate, later, non-campaign):

- **Hold / freeze** strategy research until a genuinely new, externally-sourced,
  structurally-distinct thesis with a mechanism appears (preferred).
- **Data-acquisition infrastructure only** if pursued: a verified JP rate series + longer
  multi-cycle history (to make rate-regime *identifiable*), or a verified CPI/BOJ calendar
  (low priority — the event effect found here was mechanical/vol-only).

No campaign, no C024, no approval follows from this sprint.

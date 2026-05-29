# Range / volatility-bar feasibility — sprint 001 PLAN

**Branch:** `research-range-volatility-bar-feasibility-001`
**Date:** 2026-05-29
**Type:** diagnostic feasibility study — **NOT a strategy campaign**

---

## 0. Why this sprint exists

CAMPAIGN_029 (`usdjpy_range_bar_mtf_breakout 0.1.0-c029`) was executed and rejected
cleanly: a small **gross** edge on 10-pip USD_JPY range bars that realistic,
M1-resolved cost **fully defeated** (gross +0.0839R/trade, net **−0.0188R**, avg
risk 24.05 pips, avg round-trip cost **2.29 pips ≈ 0.095R/trade**). Parity PASSED,
validation correctly NOT run, test lockbox stayed closed, nothing approved. See
`CAMPAIGN_029_TRAIN_RESULT.md`, `CAMPAIGN_029_GATE_DECISION.md`,
`CAMPAIGN_029_FINAL_INTERPRETATION.md`.

The C029 rejection proves **one specific thesis** (10-pip USD_JPY range-bar
breakout) is cost-defeated. It does **not** prove range bars or volatility bars are
useless across thresholds and pairs. This sprint runs a **diagnostic feasibility
study** to answer:

1. Is the C029 failure mostly the 10-pip threshold being too small / too
   cost-sensitive?
2. At what non-time-bar thresholds does cost stop dominating?
3. Which range/volatility thresholds produce sane trade/bar cadence?
4. Are volatility bars materially different from fixed range bars?
5. Does USD_JPY behave differently from the other six majors?
6. Should the non-time-bar lane stay open, narrow, or retire?

## 1. What this sprint is NOT (hard rules)

- **No strategy is approved.** Nothing is added to `configs/approved_strategies.yaml`.
- **No paper/demo/live** is enabled. No OANDA API calls. No live credentials.
- **No CAMPAIGN_030.** C029 is **not** tuned or revived.
- **No train/validation/test campaign.** No test-lockbox evidence is produced.
- **No trading recommendation.**
- The feasibility study computes **market-microstructure geometry** (bar cadence,
  overshoot, spread → cost). It computes **no strategy signals, no PnL, no labelled
  returns** — so the test lockbox (which seals *strategy returns* on 2025-01-01 →
  2026-05-20) is untouched by construction.
- Only **compact** diagnostics / summaries / docs / tests are committed. Full
  generated bars, M1 dumps, trade ledgers, DB dumps, `.env`, credentials, and bulky
  artifacts stay **local / gitignored**.

## 2. Baseline audit (executed in Phase 0)

| check | result |
|---|---|
| Start point | clean `origin/main` @ `cc553d8`, C029 merged |
| Branch created | `research-range-volatility-bar-feasibility-001` |
| C029 scaffold exists | ✅ `docs/research/CAMPAIGN_029_USDJPY_RANGE_BAR_SCAFFOLD_*` |
| C029 execution result exists | ✅ `CAMPAIGN_029_TRAIN_RESULT.md` + `research/campaign_029/execution/` |
| C029 verdict | ✅ `REJECT_TRAIN_GATE` |
| C029 parity | ✅ `PASS` (independent re-impl reproduced all 2,387 trades exactly) |
| validation / test | ✅ validation NOT run; lockbox NEVER opened |
| `src/forex_bot/data/non_time_bars.py` | ✅ present |
| `src/forex_bot/research/range_bar_execution.py` | ✅ present |
| C029 loader/gates/parity utils | ✅ `src/forex_bot/research/campaign_029_parity.py`, `research/campaign_029/` |
| `scripts/generate_non_time_bar_diagnostics.py` | ✅ present |
| M1 corpus (7 majors) | ✅ EUR/GBP/USD_JPY/AUD/USD_CAD/USD_CHF/NZD, all 2021-05-27 → 2026-05-26 |
| `configs/approved_strategies.yaml` | ✅ `approved: []` (empty) |
| paper/demo/live refusal | ✅ loops refuse — freeze intact |
| `pytest tests/ -q` | ✅ 2296 passed, 3 skipped (local-data skips) |
| `ruff check src scripts tests` | ✅ all checks passed |
| `scripts/check_research_freeze.py` | ✅ ALL CHECKS PASSED |
| `scripts/validate_research_archive.py` | ✅ ALL CHECKS PASSED |
| `scripts/scan_artifacts_for_secrets.py` | ✅ PASSED |

## 3. Phase plan

| phase | deliverable | commit |
|---|---|---|
| 0 | this plan + baseline audit | ✅ |
| 1 | `RANGE_VOLATILITY_BAR_FEASIBILITY_PROTOCOL.md` (diagnostic protocol) | |
| 2 | `src/forex_bot/research/non_time_bar_feasibility.py` + unit tests (pure economics/classification) | |
| 3 | `scripts/analyze_non_time_bar_feasibility.py` + helper tests | |
| 4 | `USDJPY_NON_TIME_BAR_FEASIBILITY_RESULT.md` (USD_JPY focus) | |
| 5 | `SEVEN_PAIR_NON_TIME_BAR_FEASIBILITY_RESULT.md` (all majors) | |
| 6 | `NON_TIME_BAR_LANE_DECISION_AFTER_C029.md` (lane status decision) | |
| 7 | `NEXT_PROMPT_AFTER_NON_TIME_BAR_FEASIBILITY.md` (drafted, not executed) | |
| 8 | final validation + `RANGE_VOLATILITY_BAR_FEASIBILITY_001_SUMMARY.md` | |

## 4. Method (preview — defined fully in Phase 1 protocol)

- **Diagnostic window:** the C029 **train** window `2021-05-27 → 2023-12-31`
  (~2.6 y). This is the same data C029 trained on and is entirely **outside** the
  test lockbox, so no sealed data is touched.
- **Compute:** one M1 DB pass per pair (cache candles locally in-process), then fold
  every threshold via the existing `forex_bot.data.non_time_bars` builders — the bar
  builders are **reused, not duplicated**. Spread → cost is computed from the same
  cached M1 bid/ask.
- **Economics (the new layer):** for each (pair, bar_type, threshold) compute the
  round-trip cost in pips (`full spread + 2× slippage`, matching the C029 cost
  model), the nominal stop risk (`stop_multiple × threshold`), and the ratios that
  decide feasibility:
  - `cost_to_threshold = round_trip_cost / threshold`
  - `cost_to_risk = round_trip_cost / nominal_stop` ( = the minimum gross
    expectancy, per-R, a strategy must clear just to break even on cost)
- **C029 cost floor anchor:** at 10-pip / 24-pip-stop, `cost_to_risk ≈ 0.095`; the
  best gross edge C029 could produce was `+0.084R < 0.095` → cost-defeated. We use
  `~0.08R` as the empirically-observed achievable gross-edge benchmark for this lab.

## 5. Decision labels (defined in Phase 1)

`FEASIBLE_FOR_STRATEGY_RESEARCH`, `FEASIBLE_ONLY_WITH_LARGER_STOPS`,
`COST_DOMINATED`, `TOO_SPARSE`, `TOO_NOISY`, `INCONCLUSIVE`. These are **diagnostic
hypotheses**, not gates, and do not approve anything.

## 6. Artifacts

Committed (compact): the docs in §3, the analyzer module + tests, the script +
helper tests, and compact JSON/CSV/MD summaries under
`research/non_time_bar_feasibility/` (small; full bars stay gitignored).

Local-only / gitignored: full generated bars, M1 caches, any per-bar CSVs.

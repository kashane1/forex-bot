# USD_JPY Volatility-Compression → Range-Expansion Diagnostic 001 — Plan

**Sprint:** `usdjpy-volatility-compression-expansion-diagnostic-001`
**Branch:** `research-usdjpy-volatility-compression-expansion-diagnostic-001`
(branched from the atlas sprint tip `78ab191`, **not** from an older main, because this
sprint depends on the session-atlas docs/tooling just created).
**Date:** 2026-05-28
**Status:** read-only **DIAGNOSTIC**. **NOT** a campaign, **NOT** C024, **NOT** C023
execution, **NOT** a strategy implementation, **NOT** approval, **NOT** paper/demo/live.

---

## 1. Purpose

Phase 4 of the external-thesis/atlas sprint carried forward exactly one candidate —
**intraday volatility-compression → range-expansion on USD_JPY (M15)** — with the
classification `MORE_DIAGNOSTICS_REQUIRED`. The atlas supported the *volatility* leg
(expansion is predictable in timing/state) but was silent on whether the state converts
into a **measurable, cost-surviving** structure, and forward *direction* was an
atlas-level null.

This sprint answers one question, read-only, with predeclared buckets and no tuning:

> **Does an intraday volatility-compression state on USD_JPY lead to measurable,
> cost-surviving range expansion — and if so, is it direction-agnostic or directionally
> tradable — strongly enough on BOTH train and validation to justify a future
> precommit-design sprint?**

It ends at a readiness decision. It does **not** design or run a campaign.

---

## 2. Prior atlas findings (carried in, do not re-derive)

From `USDJPY_SESSION_VOLATILITY_SPREAD_ATLAS.md` /
`EXTERNAL_THESIS_SOURCING_AND_SESSION_ATLAS_001_SUMMARY.md`:

- **Direction is a near-null** across sessions/hours/regimes (continuation ≈ reversion
  ≈ 0.49). Any directional claim starts from zero atlas support.
- **Spread** is ~1.6–1.7 pip in active sessions; **rollover (17:00 ET) is cost-toxic**
  (5–10 pip, spread/ATR ≈ 0.5); off-hours mildly elevated.
- **Volatility timing is predictable**: realized range/ATR peak NY 08:00–11:00 (London
  open → London/NY overlap); range-expansion probability rises monotonically with vol
  regime (low 0.29 → mid 0.50 → high 0.71).
- **False breakouts are frequent** (72–80% of 4h-range breaks fail) but **MFE:MAE < 1**
  after arbitrary entries — fading is not free.
- Adopted overlay: **#9 no-trade cost/spread filter** (never trade rollover; deprioritize
  off-hours) — a constraint, not an edge.

Implication for this diagnostic: design it **direction-agnostic first**; only test
directional monetization if the direction-agnostic expansion structure is real and
cost-surviving.

---

## 3. Non-goals (explicit)

This sprint will **NOT**: create `CAMPAIGN_024`/C024; execute C023; implement a trading
strategy or signal-emitting loop; run a campaign; alter any campaign verdict; rewrite
historical metrics; modify `configs/approved_strategies.yaml` except to verify
`approved: []`; enable/unblock paper/demo/live; modify broker/executor/order/live code;
call OANDA mutation/order APIs or use live credentials; commit `.env`, credentials, DBs,
raw candle dumps, parquet, or large CSVs; present descriptive statistics as tradable
edge; threshold-mine a strategy; touch the sealed TEST window.

---

## 4. Safety rules (operating constraints)

- Phased; commit after each meaningful phase.
- Local materialized M15/H1/H4 USD_JPY data is **read-only** (research Postgres
  `market_data.candles`).
- `.env` symlinks used **only** for research-DB access; credentials never printed.
- **TEST window 2025-07-01+ stays sealed** (train+validation only).
- Compact summaries committed; bulky per-bar outputs gitignored.
- Compression features use **only decision-time data** (no lookahead); expansion uses
  future bars but **as labels only**, never as a live feature.
- Predeclared buckets/quantiles only; **no threshold tuning / no best-cell selection**;
  null results reported honestly.

---

## 5. Compression definitions to test (predeclared)

All computed from data available at the decision bar `i` (bars `<= i` only):

1. **Low rolling M15 realized-range percentile** — trailing range percentile below a
   fixed low cut.
2. **Low ATR percentile** — trailing ATR(14) percentile below a fixed low cut.
3. **Narrow band width** — Bollinger-style (rolling mean ± k·std) width, or rolling
   high–low width, below a fixed low percentile.
4. **Inside-bar / multi-bar compression count** — consecutive bars contained within a
   prior bar's range (NR-style contraction).
5. **Low realized volatility over N bars** — stdev of M15 returns over a fixed window,
   low percentile.
6. **Session-specific compression** — the above, conditioned on pre-London / pre-NY
   windows (where the atlas shows expansion tends to follow).

Quantile cuts are **fixed in advance** (e.g. ≤ p20 = compressed) and a small,
**pre-declared** robustness grid (e.g. p10/p20/p30) is reported — not optimized.

## 6. Expansion definitions to test (labels; may use future bars)

Over fixed horizons (4 / 8 / 16, and 32 M15 bars if justified):

1. **Future high–low range** (direction-agnostic magnitude).
2. **Directional close-to-close move** (signed).
3. **Breakout beyond prior-range high/low.**
4. **Breakout follow-through** (continuation after the break).
5. **MFE/MAE asymmetry after a range break.**
6. **False-breakout / reversal after expansion.**

Each label is explicitly tagged direction-agnostic vs directional.

---

## 7. Session / cost dimensions

Reuse the atlas session classifier (Tokyo / London / NY / London-NY overlap / rollover /
off-hours) and cost context (spread pips, spread/ATR). Every expansion magnitude is
reported **both gross and net** of the atlas-measured session spread (+ a slippage
allowance), with the rollover/off-hours filter applied.

---

## 8. Expected artifacts

| phase | artifact |
|---|---|
| 0 | this plan |
| 1 | `src/forex_bot/research/volatility_compression_expansion.py` + unit tests |
| 2 | `scripts/build_usdjpy_volatility_compression_expansion_dataset.py`, `research/usdjpy_vol_compression_expansion/dataset_manifest.json`, `.../feature_preview.csv` |
| 3 | `scripts/analyze_usdjpy_volatility_compression_expansion.py`, `.../analysis_summary.json`, `docs/research/USDJPY_VOLATILITY_COMPRESSION_EXPANSION_DIAGNOSTIC_RESULT.md` |
| 4 | (if non-null) `scripts/analyze_usdjpy_compression_expansion_monetization.py`, `.../monetization_diagnostic.json`, `docs/research/USDJPY_COMPRESSION_EXPANSION_MONETIZATION_DIAGNOSTIC.md`; else `docs/research/USDJPY_COMPRESSION_EXPANSION_MONETIZATION_NOT_RUN.md` |
| 5 | `docs/research/USDJPY_VOLATILITY_COMPRESSION_EXPANSION_READINESS_DECISION.md` |
| 6 | `docs/research/USDJPY_VOLATILITY_COMPRESSION_EXPANSION_DIAGNOSTIC_001_SUMMARY.md` |

Bulky per-bar dataset gitignored; only compact manifest + preview committed.

---

## 9. Validation commands (Phase 0 baseline + Phase 6 final)

```
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

**Phase 0 baseline (2026-05-28):** pytest **1996 passed, 3 skipped** (pre-existing
data-absence: `test_cost_atlas` H4 store; 2× `test_compare_entries` C008 CSVs); ruff
clean; freeze/archive/secret gates all **PASS**. `approved: []` confirmed; C023 not
executed; C024 absent; paper/demo loops refuse (frozen).

**Data availability (read-only research DB, confirmed prior sprint):** USD_JPY M15
118,035 / H1 28,013 / H4 9,959 / M1 1.84M rows, 2021-05→2026-05, full bid/ask + spread.
Splits: train 2021-06-01..2023-12-31, validation 2024-01-01..2025-06-30, **TEST
2025-07-01+ SEALED**.

---

## 10. Explicit no-C024 / no-C023 / no-approval statement

This sprint creates **no** `CAMPAIGN_024`, executes **no** C023, implements **no**
strategy, runs **no** campaign, changes **no** verdict, approves **no** strategy, touches
**no** sealed TEST data, and leaves paper/demo/live **blocked**.
`configs/approved_strategies.yaml` remains `approved: []`. Output is one read-only
diagnostic module (+ tests) + two read-only analysis scripts + compact summaries + docs,
ending at a readiness decision. Any campaign design is deferred to a future,
separately-precommitted sprint.

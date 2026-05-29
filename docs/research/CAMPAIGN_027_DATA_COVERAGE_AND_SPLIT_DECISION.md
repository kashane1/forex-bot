# CAMPAIGN_027_DATA_COVERAGE_AND_SPLIT_DECISION

**Status:** TRAIN/VALIDATION EXECUTION — Phase 1 / NOT_APPROVED / TEST_LOCKBOX_CLOSED.
Branch `research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`.

Freezes the train and validation windows and the trade-completion policy **before
any execution**, so they cannot be re-chosen after seeing results. The test
window stays sealed.

> Frozen rule: [precommit scope](CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md).
> Plan: [train/validation plan](CAMPAIGN_027_TRAIN_VALIDATION_001_PLAN.md).

---

## Data source

Local read-only SQLite store `data/campaign_002.sqlite3` (worktree-aware
resolution to the primary checkout). Native **H4** candles, `complete = 1` only,
mid OHLC = `(bid + ask) / 2` per component (lab convention). No new fetch, no
broker round-trip, no derived/materialized timeframes.

## Per-pair H4 coverage (full store)

| pair | total H4 bars | first bar (UTC) | last bar (UTC) | train bars (2020–2022) | validation bars (2023–2024) | test bars (sealed) |
|---|---:|---|---|---:|---:|---:|
| EUR_USD | 9,949 | 2020-01-01 | 2026-05-24 | 4,674 | 3,114 | 2,149 |
| GBP_USD | 9,949 | 2020-01-01 | 2026-05-24 | 4,674 | 3,114 | 2,149 |
| USD_JPY | 9,950 | 2020-01-01 | 2026-05-24 | 4,675 | 3,114 | 2,149 |
| AUD_USD | 9,949 | 2020-01-01 | 2026-05-24 | 4,674 | 3,114 | 2,149 |
| USD_CAD | 9,949 | 2020-01-01 | 2026-05-24 | 4,674 | 3,114 | 2,149 |
| USD_CHF | 9,949 | 2020-01-01 | 2026-05-24 | 4,674 | 3,114 | 2,149 |
| NZD_USD | 9,953 | 2020-01-01 | 2026-05-24 | 4,676 | 3,116 | 2,149 |

All seven pairs are uniformly covered. **No pair is excluded** (as expected).

## Warmup requirements

The frozen rule needs, per pair, a causal (backward-looking) warmup of:

- z-score lookback: **20** bars,
- ATR(14): **14** bars,
- ATR-percentile trailing window: **250** bars, then `.shift(1)`,
- 12-bar forward / time-stop horizon at exit.

`compute_decision` requires `len(df) ≥ max(20, 14 + 250) + 2 = 266` bars and a
non-NaN ATR percentile, so the **first valid decision bar is ≈ index 264** in each
pair's series.

### Data limitation — leading warmup is drawn from inside the train window

The store begins **exactly at 2020-01-01**; there are **0 bars before the train
start**. Consequently the first ≈264 H4 bars of 2020 (≈ 44 calendar days, to mid-
February 2020) are consumed as z/ATR/percentile warmup and produce **no signals**.
The train window therefore yields ≈ 4,674 − 264 ≈ **4,410 usable decision bars per
pair**; the ablation/entry sample is much smaller after the |z|≥2.5 + low-vol +
quiet-session funnel. This is a documented limitation, not a blocker — it matches
the front-gate sample regime and does not affect validation (which is fully warmed
by the preceding train history).

Validation (2023–2024) and any future test computation are fully warmed: each
validation decision bar sees ≥ 4,674 preceding train bars for its rolling windows.
Using prior-window closes for a backward-looking rolling mean/σ/percentile is
**causal warmup, not lookahead or split contamination** — the split boundary
governs only which bars are *entered and scored*, by signal timestamp.

## Frozen split windows

```
train:      2020-01-01 → 2022-12-31     (signals entered + scored; single candidate; NO tuning)
validation: 2023-01-01 → 2024-12-31     (confirmation only; G7 — never selection; includes the 2024 recency gate)
test:       2025-01-01 → 2026-05-20     (LOCKBOX — sealed; NOT opened, NOT read this sprint)
```

Chronological, non-overlapping, repo-standard (identical to the precommit and to
C025). A signal is assigned to a split by its **decision (signal-bar) timestamp**.

## Trade-completion policy (frozen here, before execution)

To keep splits self-contained and the **test lockbox strictly sealed**, a signal
is entered **only if its full exit horizon stays within its own split window**:

- entry fills at `next_bar_open` (open of bar `t+1`),
- the protective-stop scan and the 12-bar time stop run over bars `t+1 … t+13`,
- the trade is entered **iff** bar index `t+13` exists **and its timestamp is
  ≤ the split-window end**.

Effect: signals in roughly the **last 13 H4 bars of each window** are dropped
(they cannot complete in-window). This (a) guarantees no validation trade ever
reads a 2025+ test-lockbox bar for its exit, and (b) makes train and validation
fully self-contained — no cross-split price contamination either direction. The
dropped trailing-signal count per pair/window is recorded in
`research/campaign_027/train_validation/blocked_or_warning_conditions.json` at run
time. This is a uniform, pre-registered rule chosen **before** seeing any result,
so it is not a results-driven adjustment.

## Data limitations (summary)

1. No pre-2020 history → ≈264-bar leading warmup truncation inside the train window.
2. Native-H4 only; financing is a conservative **stress overlay**, not a real
   accrual (`forex_bot.financing`), per repo convention.
3. Self-contained-split completion drops ≈13 trailing signals per pair/window.
4. The test window (2025-01-01 → 2026-05-20) is **not read** for any purpose.

## No-approval statement

This document freezes windows and policy only. It runs no evidence, approves
nothing, opens no test lockbox, and keeps `configs/approved_strategies.yaml` =
`approved: []` with paper/demo/live blocked.
</content>

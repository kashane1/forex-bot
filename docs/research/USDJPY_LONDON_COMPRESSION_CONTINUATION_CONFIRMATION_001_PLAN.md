# USD_JPY London Compression-Continuation Confirmation 001 — Plan

**Sprint:** `usdjpy-london-compression-continuation-confirmation-001`
**Branch:** `research-usdjpy-london-compression-continuation-confirmation-001` (branched
from the compression/expansion diagnostic tip `cd8e27c`, **not** an older main — depends
on the atlas + compression/expansion tooling just built).
**Date:** 2026-05-28
**Status:** read-only **CONFIRMATION DIAGNOSTIC**. **NOT** a campaign, **NOT** C024,
**NOT** C023 execution, **NOT** strategy implementation, **NOT** approval, **NOT**
paper/demo/live.

---

## 1. Purpose

The prior sprint's monetization diagnostic surfaced exactly one positive lead amid an
otherwise-falsified compression→expansion thesis: **post-compression London-session
breakout continuation**, positive on both train and validation at h16 and h32 under
*optimistic* assumptions. This sprint subjects that single lead to a **strict,
overfit-hardened confirmation**: realistic spread + slippage cost variants, an **intrabar
protective stop** (absent in the prior sim), and a **multiple-testing haircut** (the lead
was 1 of 12 session×horizon cells). The goal is a clean go/no-go on whether the lead is
strong enough to justify a *future* precommit-design sprint — or whether it dissolves
under realism and should trigger `PAUSE_STRATEGY_RESEARCH`.

No threshold is tuned. No new session/horizon/filter is searched. The lead is *locked*
in Phase 1 before any new simulation.

---

## 2. Prior lead summary (carried in)

From `USDJPY_COMPRESSION_EXPANSION_MONETIZATION_DIAGNOSTIC.md`:

- Cell: London session, compressed state (≥3 of 4 percentile features {range, ATR,
  bandwidth, realized-vol} ≤ 0.20), first prior-range-break **continuation**, exit at
  fixed horizon close.
- Optimistic-cost (4.4-pip round-trip), **no intrabar stop**, level-fill results:
  - h16: train **+1.04** (n=815), validation **+3.04** (n=692)
  - h32: train **+2.21** (n=846), validation **+6.12** (n=712), win rate ~0.54
- The only session positive on all four train/val × horizon cells. Every other session
  was negative or sign-flipped.
- **Caveats:** post-hoc (1 of 12 cells), optimistic cost, level-fill (no slippage), no
  intrabar protective stop, no multiple-testing correction. **Not edge.**

---

## 3. Hard non-goals

Create **no** `CAMPAIGN_024`; execute **no** C023; implement **no** strategy; run **no**
campaign; alter **no** verdict; rewrite **no** metrics; modify `approved_strategies.yaml`
only to verify `approved: []`; enable **no** paper/demo/live; modify **no**
broker/executor/order/live code; call **no** OANDA mutation/order APIs; use **no** live
credentials; commit **no** `.env`/credentials/DBs/raw-candle-dumps/parquet/huge-CSVs;
present **nothing** as tradable edge; **no** threshold-mining; keep **TEST sealed**.

---

## 4. Safety rules

- Phased; commit after each meaningful phase.
- USD_JPY M15 read **read-only** from research Postgres `market_data.candles`.
- `.env` used only for research-DB access; credentials never printed.
- **TEST window 2025-07-01+ stays sealed** (train+validation only).
- Compact summaries committed; bulky outputs gitignored.

---

## 5. Confirmation criteria (predeclared; full kill criteria locked in Phase 1)

The lead is confirmed **only if all** hold:

1. train **and** validation net expectancy > 0 after **base** cost;
2. **conservative** cost does not flip either split negative;
3. the **intrabar protective stop** model does not destroy the effect;
4. sample size adequate (not a tiny-n artifact);
5. year/half-split robustness acceptable (not one lucky period);
6. effect not dominated by a few outlier trades;
7. **TEST** not touched;
8. structurally distinct from C022/C023/microstructure family;
9. survives the **multiple-testing haircut** (1 of 12 cells from the prior search).

Any failure → not ready (and, if the lead clearly fails, `PAUSE_STRATEGY_RESEARCH`).

---

## 6. Overfit risks being controlled

- **Post-hoc selection / multiple comparisons:** Bonferroni-style haircut over the 12
  prior cells (6 sessions × 2 horizons).
- **Optimistic cost:** three cost variants (optimistic / base / conservative).
- **Unrealistic fills:** intrabar protective stop so trades can lose before the horizon.
- **Outlier dependence:** trimmed-mean / drop-top-k and per-year breakdowns.
- **Tiny-sample fragility:** report n per split/year and require adequacy.

---

## 7. Realistic cost assumptions (predeclared, round-trip pips)

Using the atlas-measured London spread (M15 median 1.7, p90 1.9; M1 confirms):

| variant | round-trip cost | rationale |
|---|---|---|
| optimistic | **2.2** | ~1 spread + 0.5 slippage (best-case fills) |
| base | **4.4** | 2 × median spread (1.7) + 1.0 slippage |
| conservative | **5.8** | 2 × p90 spread (1.9) + 2.0 slippage |

(The prior sprint's "+2.2/+6.1" was at the 4.4 = **base** level, before any stop.)

## 8. Intrabar protective-stop assumptions (predeclared, diagnostic only)

Entry at the broken prior-range level on the break bar; thereafter, scan the M15 path to
the horizon. If the adverse extreme breaches the stop, the trade exits at the stop
(loss = stop distance + cost); otherwise it exits at the horizon close.

| stop variant | distance |
|---|---|
| none | hold to horizon (matches prior sim) |
| 1.0× | 1.0 × the compressed decision-bar range |
| 1.5× | 1.5 × the compressed decision-bar range |
| ATR | 1.0 × decision-bar ATR(14) |

No stop distance is optimized; these are fixed diagnostic settings.

---

## 9. Validation commands (Phase 0 baseline + Phase 5 final)

```
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

**Phase 0 baseline (2026-05-28):** pytest **2006 passed, 3 skipped** (pre-existing
data-absence: `test_cost_atlas` H4 store; 2× `test_compare_entries` C008 CSVs); ruff
clean; freeze/archive/secret gates **PASS**. `approved: []`; C023 not executed; C024
absent; paper/demo loops refuse.

**Data:** USD_JPY M15 read-only, full bid/ask + spread, train 2021-06-01..2023-12-31,
validation 2024-01-01..2025-06-30, **TEST 2025-07+ sealed**.

---

## 10. Explicit no-C024 / no-C023 / no-approval statement

This sprint creates **no** `CAMPAIGN_024`, executes **no** C023, implements **no**
strategy, runs **no** campaign, changes **no** verdict, approves **no** strategy, touches
**no** sealed TEST data, leaves paper/demo/live **blocked**, and keeps
`configs/approved_strategies.yaml` = `approved: []`. Output is one read-only confirmation
script + compact summaries + docs, ending at a readiness decision. If the lead fails
confirmation, the verdict is `PAUSE_STRATEGY_RESEARCH`. Any campaign design is deferred to
a future, separately-precommitted sprint.

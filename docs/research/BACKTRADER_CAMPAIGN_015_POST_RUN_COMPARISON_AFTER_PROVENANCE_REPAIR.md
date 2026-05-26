# Backtrader vs Bespoke Comparison — CAMPAIGN_015 (After Provenance Repair, Phase 4)

**Sprint:** [BT C015 Provenance Repair 001](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_PLAN.md)
**Branch:** `infra-backtrader-campaign-015-provenance-repair-001`
**Date:** 2026-05-26
**Divergence classification (this sprint):** **`TIMESTAMP_MISMATCH`**
(primary, evidence-based). The compare-harness's own auto-label is
`SIGNAL_RULE_MISMATCH`, which is the appropriate auto-label *given
its inputs* but is **superseded** by the timestamp-window analysis
below.

> Diagnostic-only document. Does NOT approve any strategy.
> The Backtrader lane is a **secondary verification lane**; it cannot
> approve any strategy under any verdict.
> `configs/approved_strategies.yaml` remains `approved: []`.

This document is an **addition** to the prior
[`BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md)
(which recorded a `DATA_MISMATCH` → `BLOCKED` outcome before the
provenance repair). The prior doc is **not** rewritten.

---

## 1 · What ran

- **BT lane (this sprint):**
  `python scripts/run_backtrader_parity.py --campaign CAMPAIGN_015
  --output research/campaign_015/diagnostics/backtrader_lane`
  ran cleanly to completion against the now-loadable
  `research/lean_parity/exports/campaign_002_h4/*.csv`. 7 instruments,
  9,933–9,937 candles each.
- **Bespoke reference:** built by
  `scripts/build_campaign_015_bespoke_reference.py` from the existing
  rehydrate artifact at
  `research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json`.
- **Compare:** `scripts/compare_backtrader_parity.py` against both.

Machine-readable outputs:
- [`research/campaign_015/diagnostics/backtrader_lane/backtrader_summary.json`](../../research/campaign_015/diagnostics/backtrader_lane/backtrader_summary.json)
- [`research/campaign_015/diagnostics/backtrader_lane/backtrader_metrics.json`](../../research/campaign_015/diagnostics/backtrader_lane/backtrader_metrics.json)
- [`research/campaign_015/diagnostics/backtrader_lane/backtrader_trades.jsonl`](../../research/campaign_015/diagnostics/backtrader_lane/backtrader_trades.jsonl)
- [`research/campaign_015/diagnostics/backtrader_lane/run_manifest.json`](../../research/campaign_015/diagnostics/backtrader_lane/run_manifest.json)
- [`research/campaign_015/diagnostics/backtrader_lane/run_log_summary.md`](../../research/campaign_015/diagnostics/backtrader_lane/run_log_summary.md)
- [`research/campaign_015/diagnostics/backtrader_lane/comparison_summary.json`](../../research/campaign_015/diagnostics/backtrader_lane/comparison_summary.json)
- [`research/campaign_015/diagnostics/backtrader_lane/comparison_summary.md`](../../research/campaign_015/diagnostics/backtrader_lane/comparison_summary.md)
- [`research/campaign_015/diagnostics/campaign_015_bespoke_reference.json`](../../research/campaign_015/diagnostics/campaign_015_bespoke_reference.json)

---

## 2 · Headline numbers

| dimension | Backtrader | Bespoke (rehydrate) | delta |
|---|---|---|---|
| total trades (all 7 pairs) | **575** | **164** | **+411 (+250.6%)** |
| total PnL (account ccy, BT only) | -51.43 | (n/a — bespoke uses R units) | — |
| candles iterated per pair | 9,933–9,937 | per-fold (~test-window subset) | — |
| run windows | **whole 2020-01..2026-05 universe** | **8 rolling 180-day test windows** | window-coverage gap |

Per-pair trade count delta (auto-compare):

| instrument | BT trades | bespoke trades | Δ% |
|---|---:|---:|---:|
| AUD_USD | 99 | 24 | +312.5% |
| EUR_USD | 82 | 27 | +203.7% |
| GBP_USD | 97 | 41 | +136.6% |
| NZD_USD | 69 | 5 | +1,280.0% |
| USD_CAD | 85 | 23 | +269.6% |
| USD_CHF | 79 | 27 | +192.6% |
| USD_JPY | 64 | 17 | +276.5% |

Win rates (signal-quality sanity check, where BT does report):

| instrument | BT win rate | bespoke win rate |
|---|---|---|
| AUD_USD | 0.303 | 0.375 |
| EUR_USD | 0.317 | 0.333 |
| GBP_USD | 0.340 | 0.415 |
| NZD_USD | 0.319 | 0.200 |
| USD_CAD | 0.259 | 0.348 |
| USD_CHF | 0.317 | 0.519 |
| USD_JPY | 0.375 | 0.529 |

---

## 3 · Why this is `TIMESTAMP_MISMATCH`, not `SIGNAL_RULE_MISMATCH`

The compare harness's auto-label is `SIGNAL_RULE_MISMATCH` because
the trade-count delta exceeds its 10% tight band on every instrument.
That label is correct *given the inputs the harness sees*. It is
**wrong** for the underlying engines, because the two engines are
running on *different time windows*:

- **Bespoke:** walks-forward through 8 rolling test windows
  (`540/180/180/180`-day train/validation/test/step), each fold
  re-warming for 540 days before counting any trade in the
  180-day test slice. Total *test* coverage ≈ 8 × 180 = 1,440 days
  ≈ 3.95 years.
- **BT lane:** iterates the entire CSV (≈ 9,933 candles ≈ 6.4 years
  from `2020-01-01` to `2026-05-19`) after a single warmup at the
  start, then trades continuously.

The window-coverage ratio alone is ≈ 6.4 / 3.95 ≈ **1.6×**, which
already accounts for a meaningful fraction of the observed
**3.5×** trade-count gap. The remaining ratio (~2.2×) is the
genuinely-uncertain part — it could be:

- additional firing during what would have been bespoke's per-fold
  540-day re-warmup windows (BT only warms up once);
- a real off-by-one / signal-rule difference in the BT adapter;
- a difference in how each engine handles the post-rejection cool-down
  (the bespoke `RiskEngine` rejects some signals, BT does not have
  the same risk engine in the loop).

Without a windowed BT run (BT executed on the same 8 test windows
the bespoke uses, or bespoke executed full-window with the same
single warmup), we **cannot** tell whether the per-bar firing rate
differs at all. So the binding classification for *this* sprint is
`TIMESTAMP_MISMATCH`: the engines disagree about which bars they
are processing. A future infra sprint can isolate any residual
`SIGNAL_RULE_MISMATCH` by aligning the windows.

The compare harness's `SIGNAL_RULE_MISMATCH` auto-label is recorded
faithfully in `comparison_summary.{json,md}`; this doc is the human
interpretation layer on top of it.

---

## 4 · Approximation flags re-published (from BT run log)

The BT lane already documents seven approximation flags that apply
regardless of window alignment:

- `FILL_TIMING_APPROXIMATION` — BT queues entry on signal bar and
  fills at next bar open via `_pending_side` + `_execute_pending_entry`;
  minor microstructure drift vs bespoke `next_bar_open` is expected.
- `RANGE_PRIOR_BARS_ONLY` — prior-high / prior-low read excludes
  current bar in both engines.
- `ADX_AND_ATR_CURRENT_BAR` — current-bar ADX(14) and ATR(14) in
  both engines.
- `ADVERSE_STOP_WINS` — same-bar adverse-stop wins on entry bar; both
  engines.
- `NO_TRAILING_STOP` — no trailing stop; only hard stop + 12-bar time
  stop in both engines.
- `BACKTRADER_BROKER_BYPASSED` — BT uses a manual one-position state
  machine, not Cerebro's broker, so the strategy fills are computed
  identically to the bespoke (modulo timing).
- `MANUAL_SIZING_RISK_FRACTION` — 0.25% NAV in both engines.
- `NO_FINANCING` — pre-financing in both engines.

None of these flags individually explain a 3.5× trade-count gap.

---

## 5 · No bespoke tuning to force parity

The bespoke engine was NOT modified to make BT match it. The BT
adapter was NOT modified to make it match bespoke. The
`config_hash` in
[`research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json`](../../research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json)
is unchanged from the prior sprint:
`17ddfd7eb87d93c502f148642c8ee883c66cb72bfa8ca72f981624a0dcfdd93c`.

---

## 6 · Verbatim binding divergence-label set

- `PASS`
- `TOLERABLE_DRIFT`
- `DATA_MISMATCH` (prior sprint's label, now resolved)
- **`TIMESTAMP_MISMATCH`** ← **this sprint's primary label**
- `SIGNAL_RULE_MISMATCH` (compare-harness's auto-label, secondary)
- `FILL_TIMING_MISMATCH`
- `STOP_OR_TIME_EXIT_MISMATCH`
- `SIZING_OR_PNL_MISMATCH`
- `BLOCKED`

---

## 7 · What this means for CAMPAIGN_015

- **Approval impact:** *none.* CAMPAIGN_015 is still REJECT on the
  bespoke gates. `configs/approved_strategies.yaml` remains
  `approved: []`. Paper / demo / live remain blocked. The strongest
  possible verdict for the BT lane is "BT broadly reproduces
  bespoke" — and that is not yet established.
- **Diagnostic impact:** the strategy *implementation* in BT is
  recognisably the same family (similar win-rate band on most pairs;
  same exit reasons; no take-profit) but the window coverage is
  too different to call PASS or TOLERABLE_DRIFT. A future infra
  sprint that aligns windows is the necessary next step before any
  CAMPAIGN_015-derived candidate work.

---

## 8 · Reproduction

```bash
# (Phase 2 lock-step + Phase 3 preflight assumed PASS.)

# BT lane
python scripts/run_backtrader_parity.py \
  --campaign CAMPAIGN_015 \
  --output   research/campaign_015/diagnostics/backtrader_lane

# Build a per-pair bespoke reference from the rehydrate detail
python scripts/build_campaign_015_bespoke_reference.py \
  --fold-detail research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json \
  --out         research/campaign_015/diagnostics/campaign_015_bespoke_reference.json

# Compare
python scripts/compare_backtrader_parity.py \
  --campaign CAMPAIGN_015 \
  --backtrader-results research/campaign_015/diagnostics/backtrader_lane \
  --bespoke-reference  research/campaign_015/diagnostics/campaign_015_bespoke_reference.json \
  --output             research/campaign_015/diagnostics/backtrader_lane
```

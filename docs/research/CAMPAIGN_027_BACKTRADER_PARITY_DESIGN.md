# CAMPAIGN_027_BACKTRADER_PARITY_DESIGN

**Status:** SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED. Phase 6 of
`research-campaign-027-h4-filtered-zscore-reversion-scaffold-001`. **Design only**
— no Backtrader code is implemented in this scaffold sprint; this document
specifies how parity *will* be built and verified in a future sprint, before any
promotion review.

> Frozen rule: [precommit scope](CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md).
> Gate: G8 (`FUTURE_CAMPAIGN_REENTRY_GATES.md`) — no test lockbox, no promotion
> without parity at the approval-bound fill timing.

---

## Why parity is required before promotion review

The campaign's own research engine (the strategy module + the future
train/validation runner) computes expectancy on the local H4 store. Before any
strategy can be promotion-reviewed, that result must be **independently
reproduced in Backtrader** to a stated tolerance. Parity catches silent
engine-specific bugs (off-by-one fills, warmup misalignment, look-ahead leaks,
cost-application differences) that would otherwise inflate a wafer-thin edge.
Because the CAMPAIGN_027 edge is **inside the cost-assumption band**, an
engine discrepancy of even a fraction of a pip per trade could flip the verdict —
so parity is non-negotiable here (it is kill condition #8). Parity is required
**before** the test lockbox is opened, never after.

## How the H4 signal/entry/exit maps to Backtrader

| element | research engine | Backtrader representation |
|---|---|---|
| data | H4 mid OHLC from `data/campaign_002.sqlite3` | `bt.feeds.PandasData` on the **same** deduped mid frame (one feed per pair) |
| decision bar | last completed H4 bar `t` | `next()` on bar `t` (Backtrader's current bar is the last completed bar) |
| z-score | 20-bar mean/σ of close, **shifted 1**, σ ddof=1 | a custom indicator computing `(close[0] - mean(close, 20)[-1]) / std(close, 20)[-1]`; ddof=1 must be matched explicitly |
| ATR (low-vol) | 14-bar **simple mean** of TR | a TR SMA(14) indicator — **not** `bt.ind.ATR` (Wilder); must be the simple mean |
| ATR percentile | trailing-250 rank, shifted 1 | rolling rank over the last 250 ATR values, evaluated at `[-1]` (prior bar) |
| session | UTC-hour bucket of bar `t` | bucket from `self.data.datetime.datetime(0)` converted to UTC |
| entry | short when `z≥+2.5 & low_vol & quiet` | `self.sell(...)` submitted on bar `t`, **filled at bar `t+1` open** (`cheat_on_open=False`) → matches `next_bar_open` |
| protective stop | `entry + 3×ATR14` | a stop order at the precomputed level (server-side-style) |
| time stop | exit at 12 H4 bars | close the position when `len(self) - entry_bar == 12`, filled at the next bar open (consistent with entry) |
| cost | optimistic + conservative (spread+slip+financing) | `bt.CommInfo` / per-trade spread+slip; financing applied as a per-bar carry charge over the hold; **both** cost modes reproduced |

## How z-score and filters must be calculated (parity-critical)

- **z-score:** match the research engine *exactly*: rolling mean and std over 20
  closes, **both `.shift(1)`**, std with **`ddof=1`** (pandas default). A naive
  `bt` z-score using the current bar in the window, or population σ (`ddof=0`),
  will **not** reconcile.
- **ATR:** **simple 14-bar mean of true range**, not Wilder smoothing. TR uses
  the prior *mid* close.
- **ATR percentile:** the trailing 250-window rank, evaluated on the **prior**
  bar (`.shift(1)`), threshold `≤ 0.33`.
- **session bucket:** identical UTC-hour boundaries (asia[0,7), london[7,12)).
- **warmup:** discard the first ~270 bars per pair (max of z-window and
  ATR-window+percentile-window) — Backtrader's `minperiod` must equal the
  research warmup, or early bars will diverge.

## How the cost model must be represented

- **Optimistic:** realized per-bar spread (from the bid/ask frame) + 2×0.2-pip
  slip on entry and exit.
- **Conservative (binding):** flat 1.5-pip spread + 2×0.2-pip slip +
  worst-case financing over the 12-bar (≈48h) hold
  (`research.edge_discovery.costs.financing_stress_fraction` semantics). Both
  modes must be reproduced; parity is checked on the **conservative** figure.

## How the fixed-horizon / time exit must be represented

The primary exit is a **time stop at 12 H4 bars** filled at the next bar open.
In Backtrader, track the entry bar index and close at `entry_bar + 12`; the fill
is the open of `entry_bar + 13` (consistent with the `next_bar_open` entry
convention). The protective ATR stop may pre-empt the time stop intrabar (the
**adverse stop wins a same-bar tie**). No take-profit, no trailing.

## Expected parity tolerance

- **Per-trade entry/exit price:** exact (same bar, same open) — any mismatch is a
  bug, not tolerance.
- **Trade count:** identical (same triggers, same filters, same warmup).
- **Aggregate expectancy (post-conservative-cost):** within **±0.00002**
  (≈0.2 bp) per trade, or ≤ 2% relative on the aggregate — whichever is tighter.
  Because the edge is wafer-thin, a looser tolerance is not acceptable; a
  discrepancy above tolerance is kill condition #8 (parity fail → no promotion).

## Known parity risks

- **z-score warmup / shift:** the one-bar shift and `ddof=1` are the most likely
  reconciliation failures.
- **session labeling:** DST / local-time vs UTC mistakes shift bars between
  quiet/loud buckets and change the trade set.
- **low-vol regime calculation:** simple-mean ATR vs Wilder ATR, and the
  trailing-250 percentile shift, must match exactly.
- **financing / cost overlay:** applying financing per-bar vs once-per-trade, and
  optimistic vs conservative spread, are easy to diverge.
- **fill timing:** `next_bar_open` must be honoured on **both** entry and exit;
  Backtrader's `cheat_on_open` must be off.
- **same-bar stop/exit ambiguity:** if the protective stop and the time stop
  could both trigger on the same bar, the **adverse stop wins** — both engines
  must encode the identical tie-break.

## Scope statement

This document is **design only**. No Backtrader strategy, cerebro harness, or
parity-comparison code is written in this scaffold sprint (it is not trivial and
not safe to fold into a precommit). A future sprint implements it against the
existing repo parity tooling (`tests/research/test_parity_verifier_*`) and must
reach the tolerance above before the test lockbox is considered.

# Backtrader CAMPAIGN_011 — Phase 6 per-fold comparison deferred

**Date:** 2026-05-25
**Branch:** `infra-backtrader-secondary-lane-004-campaign-011`
**Phase:** 6 of `BACKTRADER_CAMPAIGN_011_004_PLAN.md`
**`strategy_evidence: false`**

> The **full-window** Backtrader-vs-bespoke comparison is PASS at
> trade-for-trade precision (Phase 5: 2 800 / 2 800; 100 % match by
> `(entry_time, side)`). A clean **per-fold** comparison requires
> Backtrader-side runner infrastructure that this sprint deliberately
> does not build. The informational per-fold rollup is therefore
> deferred to a future BT-lane sprint, with the design constraints
> below pinned. CAMPAIGN_011 remains REJECT / null diagnostic anchor
> by design.

## 1. Why per-fold cannot be done by post-hoc slicing

The bespoke per-fold rollup at
`research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json`
was produced by **running the bespoke engine 8 × 7 = 56 times**, once
per (fold, pair), each time loading **only** that fold's test-window
candles from the SQLite store (`scripts/export_campaign_011_norisk_reference.py`
§main per-fold loop). Each per-fold run has its **own** 32-bar
warmup at the start of the fold and its **own** independent
`_in_position=False` initial state.

A post-hoc slice of the full-window BT trade JSONL by the fold plan's
test-window dates does **not** reproduce this: the full-window BT run
is warm by 2020-12-31 and has potentially-open positions straddling
fold boundaries. The post-hoc slice therefore over-counts fold-start
trades that the bespoke per-fold run skips (warmup) and may miss
fold-end trades that the bespoke per-fold run closes inside the fold
window (the full-window run would close them as time-stop in the
*next* fold window).

This is the **expected** divergence — `CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md`
§5 explicitly says:

> Per-fold trade counts are **not** required to sum exactly to the
> full-window total — strategy state (e.g. an open position
> straddling a fold boundary, R2 re-entry blocking on bar at start
> of a fold) makes a small Δ legitimate. The full-window number is
> the canonical one.

## 2. Post-hoc-slice numbers (for reference, not for verdict)

| fold | window | bespoke trades (per-fold) | BT trades (full-window sliced) | Δ |
|---|---|---|---|---|
| 0 | 2021-12-21..2022-06-18 | 214 | 225 | +11 |
| 1 | 2022-06-19..2022-12-15 | 230 | 239 | +9 |
| 2 | 2022-12-16..2023-06-13 | 206 | 217 | +11 |
| 3 | 2023-06-14..2023-12-10 | 192 | 205 | +13 |
| 4 | 2023-12-11..2024-06-07 | 216 | 227 | +11 |
| 5 | 2024-06-08..2024-12-04 | 211 | 216 | +5 |
| 6 | 2024-12-05..2025-06-02 | 188 | 199 | +11 |
| 7 | 2025-06-03..2025-11-29 | 204 | 214 | +10 |
| **sum** | — | **1 661** | **1 742** | **+81** |

The Δ is the post-hoc-slicing artefact described in §1. It is **not**
a BT-lane bug; it is the difference between two legitimate sampling
methods.

## 3. What a real per-fold comparison would need

To do an apples-to-apples per-fold comparison, the Backtrader-lane
runner needs to load **only** the fold's test-window candles per
(fold, pair) — same shape as
`scripts/export_campaign_011_norisk_reference.py`'s per-fold pass.
Specifically:

| component | change required |
|---|---|
| `research/backtrader_lane/data_adapter.py` | accept optional `from_dt` + `to_dt` and slice the CSV rows before passing to PandasData; the sha256 check stays on the FULL CSV (provenance is the full file) — only the in-memory frame is sliced |
| `research/backtrader_lane/runner.py` (`RunOptions`, `run`) | accept a list of fold-window plans; emit one `backtrader_summary.json` + `backtrader_trades.jsonl` per (fold, pair); aggregate into a per-fold rollup |
| `scripts/run_backtrader_parity.py` | new `--fold-plan <path>` flag (defaults to the committed CAMPAIGN_011 plan when set) |
| `scripts/compare_backtrader_parity.py` | optional `--per-fold` mode comparing the BT per-fold rollup against `campaign_011_h4_bespoke_reference_per_fold.json` |

Estimate: ~150-250 lines of new code + ~10-15 tests. This is a
meaningful BT-lane feature, **not** a CAMPAIGN_011 fix.

## 4. Decision: defer

The full-window comparison is PASS at trade-for-trade precision —
the **canonical** comparison target per the contract and handoff
doc. Per-fold is **informational** and can be re-derived from the
bespoke side at any time by re-running the existing exporter. Adding
per-fold infrastructure to the BT lane is a feature decision for a
future sprint, not a bug fix for CAMPAIGN_011.

Per the sprint-004 plan §6: *"Do not let per-fold work delay
completing the full-window result."* The full-window result is
complete and committed (Phase 5). This phase concludes by deferring.

## 5. Recommended next branch (if a future sprint wants per-fold)

```
infra-backtrader-secondary-lane-005-fold-plan-support
```

Suggested scope (the next sprint can refine):
- Phase 0: baseline + plan
- Phase 1: extend `data_adapter.py` with optional `from_dt`/`to_dt`
  (preserve sha256-of-full-CSV check; only slice the in-memory frame)
- Phase 2: extend `runner.py` + `run_backtrader_parity.py` with
  `--fold-plan` support
- Phase 3: extend `compare.py` + `compare_backtrader_parity.py` with
  per-fold rollup comparison
- Phase 4: run + compare CAMPAIGN_011 per-fold against the bespoke
  `campaign_011_h4_bespoke_reference_per_fold.json`
- Phase 5: sprint summary

This sprint's full-window CAMPAIGN_011 PASS stays valid regardless
of whether per-fold is later run.

## 6. Required disclosure

CAMPAIGN_011 remains **REJECT / null diagnostic anchor by design**.
This deferral does not approve any strategy, tune any parameter,
change any CAMPAIGN_011 rule, change the bespoke engine, or change
the no-RiskEngine bespoke reference JSONs.

`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked. `strategy_evidence: false`.

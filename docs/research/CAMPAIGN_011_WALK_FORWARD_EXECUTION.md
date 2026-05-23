# CAMPAIGN_011 — Walk-Forward Execution

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-walk-forward-001`
`strategy_evidence: false`

Phase 4 per-fold execution record for the CAMPAIGN_011 research
candidate (`random_entry_anchor 0.1.0-c011` — the C5
diagnostic-anchor null model). **This document does not approve
the strategy. CAMPAIGN_011 is a null model — cannot be approved
by design.** It records the commands, data path, frozen-parameter
+ master-seed enforcement, fold-by-fold execution outcomes, and
exact artifact paths.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_011 cannot be approved by design.**
> The verdict classification lives in
> [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
> (Phase 5).

## 1. Commands

```bash
# Phase 2 plan (already generated; re-listed for repeatability):
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_011 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/

# Phase 4 per-fold execution:
.venv/bin/python scripts/run_campaign_011.py \
    --config configs/campaign_011_random_entry_anchor.yaml \
    --plan backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json \
    --out backtests/CAMPAIGN_011_random_entry_anchor/
```

Runtime: **5.6 seconds** end-to-end on the 8 folds × 7 pairs = 56
backtests, single-machine local execution. No broker call, no
credential read. (Random-entry's per-bar gate rate of 0.05
produces ~30 % fewer trades than CAMPAIGN_010's session-breakout,
which explains the slightly faster runtime.)

## 2. Data and provenance (re-confirmed at runtime)

- `data/campaign_002.sqlite3` (gitignored symlink — see
  [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md))
- per-pair source = `oanda-practice` (asserted at runtime;
  mismatch aborts the runner)
- per-pair H4 candles read with `completed_only=True`
- 7-pair universe matched exactly against the design

## 3. Frozen-parameter + master-seed enforcement (binding)

The runner aborts before any backtest if the loaded YAML's
`strategy.random_entry_anchor` deviates from the pre-commit. The
asserted-frozen set, verbatim from
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§5:

| parameter | value |
|---|---|
| `version` | `0.1.0-c011` |
| `timeframe` | `H4` |
| `master_seed` | `20260523` (belt-and-suspenders re-check inside the runner; any other value aborts) |
| `entry_probability_per_bar` | `0.05` |
| `atr_lookback` | `14` |
| `atr_stop_multiple` | `2.0` |
| `trailing_stop_atr_multiple` | `None` |
| `max_bars_in_trade` | `6` |
| `min_atr_pips` | `{}` |

All values matched. The runner also asserted
`parameter_mode == "frozen"`, `split_style == "rolling"`, and
`strategy_evidence == False` on the loaded plan.

## 4. Per-fold execution table (test windows only)

| fold | test_start | test_end | total trades | aggregate return % | expectancy R | profit factor | pairs +ve | single-pair dom % |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 0 | 2021-12-21 | 2022-06-18 | 143 | −4.79 | −0.1039 | 0.19 | 1/7 | 21.2 |
| 1 | 2022-06-19 | 2022-12-15 | 150 | −0.48 | −0.0209 | 0.85 | 4/7 | 38.3 |
| 2 | 2022-12-16 | 2023-06-13 | 153 | +4.23 | +0.0387 | 3.84 | 6/7 | 35.2 |
| 3 | 2023-06-14 | 2023-12-10 | 150 | −0.83 | −0.0056 | 0.61 | 2/7 | 26.4 |
| 4 | 2023-12-11 | 2024-06-07 | 162 | −0.08 | +0.0147 | 0.97 | 3/7 | 23.5 |
| 5 | 2024-06-08 | 2024-12-04 | 153 | +0.54 | −0.0014 | 1.21 | 4/7 | 36.4 |
| 6 | 2024-12-05 | 2025-06-02 | 128 | +0.94 | +0.0541 | 1.38 | 3/7 | 27.9 |
| 7 | 2025-06-03 | 2025-11-29 | 138 | −0.06 | +0.0068 | 0.96 | 3/7 | 22.2 |
| **total** | | | **1,177** | **−0.53** | **−0.0024** | **0.91** | | |

The per-fold expectancy R values bounce around zero
(min −0.104, max +0.054); the aggregate is **−0.0024 R** —
indistinguishable from the no-edge null-model expectation under
spread + ATR-stop costs.

## 5. Per-pair × all-folds aggregate (informational)

| pair | trades | aggregate return % | expectancy R |
|---|---:|---:|---:|
| EUR_USD | 119 | −1.22 | −0.0403 |
| GBP_USD | 196 | +4.19 | **+0.0842** |
| USD_JPY | 174 | +0.35 | +0.0000 |
| AUD_USD | 190 | −1.73 | −0.0359 |
| USD_CAD | 182 | −0.44 | −0.0099 |
| USD_CHF | 177 | +0.92 | +0.0243 |
| NZD_USD | 139 | −2.61 | −0.0737 |

3 / 7 pairs net positive (GBP_USD, USD_JPY ≈ 0, USD_CHF). Per-pair
expectancies bounded in approximately ±0.10 R, centered near 0
— exactly the shape expected from a random null model.

**USD_JPY expectancy = +0.0000** (literally zero to 4 dp). This
is a textbook random-walk signature.

## 6. Comparison to CAMPAIGN_010 (informational; not used for tuning)

| dimension | CAMPAIGN_010 (session_breakout) | **CAMPAIGN_011 (random_entry_anchor)** |
|---|---:|---:|
| total trades | 2,791 | **1,177** (≈ −58 %) |
| aggregate expectancy R | −0.0408 | **−0.0024** (much closer to 0) |
| aggregate return % | −36.56 % | **−0.53 %** (much closer to 0) |
| aggregate profit factor | 0.04 | **0.91** (much closer to 1) |
| pairs positive | 1 / 7 (USD_CHF only) | **3 / 7** (closer to uniform expectation of ~3.5) |
| fold pass rate | 0 / 8 | **0 / 8** (same — both REJECT) |
| single-pair dominance | 24.1 % | **36.5 %** (still under 40 % gate) |
| single-fold dominance | 30.3 % | **40.1 %** (still under 60 % gate) |
| verdict | REJECT | **REJECT** (expected outcome of the null model) |

This is a **diagnostic comparison** — it confirms that the
random-entry null model produces metrics consistent with no-edge
expectations (expectancy near 0, profit factor near 1, return
near 0), while the directional CAMPAIGN_010 strategy produced
decisively negative metrics (expectancy −0.04 R, profit factor
0.04, return −37 % over the same universe + cost model). The
comparison is informational; **it does not motivate any
parameter tweak** in either direction (per the binding
no-tuning rules of this sprint).

## 7. Implementation bug fixes during this sprint

**None required for the candidate itself.** The runner
(`scripts/run_campaign_011.py`) is a clone of
`scripts/run_campaign_010.py` with the strategy class swapped
and the `FROZEN_PARAMETERS` / `EXPECTED_*` constants updated.
Both ran cleanly. No edit to the strategy module, no edit to
the engine, no edit to financing.

## 8. Data issues found

None affecting the candidate's evaluation. The candidate ran
cleanly against every pair × every fold; no per-pair fold
returned a `nan`/`inf` metric or aborted due to missing
candles. EUR_USD's low trade count in fold 7 (8 trades — just
below the 30 per-fold gate's general suggestion but the
aggregate-trade-count gate is the binding one) reflects the
candidate's R4 entry-probability gate combined with bars in
spread-filter rejection — a property of the strategy + cost
model, not the data.

## 9. Committed artifacts (compact)

```
backtests/CAMPAIGN_011_random_entry_anchor/
├── walk_forward/
│   ├── plan.json            # Phase 2
│   ├── plan.md              # Phase 2
│   ├── results.json         # Phase 4 (this phase)
│   ├── results.md           # Phase 4 (this phase)
│   └── fold_detail.json     # Phase 4 (this phase)
└── folds/
    ├── fold_00/             # Phase 4 (this phase)
    │   ├── fold_00_<PAIR>_summary.json   # 7 pairs
    │   └── fold_00_<PAIR>_trades.csv     # 7 pairs
    ├── fold_01/  ...        # ... 8 folds total
    ...
```

Total folds directory size: ~600 KB total artifact directory.
Equity-curve CSVs were intentionally **not** emitted (same
convention as CAMPAIGN_010). Trades CSV per pair × fold + a
compact summary JSON; campaign-level `walk_forward/results.{json,md}`
+ `fold_detail.json` carry the gate-vector evidence.

## 10. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (untouched).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **CAMPAIGN_011** scaffold-status; verdict classification
  pending in Phase 5; **cannot be approved by design** (null
  model).
- **No broker / OANDA call** — runner reads only the local
  store.
- **No `.env` read; no credential printed; no account / order /
  trade / position / transaction endpoint queried.**
- **No QuantConnect / LEAN** action.
- **No engine-PnL change.** No `src/forex_bot/financing.py`
  edit. The runner uses `BacktestEngine` and
  `RiskEngine(mode="backtest")` exactly as
  `scripts/run_campaign_010.py` does.
- **No parameter tuning.** The frozen-parameter assertion +
  belt-and-suspenders master-seed check in the runner aborts
  before any backtest if a single YAML value drifts.
- **No seed optimization.** `master_seed = 20260523` was the
  only seed used; no other seed was tried.
- **`paper-loop` / `demo-loop` refuse**; no `live-loop` command.

## 11. Explicit null-model / no-approval statement

This phase produces *research evidence* — fold-level trade
ledgers, metrics, and a per-fold gate vector. It does not
approve the strategy. **CAMPAIGN_011 cannot be approved by
design.** Even the expected REJECT verdict (recorded in Phase 5)
does not affect the registry — the null model's value is in
*establishing the falsifiability floor*, not in any kind of
"passing" outcome.

The Phase 5 doc
([`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md))
records the formal verdict against
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§11.

## 12. Cross-links

- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md)
- [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`scripts/run_campaign_011.py`](../../scripts/run_campaign_011.py)
- [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json)
- [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.md`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.md)
- [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json)
- [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md)
  (the directional-strategy comparison baseline)

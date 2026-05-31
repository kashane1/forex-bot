# CAMPAIGN_029 — execution continuation plan

**Strategy:** `usdjpy_range_bar_mtf_breakout 0.1.0-c029`
**Branch:** `research-campaign-029-usdjpy-range-bar-scaffold-001` (continued, unmerged)
**Date:** 2026-05-29
**Status going in:** `SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED`

> Extend the existing scaffold into an **execution-ready research lane**: an
> M1-resolved range-bar execution engine, a frozen HTF/D1AGG staleness policy, an
> independent parity harness, and **train + validation only** evidence. The
> **frozen rule is not changed**; the **test lockbox stays closed**; nothing is
> approved; paper/demo/live stay blocked.

---

## 0. Continuation audit (Phase 0 — executed 2026-05-29)

| item | result |
|------|--------|
| branch | ✅ `research-campaign-029-usdjpy-range-bar-scaffold-001`, clean tree |
| scaffold commits | ✅ 7 commits `d1836a8…062acf7` present, unmerged vs `origin/main` |
| scaffold artifacts | ✅ precommit, config, preflight, strategy, tests, HTF & parity designs all present |
| USD_JPY M1 | ✅ local Postgres, 1,844,454 rows, 2021-05-27 → 2026-05-26 |
| H4M1 context | ✅ granularity `H4M1` stored, 5,448 bars, 2021-05-26 → 2026-05-26 |
| native H4 → D1AGG | ✅ native `H4` 9,959 bars (2020-01-01 →); `aggregate_h4_to_d1` derives D1AGG |
| M1 bid/ask | ✅ present → realistic per-fill spread cost (M1-resolved) |
| pytest / ruff / freeze / archive / secrets | ✅ 2273 passed/3 skipped; ruff clean; all gates PASS |

## 1. Data sources (frozen for this sprint)

- **Execution bars:** 10-pip USD_JPY range bars from **M1 mid** via
  `non_time_bars.build_range_bars` (deterministic, lookahead-free; system of record).
- **Fill/stop resolution:** the **underlying M1 rows** (bid/ask/mid) that each range
  bar aggregates (`RangeBar.source_start_time … source_end_time`).
- **H4 trend (H4M1):** stored `H4M1` granularity (`m1_derived`).
- **D1AGG:** `aggregate_h4_to_d1(native H4)` → `native_h4_derived_d1agg`. M1-derived
  D1AGG remains rejected.

## 2. Plan (phases)

1. **Phase 0** — this plan + continuation audit. *(commit)*
2. **Phase 1** — `src/forex_bot/research/range_bar_execution.py`: M1-resolved engine
   (next-range-bar-open entry, M1-walked structural stop, 12-bar time stop, no TP,
   conservative ambiguity ordering) + trade ledger + tests. *(commit)*
3. **Phase 2** — `CAMPAIGN_029_HTF_D1AGG_AVAILABILITY_AND_STALENESS.md`: quantify
   missing/stale H4 & D1AGG over train/validation; **freeze** the staleness policy. *(commit)*
4. **Phase 3** — `scripts/run_campaign_029_usdjpy_range_bar_mtf_breakout.py`:
   train/validation runner; compact artifacts under `research/campaign_029/execution/`;
   **lockbox refused**. *(commit)*
5. **Phase 4** — independent parity harness + `CAMPAIGN_029_PARITY_RESULT.md` +
   `research/campaign_029/parity/`. *(commit)*
6. **Phase 5** — execute **train**, then **validation** (confirmation only, per
   frozen policy); `CAMPAIGN_029_TRAIN_RESULT.md`, `…_VALIDATION_RESULT.md`,
   `…_GATE_DECISION.md`. *(commit)*
7. **Phase 6** — `CAMPAIGN_029_FINAL_INTERPRETATION.md` + execution summary; update
   `EVIDENCE_INDEX.md`, `STRATEGY_STATUS.md`, `EVIDENCE_MANIFEST.json`. *(commit)*
8. **Phase 7** — final validation gate + close-out response. *(commit if needed)*

## 3. Frozen execution-realism rules (from precommit — restated, not changed)

- Entry = **open of the next completed range bar** after the trigger bar's close
  (the first M1 row of bar `i+1`). No same-(range-)bar fill.
- Stop = `max(5-bar swing, 2.0 × 10 pip = 20 pip floor)` from the trigger close;
  **walked on M1** within the holding window. Conservative ambiguity: within one M1
  candle, a stop touch is taken **before** the time exit (frozen priority
  `stop → time → end_of_data`).
- Time stop = exactly **12 completed range bars** after entry. **No** profit target.
- Cost = conservative, **M1-resolved**: real half-spread at the entry and exit M1
  fill rows + `fixed_slippage_pips = 0.2` adverse each side (config `backtest:`).

## 4. Gates (from precommit §10 — frozen, applied at Phase 5)

Train expectancy ≥ 0; validation expectancy > 0; validation PF ≥ 1.05; validation
trades ≥ 100 (else `INSUFFICIENT_SAMPLE`); 2× cost-stress validation expectancy ≥ 0;
beat C011 null by ≥ +0.010R; spread/range-size documented; parity required before
any promotion-review; **test lockbox stays closed**; max status
`PROMOTION_REVIEW_REQUIRED` — never approved.

## 5. Hard rules honoured

Stay on this branch; no merge/push; no approval; `approved_strategies.yaml` stays
`[]`; no paper/demo/live; no OANDA/network; no live creds; no parameter tuning; no
rule change after results; lockbox closed; commit only compact docs/configs/tests/
manifests (full ledgers/bars stay local & gitignored).

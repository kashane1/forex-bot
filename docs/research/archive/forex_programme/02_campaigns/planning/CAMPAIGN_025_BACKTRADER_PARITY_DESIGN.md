# CAMPAIGN_025 — Backtrader parity design (DESIGN STUB)

**Strategy:** `m5_donchian_htf_confluence_breakout 0.1.0-c025`
**Status:** design only — **no Backtrader implementation in this scaffold sprint**.

> Backtrader parity is a **precommitted gate** (precommit §9.9): no
> promotion-review classification may be assigned until the M5 Donchian + HTF
> confluence strategy reproduces in Backtrader, within tolerance, the trades the
> research engine produces. This document specifies *how* that parity run will be
> built in the later execution sprint. It does not run anything now.

---

## 1. What must match

The research engine (`scripts/run_campaign_025_*` future train/validation lane)
and a Backtrader port must agree, per pair and per split, on:

- the **set of entry signals** (signal bar timestamp + side),
- the **entry fill price** (next M5 bar open),
- the **initial stop price**,
- the **exit reason and bar** (stop / time / eod),
- aggregate **trade count**, **expectancy (R)**, and **profit factor**.

## 2. How M5 entries map to Backtrader

- Feed: the **M5 materialized** series (`m1_materialized`) is the Backtrader
  primary data feed (`cerebro.adddata`), one feed per instrument.
- The Donchian breakout is computed on **prior completed M5 bars only**. In
  Backtrader terms, on bar close `t` the channel is `Highest(high, 20)[-1]`
  (i.e. excluding bar `t`), mirroring `donchian_high(high, 20)` which uses
  `.shift(1)`. The signal evaluates at bar `t` close; **no same-bar action**.
- Position sizing and the one-position-per-instrument rule are enforced in the
  strategy's `next()`; a new entry is suppressed while a position is open.

## 3. How H1 / H4 / D1AGG context is provided without lookahead

Two acceptable implementations; the execution sprint must pick one and freeze it:

- **(A) Multi-data resampling.** Add M15/H1/H4 as resampled Backtrader data feeds
  and the native-H4-derived D1AGG as a separate feed. Backtrader only delivers a
  higher-timeframe bar **after it closes**, which matches `align_last_completed`
  (last completed HTF bar ≤ decision). Care: Backtrader's resampling boundaries
  must match the materialized bar boundaries exactly (see risks).
- **(B) Precomputed aligned columns.** Precompute, per M5 timestamp, the
  last-completed H1/H4/D1AGG EMA/close features using the **same**
  `align_last_completed` helper the research engine uses, and attach them as
  Backtrader lines. This guarantees byte-identical context and is the
  recommended primary; option (A) becomes an independent cross-check.

In both cases the D1AGG feed is the **native-H4-derived** aggregation
(`aggregate_h4_to_d1`), never M1-derived.

## 4. How `next_bar_open` is represented

- The research engine fills at the **open of the M5 bar after** the signal bar.
- In Backtrader, issue the order on the signal bar's `next()`; with
  `cheat_on_open = False` the order executes at the **next bar's open** by
  default — this is the parity target. `cheat_on_open` must remain **off**.
- The stop is submitted as a child stop order at the frozen `stop_price`
  (computed from signal-bar data); it is **not** trailed.

## 5. Expected parity tolerances (to be finalized in the execution sprint)

| Quantity | Tolerance |
|---|---|
| Entry signal set (timestamp+side) | exact match required (0 unmatched) |
| Entry fill price | ≤ 1e-6 in price (rounding only) |
| Initial stop price | ≤ 1e-6 in price |
| Exit bar index | exact for stop/time; ±1 bar allowed only for `eod` boundary |
| Trade count (per pair) | exact, or ≤ 1% documented residual w/ root-caused diff list |
| Expectancy (R), per split | ≤ 0.005R |
| Profit factor, per split | ≤ 0.02 |

If exact entry-set match fails, the residual must be enumerated trade-by-trade
and root-caused before any promotion-review classification.

## 6. Known risks

- **M5 resampling alignment.** Backtrader's resample boundaries (esp. across
  the 17:00 NY daily/weekly alignment) may not coincide with the materialized
  M1-derived bar edges. Mitigation: prefer option (B) precomputed columns;
  validate option (A) boundaries against the materialized timestamps directly.
- **Session gaps.** Weekend / holiday gaps can shift the "prior 20 M5 bars"
  window; both engines must define the channel over **completed bars in series
  order**, not wall-clock windows.
- **Spread / slippage modeling.** The research engine applies a spread/slippage
  cost model (`fixed_slippage_pips`, `spread_slippage_multiplier`); the
  Backtrader commission/slippage scheme must be configured to match, and the
  **2× cost stress** must be reproducible on both.
- **HTF indicator warmup.** EMA20/EMA50 on H1/H4/D1AGG require warmup; both
  engines must drop signals before warmup completes identically (research engine
  requires ≥52 HTF bars).
- **Donchian prior-bar behavior.** The single highest-risk parity point: the
  channel must exclude the current bar in **both** engines (`.shift(1)` vs
  `Highest(...)[-1]`). A one-bar offset here silently changes every breakout.
- **Time stop counting.** The 48-bar time stop counts **completed M5 bars after
  entry**; Backtrader bar counting must start at the entry bar consistently.

## 7. Scope note

This sprint implements **none** of the above. Parity is built and run only in the
future `…-train-validation-001` (or a dedicated parity) sprint, and is a
hard precondition for any promotion-review classification.

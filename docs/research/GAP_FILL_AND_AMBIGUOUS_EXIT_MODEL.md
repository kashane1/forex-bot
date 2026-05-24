# Gap-Fill and Ambiguous-Exit Model

**Date:** 2026-05-24 · **Sprint:** [`infra-exit-fidelity-001`](INFRA_EXIT_FIDELITY_001_PLAN.md)

The backtest engine in [src/forex_bot/backtesting/engine.py](../../src/forex_bot/backtesting/engine.py) now has two new exit-fidelity features:

1. **Ambiguous-exit instrumentation** (always-on) — records bars where the same-bar stop-precedence tie-break hid a take-profit that was also in range. Pure observation; never changes any exit price, PnL, or `config_hash`.
2. **Opt-in gap-through fill** (`backtest.gap_fill_policy = "gap_through"`) — when a bar OPENS past a stop or take-profit level, fills at the bar open instead of at the level. Default `"none"` preserves byte-identical `config_hash` for every CAMPAIGN_001–009 artifact.

This document is the operating model for both features. It is parallel to [FILL_TIMING_MODEL.md](FILL_TIMING_MODEL.md) (the precedent opt-in fidelity feature from `infra-execution-fidelity-001`).

---

## 1. Same-bar SL+TP ambiguous-exit

### Why it matters

The engine's exit precedence (engine.py:259-291) uses an `if/elif` chain:

```
if adverse stop in range:   exit reason = "stop" / "trailing_stop"
elif tp in range:           exit reason = "target"
elif bars_held >= max:      exit reason = "time"
```

When BOTH the adverse stop AND the take-profit are in range on the same bar, the stop wins by design — pre-declared in [CAMPAIGN_009_PRECOMMIT.md §59](CAMPAIGN_009_PRECOMMIT.md):

> "if a bar touches both the stop and the target, the adverse stop wins (conservative)"

The tie-break is correct from a risk-management standpoint: OHLC alone cannot prove which level was hit first within the bar, so the adverse interpretation is the honest default. But the engine never recorded how OFTEN this happened. For a mean-reversion strategy with a midline TP (CAMPAIGN_009), the question "how many of these stop-outs could have been TP wins?" was previously unanswerable.

### Behavior

On every exit-bar where:

- `exit_reason in {"stop", "trailing_stop"}`, AND
- `take_profit_price is not None`, AND
- the take-profit was provably in range on the same bar (long: `bid_high >= tp`; short: `ask_low <= tp`),

the engine sets `TradeRecord.ambiguous_exit = True`. Aggregated as `BacktestMetrics.ambiguous_exit_count` (and mirrored on `BacktestResult.ambiguous_exit_count`).

The flag is **pure observation** — `exit_reason`, `exit_price`, `pnl`, `r_multiple` are all unchanged. The same-bar tie-break is unchanged.

### When the flag is False

- Strategy emits no `take_profit_price`.
- Exit reason is `"time"` or `"eod"` (which by construction means stop and tp were both NOT in range).
- The exit-bar's range did not reach the TP.

### Surfacing

- Per-trade: trades CSV column `ambiguous_exit` (boolean).
- Aggregate: metrics JSON `metrics.ambiguous_exit_count`, metrics MD line `Ambiguous same-bar SL+TP exits: **N**`, summary JSON `metrics.ambiguous_exit_count`.

---

## 2. Opt-in gap-through fill

### What it changes

When `gap_fill_policy = "gap_through"` is set on the engine (default `"none"`), the engine activates four cases:

| trade side | exit kind | gap test | fill price | direction |
|---|---|---|---|---|
| long  | stop | `bid_open < pre_trailing_stop_price` | `bid_open` | **adverse** (worse than stop) |
| short | stop | `ask_open > pre_trailing_stop_price` | `ask_open` | **adverse** (worse than stop) |
| long  | tp   | `bid_open > tp_price` | `bid_open` | **favorable** (better than tp) |
| short | tp   | `ask_open < tp_price` | `ask_open` | **favorable** (better than tp) |

Mirrors how real stop-market and limit orders fill when price has already moved through the level. Precedence within the resolver: adverse stop > favorable tp (mirrors the existing if/elif precedence).

#### Semantics: bar-open as the first event in `gap_through` mode

A subtle but correct consequence of gap-through is that the **bar-open is modeled as the chronologically-first event in the bar**. When the bar opens past a favorable level (long: `bid_open > tp`), the gap-fill resolver closes the trade at the open — *before* the intra-bar range can fire anything else. So if the same bar also wicks DOWN through the stop later in the bar, the stop never fires, because the trade is already closed at the favorable open price.

Concretely, for a long with `gap_fill_policy="gap_through"`:

| Bar geometry | `none` mode exit | `gap_through` mode exit |
|---|---|---|
| `bid_open` > tp, `bid_low` ≤ stop | `stop` at `stop_price` (adverse — range precedence) | `target` at `bid_open` (favorable — open precedence) |
| `bid_open` < stop, `bid_high` ≥ tp | `stop` at `stop_price` | `stop` at `bid_open` (still adverse, but worse) |
| `bid_open` ≤ tp and ≥ stop | (uses regular range tests) | (uses regular range tests) |

The flip in row 1 is **not a bug** — it correctly models a TP limit order that would have filled at the open (1.10700) before price ever reached the stop later in the bar. In default mode, the engine uses intra-bar range only (OHLC alone cannot prove order of touches, so the conservative stop-precedence rule applies). In `gap_through` mode, the bar-open is treated as an additional, chronologically-first reference point. Verified by `tests/unit/test_gap_fill.py::test_long_tp_gap_overrides_intra_bar_adverse_stop` and the short mirror.

When a gap-fill fires:

- `TradeRecord.gap_fill = True`
- `TradeRecord.gap_fill_distance_pips = |level - fill_price| / pip_size`
- `BacktestMetrics.gap_fill_exit_count` and `BacktestResult.gap_fill_exit_count` aggregate.
- `BacktestResult.gap_fill_policy = "gap_through"` (surfaces the active policy on every artifact).

### Trailing-stop ordering caveat (the snapshot)

The trailing stop is updated at the TOP of every bar using that bar's close (engine.py:237-254), BEFORE exit checks run. This is intentional and load-bearing for CAMPAIGN_001-009 behavior, but it creates a subtle question for gap-fill: the comparison against the bar's OPEN should test against the stop level that was **active when the bar opened**, not against a level derived from the bar's close.

The engine handles this by snapshotting:

```python
pre_trailing_stop_price: Decimal = open_trade.stop_price  # snapshot
# ... trailing update runs here, mutating open_trade.stop_price ...
# Gap-fill comparison uses pre_trailing_stop_price (the original level)
# Range tests (bid_low <= open_trade.stop_price) use the post-update level
# (unchanged behavior).
```

This means:

- A bar that opens BELOW the *post-update* (tightened) stop but ABOVE the *pre-update* stop does NOT gap-fill — the new stop didn't exist when the bar opened. The regular range check fires instead.
- A bar that opens BELOW the *pre-update* stop DOES gap-fill — at the bar's open, the trader was already past the original stop level.

Alternative orderings considered and rejected:

- **Defer trailing update until after exits.** Would change the post-update stop semantics for non-gap-fill bars under any `fill_timing` mode, breaking hash compatibility.
- **Accept the time inversion** (compare against post-update stop). Would let a stop that did not yet exist at the bar's open "win" against the open price. Dishonest.

### bid/ask_open None fallback

When a candle has no bid/ask split (synthetic data, or pre-CAMPAIGN-002 mid-only candles), the engine falls back to the mid `open` column — same convention as `bid_low → low`, `ask_high → high`, etc. Uses `pd.notna(...)` (not `is not None`) because pandas coerces stored `None` to numpy NaN at DataFrame construction.

The same NaN-aware fallback was retrofitted onto the pre-existing bid_low/ask_high/bid_high/ask_low/bid_close/ask_close resolutions during this sprint (the latent bug never triggered before because every prior test set bid/ask explicitly). This is a strict correctness improvement; no test outcome changed.

### Compatibility with prior campaigns

Quoting [FILL_TIMING_MODEL.md §"Compatibility with old campaigns"](FILL_TIMING_MODEL.md):

> "The engine only folds `fill_timing` into its `config_hash` when it departs from `signal_bar_close`. A `signal_bar_close` run therefore produces the **same `config_hash`** as it did before this feature existed, so prior campaign artifacts (CAMPAIGN_001–009) stay hash-comparable. A `next_bar_open` run gets a distinct `config_hash`, so the two can never be silently confused."

The same guarantee holds for `gap_fill_policy`:

- Default `"none"` does NOT fold into `config_hash` → byte-identical hash to pre-sprint runs.
- Opt-in `"gap_through"` DOES fold in → distinct hash, no silent confusion.

This is verified at every commit by:
- The pinned hash snapshot at [tests/fixtures/pre_sprint_config_hashes.json](../../tests/fixtures/pre_sprint_config_hashes.json) covering CAMPAIGN_001 / CAMPAIGN_004 / CAMPAIGN_009 (carries a `_doc` guardrail to prevent accidental regeneration — see [AC-13](INFRA_EXIT_FIDELITY_001_PLAN.md)).
- Three regression tests:
  - `test_phase1_does_not_change_config_hash_for_pinned_configs` (Phase 1)
  - `test_default_policy_matches_phase0_snapshot` (Phase 2)
  - `test_snapshot_doc_guardrail` (Phase 2 — asserts the `_doc` warning string is preserved)

### Lean parity impact

Under default `gap_fill_policy = "none"`, every Lean-parity verdict is byte-identical to pre-sprint — the parity baselines at [tests/research/test_parity_verifier_*.py](../../tests/research/) require no change.

Under opt-in `gap_fill_policy = "gap_through"`, parity comparisons are **out of scope for this sprint**. Lean stop-market orders already fill at stop-or-worse ([CAMPAIGN_002_LEAN_MAPPING_SPEC.md §131-133](CAMPAIGN_002_LEAN_MAPPING_SPEC.md:131)), so the bespoke engine in `gap_through` mode is moving toward Lean's behavior — but the existing parity tolerance baselines were captured under the old bespoke behavior and would likely diverge. Regenerating them is a separate sprint that requires fresh Lean cloud runs.

### Artifact asymmetry

Committed `backtests/campaign_*/runs/_index.json` and `*_summary.json` files predate this sprint and **do not** carry the new keys (`gap_fill_policy`, `ambiguous_exit_count`, `gap_fill_exit_count`). Freshly-generated artifacts (from any default-mode rerun) **do** carry them.

This asymmetry is expected. Backfilling the old files would violate the research freeze ([forex-bot-research-freeze](../../README.md)). All `_index.json` readers ([scripts/build_campaign_*_report.py](../../scripts/), [scripts/build_marathon_report.py](../../scripts/build_marathon_report.py)) use the tolerant `json.loads(...read_text()) + .get(name, default)` pattern and handle both shapes cleanly. This is verified by [test_committed_index_json_files_load_cleanly](../../tests/unit/test_exit_fidelity_exporters.py).

---

## 3. Configuration

```yaml
# configs/<your-config>.yaml
backtest:
  fill_timing: signal_bar_close   # default; opt-in: next_bar_open
  gap_fill_policy: none           # default; opt-in: gap_through
```

```bash
# CLI override (takes precedence over config)
bot backtest --config configs/paper.yaml \
             --fill-timing next_bar_open \
             --gap-fill-policy gap_through
```

The CLI prints both at startup:

```
fill timing: next_bar_open
gap fill: gap_through
```

The two flags are orthogonal and can be combined freely.

---

## 4. Known limitations

### Entry-bar gap-through-stop (out of scope)

In `next_bar_open` fill timing, the entry happens at bar N+1's open. If bar N+1 gaps far past the signal-time stop, the trade can fill at a price worse than its own stop — leaving the trade "born underwater". The engine's exit-check on bar N+1 then immediately triggers the stop, producing a perverse "profit" (sold for more than the entry price on a long). This is a pre-existing pathology in the entry path, unrelated to exit fidelity. **Deserves a dedicated audit sprint.** Not addressed here.

### Gap-fill mode breaks Lean parity baselines

See "Lean parity impact" above. Anyone selecting `gap_through` and then asking "does this match Lean?" gets no answer until parity baselines are regenerated.

### Single distance, not direction

`gap_fill_distance_pips` records the *absolute* distance between the level and the fill price. Whether the gap was adverse (stop) or favorable (tp) is implicit in `exit_reason` — a future enhancement could split this into signed `gap_fill_distance_pips` for cleaner analytics.

### No same-bar-but-gap-not-touched flag

`ambiguous_exit` records only the case where the regular range test (bid_high >= tp) shows the TP in range. With `gap_fill_policy = "gap_through"` AND a bar that opens past the TP, the gap-fill resolver sees the TP at the open (favorable gap) but if the adverse stop was ALSO past the open, the stop wins per precedence. The `ambiguous_exit` flag still fires (because bid_high >= tp). No additional flag distinguishes "TP was reachable at OPEN specifically" vs "TP was reachable somewhere in the bar". A future enhancement could split this.

---

## 5. Recommendation

### When to use which policy

| Goal | gap_fill_policy |
|---|---|
| Reproduce a CAMPAIGN_001–009 verdict byte-for-byte | `none` |
| Measure how often gap-through fills would change a verdict | `gap_through` |
| Compare against Lean parity (today) | `none` (baselines were captured under this mode) |
| New D1AGG or daily research from scratch | `gap_through` (daily gaps are largest) |

### Detailed guidance

- **Default-mode (`none`) results** are byte-identical to pre-sprint and remain the canonical reference for every CAMPAIGN_001-009 result.
- **`gap_through` mode** is research infrastructure: useful for measuring how often gap-through fills would change a campaign's verdict, and for moving toward Lean parity in a future sprint. Treat its results as new audit data, not as a re-run of an existing campaign verdict.
- **`ambiguous_exit_count`** is the first quantitative measurement of same-bar SL+TP collisions in CAMPAIGN_008/009-style strategies — use it to decide whether the conservative stop-precedence rule is materially under-reporting TP wins.
- **The pinned hash snapshot** at [tests/fixtures/pre_sprint_config_hashes.json](../../tests/fixtures/pre_sprint_config_hashes.json) is load-bearing. Do not regenerate it to "make tests pass"; the regeneration script at [scripts/snapshot_pre_sprint_hashes.py](../../scripts/snapshot_pre_sprint_hashes.py) carries a header warning, and the `_doc` guardrail test asserts the warning string is preserved.

---

## Cross-references

- Plan: [INFRA_EXIT_FIDELITY_001_PLAN.md](INFRA_EXIT_FIDELITY_001_PLAN.md) and [docs/plans/2026-05-24-feat-backtest-exit-fidelity-plan.md](../plans/2026-05-24-feat-backtest-exit-fidelity-plan.md) (deepened workflow plan)
- Precedent opt-in feature: [FILL_TIMING_MODEL.md](FILL_TIMING_MODEL.md)
- Same-bar tie-break rule: [CAMPAIGN_009_PRECOMMIT.md §59](CAMPAIGN_009_PRECOMMIT.md)
- Original gap mismatch documentation: [CAMPAIGN_002_LEAN_MAPPING_SPEC.md §131-133](CAMPAIGN_002_LEAN_MAPPING_SPEC.md:131)
- Sibling sprint (entry fidelity): [INFRA_EXECUTION_FIDELITY_001_PLAN.md](INFRA_EXECUTION_FIDELITY_001_PLAN.md) + [INFRA_EXECUTION_FIDELITY_001_SUMMARY.md](INFRA_EXECUTION_FIDELITY_001_SUMMARY.md)

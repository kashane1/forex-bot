# Backtrader CAMPAIGN_011 — Phase 5 fidelity fix

**Date:** 2026-05-25
**Branch:** `infra-backtrader-secondary-lane-004-campaign-011`
**Phase:** 5 of `BACKTRADER_CAMPAIGN_011_004_PLAN.md`
**`strategy_evidence: false`**

> Two Backtrader-lane fidelity bugs found by the Phase 3 + 4 real-data
> comparison are fixed here. After both fixes, the BT-lane CAMPAIGN_011
> output matches the bespoke no-RiskEngine reference **trade-for-trade**
> on all 7 pairs (2 800 / 2 800; 100 % match by `(entry_time, side)`).
> No bespoke-engine change, no CAMPAIGN_011 rule change, no strategy
> approval. CAMPAIGN_011 remains REJECT / null diagnostic anchor by
> design.

## 1. Initial divergence (preserved from Phase 4)

| pair | pre-fix BT trades | bespoke trades | Δ |
|---|---|---|---|
| EUR_USD | 395 | 394 | +1 |
| GBP_USD | 401 | 400 | +1 |
| USD_JPY | 419 | 418 | +1 |
| AUD_USD | 385 | 385 | 0 |
| USD_CAD | 396 | 394 | +2 |
| USD_CHF | 411 | 409 | +2 |
| NZD_USD | 401 | 400 | +1 |
| **total** | **2 808** | **2 800** | **+8** |

Pre-fix harness verdict: `TOLERABLE_DRIFT` (all per-pair Δ ≤ 0.51 %
inside the wider 10 % band; the harness does not check
`expectancy_r` / `return_pct` on the BT side out of the box).
Sprint-plan binding classification: `SIGNAL_RULE_MISMATCH` (the rule
that defines when the strategy is first eligible to fire differs).

## 2. Root causes (two BT-lane bugs)

### 2.1 Bug A — warmup off-by-N (-7 trades on a fix)

The BT adapter honoured only the in-strategy R1 check
(`len(df) >= atr_lookback + 2 = 16`), but the bespoke engine
respects `strategy.warmup_bars_required() = 32` via
`warmup = max(strategy.warmup_bars_required(), 5)` at
`src/forex_bot/backtesting/engine.py:204,220`. The strategy declares
`warmup_bars_required() = 32` at
`src/forex_bot/strategies/random_entry_anchor.py:99-101` with the
comment *"ATR(14) needs ≥15 bars; +1 for accessing index -2; small
buffer"*. So bars 16-31 were eligible for the BT adapter but
deliberately skipped by the bespoke engine. Any SHA-256 gate fires
in that 16-bar window became extra BT trades.

### 2.2 Bug B — same-bar EOD re-entry (-1 trade on a fix)

The BT adapter's `_try_exit()` had a third priority case ("end-of-data")
that closed any open trade at the last bar of the data with
`exit_reason="eod"`. After this close, `next()` then ran `_try_entry()`
since `self._in_position` was now False, and if the SHA-256 gate
fired on that final bar, the adapter opened a new trade — which was
immediately closed by `stop()` with `bars_held=0`. The bespoke
engine does **not** do this: its per-bar loop only checks
adverse-stop and time-stop inside the loop, and closes any
still-open trade in a **post-loop** block at
`src/forex_bot/backtesting/engine.py:646-683`. So bespoke never
gets a chance to fire a fresh entry on the very last bar; only the
existing open trade is closed.

USD_CAD's last bar (`2026-05-19T21:00:00+00:00`) is the example: the
SHA-256 gate fires on it (gate_value ≈ 0.029 < 0.05), side=short.
BT pre-fix recorded an extra short trade there; bespoke didn't.

The bug also exists structurally in
`research/backtrader_lane/strategies/campaign_002_trend_following.py`
(the CAMPAIGN_002 adapter's `_try_exit()` has the same priority-3
EOD close inside the per-bar loop). It does not manifest for
CAMPAIGN_002 because:
- CAMPAIGN_002's strategy needs an EMA-50/200 crossover AND a
  Donchian-20 breakout on the last bar AND `EMA(50) > EMA(200)` etc.
  — these almost certainly do not all coincide on the very last
  H4 bar in 2026-05-19 21:00.
- CAMPAIGN_002 sprint-003 already passed PASS without this fix
  surfacing, so the bug is dormant there.

**Scope discipline:** this sprint only fixes the CAMPAIGN_011
adapter. The dormant CAMPAIGN_002 bug is documented here as a
follow-up. (See §6 below.)

## 3. Fixes applied

### 3.1 Fix A — warmup-threshold constant

Adds two module-level constants and rewrites the R1 guard:

```python
WARMUP_BARS_REQUIRED = 32
WARMUP_BAR_COUNT_THRESHOLD = WARMUP_BARS_REQUIRED + 1  # 1-based BT len(self)
...
def _try_entry(self) -> None:
    if _bar_count(self) < WARMUP_BAR_COUNT_THRESHOLD:
        return
    ...
```

A new regression unit test
(`test_warmup_threshold_matches_bespoke_strategy`) imports
`RandomEntryAnchorStrategy().warmup_bars_required()` from the
bespoke side and asserts both constants line up. If a future sprint
ever changes either side's warmup, the test will fail loudly.

### 3.2 Fix B — drop the in-loop EOD close

Removes the third priority case from `_try_exit()`. The `stop()`
method (Backtrader's after-the-last-bar hook) already closes any
open trade with `exit_reason="eod"` at the last bar's close — the
same behaviour the bespoke engine has in its post-loop block at
`engine.py:646-683`. With this change, the BT adapter never fires
a fresh entry on the very last bar (because `_in_position` is True
when `next()` returns, blocking `_try_entry()`).

## 4. Post-fix result

```
$ python scripts/run_backtrader_parity.py \
      --campaign CAMPAIGN_011 \
      --output research/backtrader_lane/results/campaign_011_full_window_004_postfix
Total trades: 2800
Total PnL (account): -28.6922
```

Per-pair (vs bespoke reference):

| pair | post-fix BT trades | bespoke trades | Δ | match by (entry_time, side) |
|---|---|---|---|---|
| EUR_USD | 394 | 394 | 0 | **394/394** |
| GBP_USD | 400 | 400 | 0 | **400/400** |
| USD_JPY | 418 | 418 | 0 | **418/418** |
| AUD_USD | 385 | 385 | 0 | **385/385** |
| USD_CAD | 394 | 394 | 0 | **394/394** |
| USD_CHF | 409 | 409 | 0 | **409/409** |
| NZD_USD | 400 | 400 | 0 | **400/400** |
| **total** | **2 800** | **2 800** | **0** | **2 800/2 800** |

100 % trade-for-trade match on `(instrument, entry_time, side)`.

Post-fix comparison-harness verdict (with the tight CAMPAIGN_011
tolerances):

```
$ python scripts/compare_backtrader_parity.py \
      --campaign CAMPAIGN_011 \
      --backtrader-results research/backtrader_lane/results/campaign_011_full_window_004_postfix/ \
      --bespoke-reference research/lean_parity/campaign_011_h4_bespoke_reference.json \
      --output backtests/diagnostics/backtrader_campaign_011_full_window_004_postfix \
      --trade-count-tolerance-pct 0.0 \
      --expectancy-r-tolerance 0.005 \
      --return-pct-tolerance 0.10 \
      --win-rate-tolerance 0.001
Overall classification: PASS
```

Every per-pair classification: `PASS`.

## 5. Post-fix determinism

Two consecutive BT-lane runs produced bit-identical artefacts:

```
$ shasum -a 256 /tmp/c011_post_run1.json /tmp/c011_post_run2/backtrader_summary.json
26d078da91691ff79f05a5dfbfef50d59c280d81435c881c4d67cae855127fbc  run1/backtrader_summary.json
26d078da91691ff79f05a5dfbfef50d59c280d81435c881c4d67cae855127fbc  run2/backtrader_summary.json

$ shasum -a 256 /tmp/c011_post_trades_run1.jsonl /tmp/c011_post_run2/backtrader_trades.jsonl
86f0e03b3f42ccca3a486d90b8901c2500bf448497e75f10afae6fc015d5da0a  run1/backtrader_trades.jsonl
86f0e03b3f42ccca3a486d90b8901c2500bf448497e75f10afae6fc015d5da0a  run2/backtrader_trades.jsonl
```

## 6. Unresolved drift

**None for CAMPAIGN_011.** Every per-pair, per-trade `(entry_time,
side)` matches the bespoke side bit-for-bit.

**One dormant follow-up:** the in-loop EOD close pattern in
`research/backtrader_lane/strategies/campaign_002_trend_following.py`
(CAMPAIGN_002's adapter) is structurally the same bug as §2.2 here.
It does not manifest because the CAMPAIGN_002 strategy is much
harder to trigger on the last bar (multi-condition signal). A
future BT-lane hardening sprint may want to extract a shared
`_post_loop_eod_close()` helper and standardise both adapters.
This sprint does **not** touch the CAMPAIGN_002 adapter per the
scope discipline (sprint plan §2: "Do not modify the bespoke
engine to force parity" and "Make only targeted changes needed for
CAMPAIGN_011").

## 7. Required disclosure

CAMPAIGN_011 remains **REJECT / null diagnostic anchor by design**.
The fixes here corroborate that REJECT verdict at trade-for-trade
precision; they do not approve any strategy, tune any parameter,
change any CAMPAIGN_011 rule, change the bespoke engine, or change
the no-RiskEngine bespoke reference JSONs.

`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked. `strategy_evidence: false`.

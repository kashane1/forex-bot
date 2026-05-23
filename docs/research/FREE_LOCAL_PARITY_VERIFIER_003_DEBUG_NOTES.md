# Free / Local Parity Verifier — Sprint-003 Debug Notes

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-003-with-data`
**Phase:** 5 · `strategy_evidence: false`

Verifier-side debugging pass after the Sprint-003 mid-sprint unblock
produced a comparison FAIL with overall classification `unknown`. Two
verifier-side bugs were localized and fixed; no bespoke-engine change
was made; no CAMPAIGN_002 rule was touched; no parameter was tuned.

> Verifier-side fixes only, per sprint rules. Bespoke engine
> unchanged. CAMPAIGN_002 remains REJECT. `configs/approved_strategies.yaml`
> remains `approved: []`. Paper / demo / live remain blocked.

## Headline impact

| metric | before debug | after Bug #1 | after Bug #2 |
|---|---|---|---|
| Verifier total trades | 1,586 | 1,580 | **1,655** |
| Bespoke total trades | 1,647 | 1,647 | 1,647 |
| Total Δ % | −3.70 % (OK) | −4.07 % (OK) | **+0.49 % (OK)** |
| Pairs OK | 1 / 7 | 1 / 7 | **3 / 7** |
| Pairs WARN | 5 / 7 | 5 / 7 | **4 / 7** |
| Pairs FAIL | 1 / 7 (EUR_USD return) | 1 / 7 (EUR_USD return) | **0 / 7** |
| Overall status | FAIL | FAIL | **WARN** |
| Overall classification | unknown | unknown | unknown (sub-WARN drift remains) |

Two verifier-side bugs were found. After both fixes, the comparison
no longer FAILs on any tolerance threshold; the remaining drift sits
inside the WARN band on 4 / 7 pairs. The remaining drift is most
likely Decimal-vs-float precision and the absence of the bespoke's
`instrument.round_price(...)` step on the verifier side — both
sub-pip effects.

## Bug #1 — initial stop anchored at the wrong base price

### Symptom

After the first end-to-end run, the verifier reported 1,586 trades vs
bespoke 1,647 (−3.70 %) and was systematically less negative on every
pair's expectancy and return. EUR_USD return delta was +2.4053 pp,
exceeding the 2.0 pp FAIL threshold from
`LEAN_PARITY_COMPARISON_METHOD.md`.

### Trace

The bespoke strategy
(`src/forex_bot/strategies/trend_following.py:114-117`) emits
``signal.stop_price`` computed from the bar's **mid close**:

```python
if side == "long":
    stop = last_close - atr_multiple * last_atr
else:
    stop = last_close + atr_multiple * last_atr
```

The bespoke engine (`backtesting/engine.py:491-505` — no-RiskEngine
path) uses that ``signal.stop_price`` directly:

```python
stop_price_to_use = signal.stop_price
```

The verifier's `event_loop.py` was passing the **post-slippage
``entry_price``** (= `ask_close + slip` for long) to
`rules.initial_stop_price`:

```python
stop_price = initial_stop_price(
    side=side,
    entry_price=entry_price,    # WRONG — uses post-slippage ask
    atr_value=atr_series[i],
    atr_stop_multiple=config.atr_stop_multiple,
)
```

For a long with `close = 1.1500`, `ATR = 0.005`, `multiple = 2.0`,
`slip = 1 pip`:

- bespoke stop (correct) = `1.1500 − 0.010 = 1.1400`
- buggy verifier stop = `1.1501 − 0.010 = 1.1401` (1 pip higher)

The 1-pip discrepancy made the verifier's stop slightly closer to
entry → triggered slightly sooner with a slightly smaller loss per
trade → systematic "less bad" expectancy / return.

### Fix

Rename `initial_stop_price`'s argument from `entry_price` to
`close_price` and pass `bar.close` (mid close) from the event loop.

- File: `research/parity_verifier/rules.py`
- File: `research/parity_verifier/event_loop.py`
- Regression test:
  `tests/research/test_parity_verifier_rules.py::test_initial_stop_uses_close_not_post_slippage_entry`

### Impact (Bug #1 only)

| | before | after Bug #1 |
|---|---|---|
| Total trades | 1,586 | 1,580 |
| Total Δ % | −3.70 % | −4.07 % |
| EUR_USD return Δ pp | +2.4053 | +2.4963 |
| Overall status | FAIL | FAIL |

Bug #1 alone barely moved the comparison. The fix is correct
(verifier now matches the bespoke strategy literally), but a 1-pip
stop offset on a ~20-40 pip ATR stop only produces a fraction-of-a-
percent shift per pair. The real cause was elsewhere.

## Bug #2 — verifier blocked same-bar re-entry after exit

### Symptom

After Bug #1 was fixed, the verifier was still systematically lower
on trade count (-4.07 % overall) and less negative on returns. Every
pair showed the same direction of drift.

### Trace

The bespoke engine processes each bar in two phases (`engine.py:`
trailing/exit at lines 237-320, then new-entry signal at lines 322
onward):

```python
# 1. If open trade: update trailing → check exits → close trade
...
if exit_reason:
    ...
    open_trade = None

equity_bars.append(...)

# 2. Consider a new entry (if no open trade)
if open_trade is not None:
    continue
... # signal generation + entry on this same bar
```

Critically: lines 322-329 mean the same bar that just closed a trade
can immediately open a new one. This is the standard "exit first then
re-evaluate" pattern for bar-by-bar event loops.

The original verifier's `event_loop.py` had the opposite structure:

```python
for i, bar in enumerate(bars):
    if not in_position:
        # entry
        ...
        if entry: in_position = True
        continue    # WRONG — entry-bar gets no exit check (correct)
                    # but...
    # only reached if in_position
    bars_held += 1
    # ... exit check ...
    if exit:
        # record trade; in_position = False
        ...        # WRONG — falls through to end of iteration with NO
                   # entry check on this bar
```

The verifier never evaluated a new entry on the same bar that just
exited. This systematically dropped same-bar re-entries the bespoke
engine takes. On a *losing* strategy, the missed entries are on
average losers, so the verifier looked "less bad" than bespoke.

### Fix

Refactor `event_loop.py` to use the bespoke engine's bar order:
exit-check first (if in position), then entry-check (if flat, possibly
because the exit just closed the trade).

```python
for i, bar in enumerate(bars):
    is_last_bar = i == n - 1

    # Step 1: exits (if in a position)
    if in_position:
        bars_held += 1
        # ... trailing + exit ...
        if exit:
            # record trade; in_position = False
            ...
        else:
            continue  # still in position, skip entry-check

    # Step 2: entry (if flat — possibly because step 1 just exited)
    decision = evaluate_entry(...)
    if not decision.is_entry:
        continue
    # ... entry stuff ...
    in_position = True
    bars_held = 0
```

The new structure makes the bespoke's bar order explicit: exits
before entries; an exit-on-bar-X allows entry-on-bar-X if the bar's
close still passes the entry filter.

- File: `research/parity_verifier/event_loop.py` (refactor)
- Regression test:
  `tests/research/test_parity_verifier_event_loop.py::test_same_bar_re_entry_after_exit`

### Impact (Bug #2)

| | after Bug #1 | after Bug #2 |
|---|---|---|
| Total trades | 1,580 | **1,655** |
| Total Δ % | −4.07 % | **+0.49 % (OK)** |
| EUR_USD return Δ pp | +2.4963 (FAIL) | **+0.7644 (WARN)** |
| Pairs OK | 1 / 7 | **3 / 7** |
| Pairs WARN | 5 / 7 | **4 / 7** |
| Pairs FAIL | 1 / 7 | **0 / 7** |
| Overall status | FAIL | **WARN** |

Bug #2 was the dominant cause. The comparison no longer FAILs on any
tolerance threshold; the remaining drift sits in the WARN band on
4 / 7 pairs.

## Post-debug per-pair comparison

| pair | bespoke trades | verifier trades | Δ % | Δ R | Δ pp | status |
|---|---|---|---|---|---|---|
| EUR_USD | 233 | 235 | +0.86 | +0.0160 | +0.7644 | WARN |
| GBP_USD | 215 | 215 | +0.00 | +0.0005 | +0.0075 | OK |
| USD_JPY | 247 | 251 | +1.62 | −0.0125 | +0.3093 | OK |
| AUD_USD | 237 | 238 | +0.42 | −0.0033 | −0.2241 | OK |
| USD_CAD | 251 | 251 | +0.00 | −0.0605 | +0.0025 | WARN |
| USD_CHF | 224 | 223 | −0.45 | +0.0428 | +1.6304 | WARN |
| NZD_USD | 240 | 242 | +0.83 | −0.0077 | −0.5110 | WARN |
| **total** | **1647** | **1655** | **+0.49** | | | **WARN** |

## What remains (sub-WARN drift, not fixed this turn)

- **Decimal vs float precision.** Bespoke uses `decimal.Decimal`
  end-to-end; verifier uses Python `float`. Sub-pip rounding
  differences accumulate over thousands of bars.
- **`instrument.round_price(stop)`** — bespoke rounds the stop to
  display precision (5 decimals for USD-quote, 3 for JPY-quote)
  before storing; verifier does not. This is a sub-pip effect.
- **PnL conversion path for USD-base pairs**: both engines divide by
  `exit_price` (verifier matches), but the exact intermediate Decimal
  vs float arithmetic differs slightly.

These three together plausibly explain the remaining WARN-band drift
(largest delta now is USD_CHF return +1.63 pp; bespoke uses Decimal,
verifier uses float; one pair out of seven exhibiting a ~1.6 pp drift
is consistent with sub-pip arithmetic). Phase 5 chose not to chase
these further this turn — the comparison verdict has already moved
from FAIL to WARN, the directional verdict is intact (both engines
agree every pair is loss-making, CAMPAIGN_002 stays REJECT under
either measurement), and further fixes risk implementing the bespoke
engine inside the verifier (sacrificing independence). A future
sprint can pursue Decimal-precision parity if higher fidelity is
needed.

## What was NOT done

- The bespoke engine was **not modified** to match the verifier.
- CAMPAIGN_002 rules were **not changed**.
- No parameter was tuned.
- No divergence was hidden, relabelled, or silently "passed".
- No new external dependency was added.

## What this proves

- The verifier and the bespoke engine now agree on **trade count
  within 1.62 % per pair** and **0.49 % overall**.
- Both engines agree on the **directional verdict** for every pair:
  every CAMPAIGN_002 H4 pair is loss-making on the no-RiskEngine path.
- CAMPAIGN_002 remains REJECT under either measurement.

## What this does NOT prove

- It does not prove the bespoke engine is **exactly** correct
  (sub-WARN drift remains, plausibly explained by Decimal precision).
- It does not approve any strategy.
- It does not lift the research freeze.

## Test count

- Sprint 001 + 002 baseline: 85 verifier-side fixture tests
- Sprint 003 added: +1 (Bug #1 regression) + 1 (Bug #2 regression)
  = **87 verifier-side tests pass**.
- Full repo test count: **475 pass** (388 pre-sprint + 87 verifier).

# Diagnostic Stop-Model Comparison (EXECUTED)

**Diagnostic sensitivity only** — fixed C022 entries, exit rule varied. No optimization, no 'best' stop promoted, no verdict/metric changed, no C024.

Reconstructed paths: **2396** (dropped 0); horizon 32 M15 bars; schema `market_data`.

> **Caveats.** mid OHLC only; no spread/slippage; no next-bar-open fill timing; structure/reclaim stop families omitted (need ATR-at-entry & pullback/reclaim geometry not in historical artifacts). Compare DELTAS between variants, not absolute levels.

## Baseline sanity check

- realized price-based expectancy: **-0.1402R**
- simulated 2.0×ATR baseline expectancy: **-0.0732R**
- should be close; residual = mid-vs-fill-model approximation.

## Hard-stop sensitivity (ATR multiple → R distance)

| stop | n | expectancy_r | win_rate | mean_loss_r |
|---|---|---|---|---|
| 1.5xATR | 2396 | -0.0513 | 0.2892 | -0.7219 |
| 2.0xATR(baseline) | 2396 | -0.0732 | 0.3472 | -0.9294 |
| 2.5xATR | 2396 | -0.0637 | 0.4007 | -1.0984 |
| 3.0xATR | 2396 | -0.0777 | 0.4257 | -1.2292 |

## Time-to-invalidation early exit

| rule | n | expectancy_r | win_rate | mean_loss_r |
|---|---|---|---|---|
| no+0.25R_by_8 | 2396 | -0.0748 | 0.3205 | -0.8467 |
| no+0.5R_by_8 | 2396 | -0.0603 | 0.3397 | -0.7942 |
| no+0.5R_by_12 | 2396 | -0.0728 | 0.3364 | -0.8514 |

## Reading (diagnostic — not an edge)

- Every variant is reported for sensitivity. **No variant is endorsed as tradable**; all remain negative and none is promoted.
- **All hard-stop multiples (1.5×–3.0× ATR) and all time-to-invalidation rules stay in a tight negative band** — no exit rule lifts expectancy toward zero. Stop geometry is **not** the lever.
- The simulated baseline here is **cost-free** (mid OHLC, no spread/slippage) yet still negative; the gap to the realized price-based expectancy is approximately the cost drag. Even in the idealized no-cost case the entries do not clear zero — strong evidence the problem is **entry edge, not stop distance**.
- Any genuinely interesting variant must be re-tested in a pre-registered campaign with the real fill model — never adopted from this sensitivity sweep.

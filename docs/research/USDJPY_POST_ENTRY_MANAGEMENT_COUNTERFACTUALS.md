# USD_JPY Post-Entry Management — Diagnostic Counterfactuals

**Status:** read-only, DIAGNOSTIC ONLY. No verdict change, no approval, no tuning, no C024, no rule adopted. USD_JPY-only.

> **Optimistic caveat.** OPTIMISTIC counterfactuals: assume perfect action at the bar, mid open marks (no spread/slippage on the early exit), and do not net out the entry-edge problem. NOT tradable; no rule adopted; no verdict changed. Exit timing: next-bar-open after the horizon.

## Predeclared exit rules (fixed event + horizon, not mined)

| rule | split | n | affected | realized mean R | counterfactual mean R | Δ expectancy R | stops exited early | winners cut | winner R lost |
|---|---|---|---|---|---|---|---|---|---|
| early_reclaim_failure@h2 | train | 133 | 53 | -0.00172 | -0.13533 | -0.13362 | 36 | 16 | 4.502 |
| early_reclaim_failure@h2 | validation | 173 | 54 | 0.0004 | -0.11139 | -0.11178 | 42 | 12 | 3.4249 |
| early_reclaim_failure@h4 | train | 133 | 60 | -0.00172 | -0.10017 | -0.09846 | 39 | 20 | 0.7248 |
| early_reclaim_failure@h4 | validation | 173 | 57 | 0.0004 | -0.09009 | -0.09049 | 37 | 16 | 0.8703 |
| early_adverse_expansion@h2 | train | 133 | 28 | -0.00172 | -0.09262 | -0.0909 | 20 | 7 | 2.8464 |
| early_adverse_expansion@h2 | validation | 173 | 36 | 0.0004 | -0.07672 | -0.07711 | 27 | 8 | 1.6816 |
| no_continuation@h4 | train | 133 | 43 | -0.00172 | -0.10795 | -0.10623 | 25 | 17 | 3.9453 |
| no_continuation@h4 | validation | 173 | 39 | 0.0004 | -0.06507 | -0.06546 | 26 | 11 | 0.6015 |
| trap_or_failed_breakout@h2 | train | 133 | 48 | -0.00172 | -0.12532 | -0.1236 | 31 | 16 | 4.502 |
| trap_or_failed_breakout@h2 | validation | 173 | 49 | 0.0004 | -0.10582 | -0.10621 | 40 | 9 | 2.7939 |

## Reading (honest)

- Any rule with a **positive** expectancy delta on **both** splits: **False**.
- Even a positive delta here is an **upper bound**: it assumes perfect, cost-free action at the bar and ignores the entry-edge problem already documented. A rule that only helps because it cuts trades to a mid mark is not a demonstrated tradable edge.
- **Winner damage** (winners cut, winner R lost) is the cost of acting on an exit signal; weigh it against stops exited early. A rule that saves stop losses but forfeits comparable winner R is not net-useful.
- No rule is adopted; no threshold is a parameter; this is input to the readiness decision only.

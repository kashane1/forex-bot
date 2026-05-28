# USD_JPY Post-Entry Trade-Management Diagnostic — Result

**Status:** read-only diagnostic. No verdict change, no approval, no tuning, no C024, no campaign, no edge claim. USD_JPY-only. Post-entry events are TRADE-MANAGEMENT diagnostics, never entry alpha; nothing here is a tradable rule.

## Setup

- USD_JPY trades: 306 (train 133, validation 173); realized mean R {'train': -0.001717, 'validation': 0.000396}; overall hard-stop rate 0.5621.
- Each event is evaluated **only on trades still open at the horizon** (the only trades a management decision could act on), present vs absent, per split.
- 'Stable' = same-signed lift on train & validation with ≥ 25 per subgroup. Horizons are the fixed 2/4/8/16 M15 bars; no threshold is tuned.

## Headline

Candidate stable live-manageable signals — EXIT-type: ['early_reclaim_failure', 'no_continuation', 'early_adverse_expansion', 'trap_or_failed_breakout']; HOLD-type: ['early_retest_hold', 'early_favorable_displacement', 'reached_plus_025', 'reached_plus_05']. Treat as hypothesis-generating only; winner damage and optimistic-counterfactual caveats apply (Phase 4).

## EXIT-type events (present → expect worse outcome)

### early_reclaim_failure (live_manageable)

| horizon | n present (tr/va) | hard-stop lift (tr/va) | win-rate lift (tr/va) | winner-damage win-rate (tr/va) | stable? |
|---|---|---|---|---|---|
| 2 | 53/54 | 0.1939/0.4259 | -0.1393/-0.3148 | 0.3019/0.2222 | yes |
| 4 | 60/57 | 0.2349/0.338 | -0.1573/-0.3193 | 0.3333/0.2807 | yes |
| 8 | 57/60 | 0.2661/0.3962 | -0.1447/-0.3398 | 0.4386/0.3833 | yes |
| 16 | 52/72 | 0.1966/0.2311 | -0.0876/-0.2652 | 0.6346/0.5833 | no |

### no_continuation (live_manageable)

| horizon | n present (tr/va) | hard-stop lift (tr/va) | win-rate lift (tr/va) | winner-damage win-rate (tr/va) | stable? |
|---|---|---|---|---|---|
| 2 | 62/67 | 0.0213/0.2778 | 0.0142/-0.2024 | 0.3871/0.3134 | no |
| 4 | 43/39 | 0.0671/0.3056 | -0.019/-0.2642 | 0.3953/0.2821 | yes |
| 8 | 21/13 | 0.1686/0.2171 | -0.0853/-0.1958 | 0.4286/0.3846 | no |
| 16 | 8/4 | 0.2742/0.552 | -0.1774/-0.4332 | 0.5/0.25 | no |

### early_adverse_expansion (live_manageable)

| horizon | n present (tr/va) | hard-stop lift (tr/va) | win-rate lift (tr/va) | winner-damage win-rate (tr/va) | stable? |
|---|---|---|---|---|---|
| 2 | 28/36 | 0.1874/0.3294 | -0.1694/-0.2699 | 0.25/0.2222 | yes |
| 4 | 33/35 | 0.222/0.3947 | -0.1898/-0.325 | 0.2727/0.2286 | yes |
| 8 | 25/24 | 0.1629/0.2962 | -0.1294/-0.2806 | 0.4/0.3333 | no |
| 16 | 16/15 | 0.0718/0.1333 | -0.0417/-0.1556 | 0.625/0.5333 | no |

### range_compression_after_entry (live_manageable)

| horizon | n present (tr/va) | hard-stop lift (tr/va) | win-rate lift (tr/va) | winner-damage win-rate (tr/va) | stable? |
|---|---|---|---|---|---|
| 2 | 116/137 | 0.1776/0.0636 | -0.0207/-0.1039 | 0.3793/0.4161 | no |
| 4 | 84/97 | 0.0304/-0.027 | 0.0374/-0.0361 | 0.4167/0.4639 | no |
| 8 | 33/41 | 0.1622/-0.0763 | -0.1561/0.0378 | 0.3939/0.5854 | no |
| 16 | 4/5 | -0.0076/-0.02 | 0.0985/-0.07 | 0.75/0.6 | no |

### trap_or_failed_breakout (live_manageable)

| horizon | n present (tr/va) | hard-stop lift (tr/va) | win-rate lift (tr/va) | winner-damage win-rate (tr/va) | stable? |
|---|---|---|---|---|---|
| all | 48/49 | 0.1253/0.4623 | -0.0777/-0.3561 | 0.3333/0.1837 | yes |

## HOLD-type events (present → expect better outcome)

### early_retest_hold (live_manageable)

| horizon | n present (tr/va) | hard-stop lift (tr/va) | win-rate lift (tr/va) | winner-damage win-rate (tr/va) | stable? |
|---|---|---|---|---|---|
| 2 | 64/95 | -0.116/-0.1251 | 0.0886/0.126 | 0.4219/0.4842 | yes |
| 4 | 79/104 | -0.0272/-0.0324 | 0.0353/0.0157 | 0.4177/0.4808 | yes |
| 8 | 79/108 | 0.0986/-0.0103 | -0.0904/0.0354 | 0.481/0.5648 | no |
| 16 | 67/100 | -0.0796/0.23 | -0.01/-0.35 | 0.6567/0.65 | no |

### early_favorable_displacement (live_manageable)

| horizon | n present (tr/va) | hard-stop lift (tr/va) | win-rate lift (tr/va) | winner-damage win-rate (tr/va) | stable? |
|---|---|---|---|---|---|
| 2 | 56/86 | -0.031/-0.2595 | 0.0237/0.1944 | 0.3929/0.5233 | yes |
| 4 | 61/85 | -0.14/-0.2394 | 0.1128/0.2099 | 0.459/0.5647 | yes |
| 8 | 51/78 | -0.2815/-0.233 | 0.2072/0.2495 | 0.5882/0.6538 | yes |
| 16 | 42/59 | -0.2857/-0.2679 | 0.2024/0.2966 | 0.7381/0.7966 | yes |

### reached_plus_025 (live_manageable)

| horizon | n present (tr/va) | hard-stop lift (tr/va) | win-rate lift (tr/va) | winner-damage win-rate (tr/va) | stable? |
|---|---|---|---|---|---|
| 2 | 59/95 | -0.0213/-0.2778 | -0.0142/0.2024 | 0.3729/0.5158 | no |
| 4 | 70/108 | -0.0671/-0.3056 | 0.019/0.2642 | 0.4143/0.5463 | yes |
| 8 | 72/112 | -0.1686/-0.2171 | 0.0853/0.1958 | 0.5139/0.5804 | no |
| 16 | 62/101 | -0.2742/-0.552 | 0.1774/0.4332 | 0.6774/0.6832 | no |

### reached_plus_05 (live_manageable)

| horizon | n present (tr/va) | hard-stop lift (tr/va) | win-rate lift (tr/va) | winner-damage win-rate (tr/va) | stable? |
|---|---|---|---|---|---|
| 2 | 29/60 | -0.0244/-0.1225 | 0.0442/0.1343 | 0.4138/0.5167 | yes |
| 4 | 42/70 | -0.2528/-0.1078 | 0.1858/0.1273 | 0.5238/0.5429 | yes |
| 8 | 52/81 | -0.2585/-0.1355 | 0.2303/0.2329 | 0.5962/0.642 | yes |
| 16 | 56/90 | -0.3036/-0.2111 | 0.2857/0.2333 | 0.7143/0.7 | no |

## Hindsight-only references (UNUSABLE for live management)

Full-path fields (e.g. realized MAE at exit, full time-to-threshold) often separate outcomes strongly, but they are only knowable at/after exit and **cannot** drive a live management decision. They are excluded from the usefulness verdict by construction.

## Reading (honest)

- **Restricted to still-open trades.** A management signal only matters for trades not already closed at the horizon; the tables reflect that subset.
- **Winner damage.** For EXIT-type signals, the 'winner-damage win-rate' is the share of flagged (would-exit) trades that were actually winners — early-exiting them forfeits those wins. A high value means the signal cuts winners.
- **Optimistic counterfactuals.** Any apparent gain is upper-bounded; the Phase 4 counterfactual (if run) assumes perfect action at the bar and ignores execution cost. Nothing here is tradable, and no threshold is a parameter.

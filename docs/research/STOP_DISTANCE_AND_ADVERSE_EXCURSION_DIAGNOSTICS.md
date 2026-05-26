# Stop Distance and Adverse Excursion Diagnostics

**Date:** 2026-05-26  
**Branch:** `research-stop-and-exit-diagnostics-001`  
**Artifact:** [`research/exit_diagnostics/stop_distance_adverse_excursion.json`](../../research/exit_diagnostics/stop_distance_adverse_excursion.json)

> **Diagnostic only** — `strategy_evidence: false`. **No alternate stop distances tested.** Descriptive MAE/MFE from existing H4 deduped candles.

---

## MAE/MFE status

| item | status |
|---|---|
| MAE/MFE computed | **yes** |
| method | H4 deduped candles between `entry_time` and `exit_time`; R normalized by entry–stop distance |
| campaigns covered | C008 (823 trades), C009 (403 trades) |
| other campaigns | not computed — would require per-campaign candle joins; C008/C009 were sprint focus |

---

## Stop distance (descriptive)

| campaign | median stop distance (pips) |
|---|---:|
| C008 | 45.5 |
| C009 | 45.25 |

Stop placement is **unchanged** between C008 and C009 (same entry/stop rules). No optimization performed.

---

## C008 MAE/MFE

| bucket | count | median MAE (R) | median MFE (R) |
|---|---:|---:|---:|
| stop exits | 559 | 1.17 | 1.10 |
| time exits | 263 | 0.50 | **3.33** |

### Stop exits — favorable excursion before stop

| metric | value |
|---|---:|
| % reaching ≥1R favorable before stop | **58.9%** |
| % never reaching 1R favorable | **41.1%** |

**Interpretation (descriptive, not prescriptive):**

- **~41%** of stop exits never saw 1R favorable move — consistent with **invalid or mistimed entries** relative to the thesis.
- **~59%** saw ≥1R favorable then still stopped — consistent with **stop too tight vs noise**, **reversal after partial reversion**, or **correct invalidation after failed continuation**. Cannot distinguish without a pre-registered alternative stop rule (forbidden this sprint).

Time-exit survivors had **low median MAE (0.50R)** and **high median MFE (3.33R)** — trades that avoided the stop experienced substantial favorable drift before the 40-bar close.

### By split (stop MFE / time MFE medians)

| split | stop MFE | time MFE |
|---|---:|---:|
| train | 1.10 | 3.28 |
| validation | 1.15 | 3.33 |
| full | 1.09 | 3.36 |

Pattern is **stable across splits** — not validation-only MFE inflation.

---

## C009 MAE/MFE

| bucket | count | median MAE (R) | median MFE (R) |
|---|---:|---:|---:|
| stop exits | 227 | 1.17 | 1.04 |
| target exits | 165 | — | **1.83** |
| time exits | 10 | 0.63 | 1.65 |

| metric | C009 stop |
|---|---:|
| % reaching ≥1R before stop | 53.3% |
| % never 1R favorable | 46.7% |

Target exits **cap MFE near ~1.83R** vs C008 time-exit median MFE **3.33R** — quantifies the **winner capping** effect of midline target.

---

## Question 2 answer: tight, badly placed, or bad entries?

**Mixed — all three mechanisms appear in the data, without retuning:**

| mechanism | evidence |
|---|---|
| Bad entries | ~41–47% of stops never reach 1R favorable |
| Stop vs noise / reversal | ~53–59% reach 1R favorable then stop at −1R |
| Exit structure (time vs target) | C008 time exits capture higher MFE tail than C009 targets |

Hard stops are **not purely** "too tight" nor purely "bad entries" — both populations exist at similar scale.

---

## Rules observed

- No alternate stop distances tested.
- No stop multiple optimization.
- No new stop value recommended from winners.
- Descriptive only.

# C008/C009 Exit Forensics

**Date:** 2026-05-26  
**Branch:** `research-stop-and-exit-diagnostics-001`  
**Artifact:** [`research/exit_diagnostics/c008_c009_exit_forensics.json`](../../research/exit_diagnostics/c008_c009_exit_forensics.json)

> **Diagnostic only** — `strategy_evidence: false`. C008/C009 remain **REJECT / research-only**. Evidence **LIKELY_CONTAMINATED**.

---

## C008 train vs validation

### Hard stops (exit_reason = stop)

| split | count | exp R | median R | avg bars | avg spread pips |
|---|---:|---:|---:|---:|---:|
| train | 153 | −0.802 | −1.0 | 10.3 | 1.58 |
| validation | 88 | −0.785 | −1.0 | 10.0 | 1.55 |

Stop outcomes are **nearly identical** across splits — not a validation-only artifact.

### Time exits (40-bar)

| split | count | exp R | median R | avg bars | avg spread pips |
|---|---:|---:|---:|---:|---:|
| train | 62 | +1.894 | +1.131 | 40.0 | 1.49 |
| validation | 50 | +1.827 | +1.410 | 40.0 | 1.57 |
| validation winners | 44 | +2.106 | +1.689 | 40.0 | 1.56 |

Time exits are **positive in both splits**. Validation winners are 100% time exits (44/44 winners); train has 62 time exits vs 153 stops.

### Pair distribution (stops vs time)

Stops and time exits are **spread across all six pairs** — no single pair explains the split:

- Train stops: USD_CAD (34), AUD_USD (28), GBP_USD (25), EUR_USD (24), USD_JPY (24), USD_CHF (18)
- Train time: AUD_USD (15), USD_JPY (13), GBP_USD (12), EUR_USD (11), USD_CAD (7), USD_CHF (4)
- Validation stops/time: similar broad distribution

### Session distribution

| session | train stops | train time | val stops | val time |
|---|---:|---:|---:|---:|
| asia | 54 | 25 | 17 | 9 |
| london | 47 | 21 | 25 | 19 |
| london_ny_overlap | 51 | 16 | 40 | 17 |
| ny | 1 | 0 | 6 | 5 |

No single session owns the pathology; **asia + london + overlap** all contribute stops and time exits.

### Spread

Average spread ~1.49–1.58 pips across stop and time buckets — **does not explain** train/validation or stop/time split (consistent with C008 post-mortem).

---

## C009 vs C008

### Exit mix shift

| | C008 (all baseline) | C009 (all) |
|---|---:|---:|
| stop share | 68% | 56% |
| time share | 32% | 2% |
| target share | — | 41% |

C009 **eliminated** most 40-bar time exits by hitting midline target first (~10.5 bars avg vs 40 bars).

### Train C009 by exit

| exit | share | exp R |
|---|---:|---:|
| stop | 60% | −0.799 |
| target | 38% | +1.159 |
| time | 1% | +0.629 |
| **overall** | — | **−0.025** |

### Validation C009 by exit

| exit | share | exp R |
|---|---:|---:|
| stop | 50% | −0.768 |
| target | 45% | +1.214 |
| time | 5% | +0.557 |
| **overall** | — | **+0.186** |

Validation looks better than train but **train gate failed** (−0.025R vs ≥0 required). Target exits are 100% winners but **lower expectancy** than C008 time exits (+1.18R vs +1.83R validation time).

---

## Forensic conclusions

### Did time exits win because trades eventually reverted after long holding?

**Partially yes, descriptively.** All C008 time exits held exactly 40 bars. MAE/MFE analysis (Phase 4) shows time-exit trades had **median MFE ~3.3R** vs stop exits **median MFE ~1.1R** before exit — survivors experienced large favorable excursion consistent with delayed mean reversion, then closed at bar 40 rather than at a structural target.

### Were hard stops clustered in one pair/session/regime?

**No single cluster.** Stops are broad-based across pairs and sessions. Regime/confluence joins were available in C008 post-mortem but did not isolate a clean pre-trade filter without retuning (see post-mortem docs).

### Did C009 midline target cap trades C008 would have held to time exit?

**Yes.** C009 validation: only 7 time exits vs C008 validation 50 time exits. Target exits (+1.21R) replace higher-tail C008 time exits (+1.83R). Train overall worsened.

### Did the 40-bar time stop act like implicit profit capture?

**Yes, descriptively** — it functions as a **holding-period exit** that realizes mean-reversion drift for trades that survive initial adverse movement. It is not a take-profit rule; winners at bar 40 had high MFE (median 3.3R) but closed at ~+1.4–1.9R realized.

### Was train/validation split mostly regime-dependent?

**Not clearly from exit forensics alone.** Stop/time mechanics replicate across splits with similar spread. Validation's positive overall in C008 post-mortem came from **more time exits relative to stops** in that window, not from a single regime bucket — but **contamination** prevents treating validation as clean OOS.

---

## Evidence caveats

- C008/C009 artifacts **LIKELY_CONTAMINATED** — findings are explanatory, not promotable.
- Test lockbox **not opened**.
- Financing on 40-bar holds **not modeled**.
- No retuning performed in this sprint.

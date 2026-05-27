# Exit Hypothesis Selection Memo

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-001`

> **Precommit only** — `strategy_evidence: false`. Selects one hypothesis; does not authorize execution.

---

## Question answered

What is the single cleanest exit hypothesis worth testing next on frozen mean-reversion entries?

---

## Candidates considered

| ID | hypothesis | verdict |
|---|---|---|
| A7 | Protective / break-even stop after +1R favorable excursion | **SELECTED** |
| A1 | Volatility-scaled stop redesign (new ATR multiplier) | rejected |
| A2 | Regime-dependent time stop (FRED buckets) | rejected |
| A3 | Counter-signal exit (opposite-band / RSI recross) | rejected |
| A4 | ATR trail after favorable excursion | rejected |
| A5 | Partial exit at midline + runner bundle | rejected |
| A6 | No-target invalidation-only (C008-equivalent) | rejected |
| — | C009 midline target revival | forbidden |

---

## Why each rejected candidate was rejected

### A1 — Volatility-scaled stop redesign

Changes the **initial hard-stop distance**. C008 already uses 1.5× ATR-14 pre-committed for range MR. Reselecting a multiplier from MAE distributions would resemble stop retuning. Does not directly test the **favorable-then-stopped** population without also changing entry-risk geometry.

### A2 — Regime-dependent time stop

Requires pre-declaring FRED regime buckets and multiple time-stop lengths. Adds confounds (regime labeling + hold period) and makes it harder to attribute results to a single exit mechanism. Financing modeling becomes mandatory before fair comparison — a parallel blocker sprint, not the cleanest first exit test.

### A3 — Counter-signal exit

Valid future hypothesis but addresses **thesis invalidation**, not **giveback after favorable move**. Deduped evidence shows ~40% of stops never reached 1R (likely bad entries); counter-signal may help that bucket but does not target the ~60% that reached ≥1R then stopped at −1R.

### A4 — ATR trail after favorable excursion

Similar intent to A7 but introduces **trail offset** and **ATR multiple for trail** — two additional parameters. Higher overfit surface. A7 uses the objective 1R unit already defined by entry stop distance.

### A5 — Partial exit + runner bundle

C009 already tested the **midline partial leg** and falsified it (target caps tail at ~1.18R vs C008 time MFE ~3.29R). A bundle with midline partial is contaminated by prior falsification. Runner-only without partial is closer to A6/A7.

### A6 — No-target invalidation-only

**Is C008.** No new exit information. C008 deduped replay already established train-fail / validation-positive shape with 40-bar time exit and 1.5× ATR stop.

### C009 midline target

**Forbidden.** Deduped replay confirmed target exits cap winner tail. Not a rescue path.

---

## Selected hypothesis

**Label:** `delayed_reversion_protective_stop_after_1R`  
**Catalog reference:** [`FUTURE_EXIT_RESEARCH_HYPOTHESES.md`](FUTURE_EXIT_RESEARCH_HYPOTHESES.md) §A7

### Thesis

Mean-reversion trades on frozen C008 entries that reach **≥ +1.0R favorable excursion** (MFE measured in initial-risk units) but later stop out at the original hard stop may contain **delayed-reversion edge that is being surrendered**. Moving the stop to **break-even (entry price)** once +1R is reached may:

1. Convert some −1R stop-outs into ~0R exits (reducing hard-stop churn on the favorable-then-stopped population).
2. Preserve the **no-target / time-exit tail** that C008 time exits exploit (median time MFE ~3.29R on deduped replay).
3. Avoid C009's failure mode (fixed midline target capping winners at ~1.18R).

### Why it follows from deduped evidence

| finding | implication |
|---|---|
| C008: 68% stop / 32% time; time exp +1.86R | Delayed reversion exists; hard stops dominate PnL |
| C008 time MFE median 3.29R | Tail is real; must not cap with fixed target |
| 60.17% of C008 stops reached ≥1R before stopping | Large sub-population where protective transition is relevant |
| 39.83% never reached 1R | Bad-entry bucket unchanged by this rule (still stops at initial hard stop) |
| C009 target ~41% at +1.18R exp | Fixed target path falsified; protective stop is not a target |
| Train −0.025R / val +0.161R on deduped C008 | Exit change may address train failure without reopening C008 as-is |

### Why it is not a C008/C009 retune

| dimension | C008/C009 | this hypothesis |
|---|---|---|
| Campaign ID | CAMPAIGN_008 / 009 | **new CAMPAIGN_018** |
| Strategy version | 0.1.0-c008 / 0.2.0-c009 | **0.1.0-c018** (new) |
| Entry rules | frozen | **identical to C008** — no change |
| Initial stop | 1.5× ATR-14 | **unchanged** |
| Time stop | 40 bars | **unchanged** |
| Profit target | none / midline (C009) | **none** — explicitly no target |
| Exit change | — | **one new rule:** break-even stop after +1R MFE |
| +1R threshold | — | **objective R-multiple** tied to entry stop distance; not swept from MAE percentiles |

This is a **new exit mechanism** on frozen entries, not a parameter sweep of C008 stop distance, time-stop length, or C009 midline level.

---

## What would falsify it

1. **Train expectancy still < 0** after deduped run with financing modeled — same gate failure as C008/C009.
2. **Protective-stop exits dominate** but combined expectancy ≤ C011 deduped null (WITHIN_NULL).
3. **Time-exit share collapses** and winner tail MFE drops toward C009 target levels (~1.8R) — protective rule effectively caps reversion without improving train.
4. **Validation uplift vs C008 deduped baseline** does not survive **2× cost stress**.
5. **Per-pair robustness fails** — edge concentrated in one pair/session discovered only post-hoc.
6. **Stop-transition rate ≈ 0** in implementation — rule inert; hypothesis not testable.

---

## What would support further research (still not approval)

1. **Train expectancy ≥ 0** with **validation expectancy > 0**, PF ≥ 1.05, ≥ 2 pairs positive — passes screening gate (first time for MR family on deduped path).
2. **Beat-null** vs C011 deduped on validation (expectancy materially above −0.003R with adequate trades).
3. **Hard-stop share decreases** vs C008 deduped without collapsing time-exit tail MFE below ~2R median.
4. **Protective/break-even exit bucket** shows neutral-to-positive expectancy; time-exit bucket retains positive expectancy.
5. **2× cost stress** validation expectancy ≥ 0.
6. **Financing overlay** does not flip validation negative under conservative assumptions.

Even if all above hold: verdict ceiling remains **REVISE / research-only** (mean-reversion tail risk). Separate human promotion review required. **No automatic approval.**

---

## Why this still cannot approve anything

- Mean-reversion tail risk and financing remain structural blockers.
- Test lockbox unopened until screening passes.
- `configs/approved_strategies.yaml` stays empty.
- Broad strategy search remains paused.
- Precommit ≠ evidence; only a future **executed** campaign with passed gates could justify further review — not this sprint.

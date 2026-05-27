# Exit Hypothesis Precommit 002 — Selection Memo

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-002`  
**Evidence class:** `precommit_design_only` — `strategy_evidence: false`

---

## Question 1: Should there be another exit hypothesis?

**Yes — one more, narrowly scoped.**

C018 falsified profit-triggered +1R break-even protection but did **not** test
thesis-invalidation exits. Stop diagnostics show **41–47%** of hard stops never reached
+1R favorable — a distinct failure mode C018 could not address. Backtrader parity is
hardened; exit mechanism research can proceed under a **new campaign ID** with frozen
C008 entries.

Financing remains unresolved but **does not block** a single pre-registered exit test —
overlay is mandatory at execution interpretation, not at precommit.

---

## Candidates considered

| ID | hypothesis | verdict |
|---|---|---|
| **B1** | Z-score continuation thesis-invalidation exit | **SELECTED** |
| B2 | Early failure-to-revert (no MFE within fixed window) | rejected |
| B3 | Delayed ATR trail after +2R favorable excursion | rejected |
| B4 | Counter-signal RSI recross exit | rejected |
| B5 | Regime-dependent time compression (FRED) | rejected |
| B6 | C008-equivalent (no new exit rule) | rejected |
| B7 | No further exit hypothesis | rejected |
| — | C018 +1R break-even threshold change | **forbidden** |
| — | C009 midline target revival | **forbidden** |

---

## Rejected candidates — why

### B2 — Early failure-to-revert window

Exit if MFE < +0.25R by bar 8 (example). Requires choosing MFE floor and window length
— parameters not structurally fixed by entry logic. High retune/overfit surface; overlaps
with time-stop retuning.

### B3 — Delayed trail after +2R

Still **profit-triggered** like C018. Different threshold is a retune, not a new mechanism
family. Precommit 001 already rejected A4 (ATR trail after excursion) for parameter surface.

### B4 — RSI recross exit

Valid invalidation concept but RSI midline (50) is ambiguous for MR — could exit **winners**
entering reversion. Z-score continuation is **aligned with entry indicator** and directionally
unambiguous (further extension = thesis failure).

### B5 — Regime-dependent time compression

FRED confound + financing complexity. Rejected in precommit 001 (A2); unchanged.

### B6 — C008-equivalent

No new information. C008 already REJECT on train.

### B7 — No further exit hypothesis

Conservative but premature: invalidation bucket untested; parity lane now viable for
independent confirmation. One structurally distinct hypothesis remains defensible.

### C018 threshold retune / C009 target

Explicitly forbidden by sprint rules and prior falsification.

---

## Selected hypothesis

**Label:** `thesis_invalidation_zscore_continuation_exit`  
**Catalog reference:** [`FUTURE_EXIT_RESEARCH_HYPOTHESES.md`](FUTURE_EXIT_RESEARCH_HYPOTHESES.md) §A3
(refined — z-score continuation, not RSI recross)

### Thesis

On frozen C008 mean-reversion entries, **~41–47%** of hard stops occur without ever
reaching +1R favorable excursion — trades where the reversion thesis **never engaged** or
**continued extending against the position**. Exit early when the **same z-score indicator
that triggered entry** shows structural continuation failure (price moving further from
mean beyond the entry band), rather than waiting for full −1R hard stop or profit-triggered
protection.

This targets the **invalidation bucket** C018 did not address. C018 targeted the **giveback
bucket** (≥+1R then stopped) and failed train.

### Exact rule (precommit)

While trade is open, at each completed H4 bar close, compute z-score of close over
**20 bars** (same as entry). If continuation invalidation triggers, exit at bar close with
reason `thesis_invalidation`:

| side | entry condition (frozen C008) | invalidation exit |
|---|---|---|
| long | z ≤ −2.0 | z ≤ **−3.0** |
| short | z ≥ +2.0 | z ≥ **+3.0** |

The ±3.0 threshold is **not** optimized from validation or MAE distributions — it is the
**next integer z-band unit** beyond the ±2.0 entry threshold (one structural sigma step),
pre-declared before any CAMPAIGN_019 run.

Processing order per bar: thesis_invalidation → hard stop → time stop. No profit target.
No protective stop. No trailing ratchet.

---

## Why it follows from deduped + Backtrader-confirmed evidence

| finding | implication |
|---|---|
| 41–47% stops never +1R favorable | Thesis-invalidation exit targets this bucket directly |
| C018 +1R break-even failed train | Profit-triggered protection closed for next test |
| C008 time exit MFE ~3.29R | Tail preserved when not stopped early — invalidation should fire only on continuation, not on reversion |
| C009 target ~1.18R cap falsified | No fixed profit target in C019 |
| BT parity ±1 trade, CLOSE_MATCH exits | Future C019 exits independently verifiable |

---

## Why it is not a retune of C008/C009/C018

| dimension | C008 | C009 | C018 | C019 (proposed) |
|---|---|---|---|---|
| Entry | frozen MR | same + midline target | same, no target | **same as C008** |
| Initial stop | 1.5× ATR | same | same | **same** |
| Time stop | 40 bars | same | same | **same** |
| Profit target | none | midline | none | **none** |
| Extra exit | — | target | +1R break-even | **z ≤ −3 / z ≥ +3 invalidation** |

C019 adds **one thesis-failure exit** triggered by **adverse indicator continuation**, not
by favorable PnL, not by target level, not by stop/time parameter change.

---

## What would falsify it

1. **Train expectancy < 0** (primary — same bar as C008/C009/C018).
2. **Thesis_invalidation exit rate < 5%** — rule inert, not testable.
3. **Thesis_invalidation exit rate > 45%** — mostly re-labeling hard stops without train improvement.
4. **Train exp worse than C008 deduped** (−0.025 R) — mechanism harmful vs baseline.
5. **Time-exit median MFE < 2.0R** — tail collapsed vs C008 (~3.29R).
6. **WITHIN_NULL** vs C011 deduped on validation.
7. **Financing overlay** flips validation net exp ≤ 0.
8. **Backtrader parity** trade-count gap > ±1 or exit shares MATERIAL_DIVERGENCE post-execution.

---

## What would support further research (not approval)

- Train exp ≥ 0 with thesis_invalidation rate 10–35%
- Validation exp > 0 with ≥ 2 pairs positive
- Train improvement vs C008 without collapsing time-exit tail
- Beat-null vs C011; 2× stress validation pass
- Backtrader parity within ±1 trade

Maximum status even if all pass: **RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED** — never
approval from this lane alone.

---

## Why this still cannot approve anything

- Mean-reversion family remains REJECT across C008/C009/C018
- Financing observed path paused; synthetic drag material on 40-bar holds
- Broad strategy search paused
- Precommit docs only — zero execution evidence for C019
- `configs/approved_strategies.yaml` stays empty

# Backtrader Exit Parity — Divergence Analysis

**Branch:** `infra-backtrader-exit-parity-diagnostics-001`  
**Date:** 2026-05-27  
**Evidence class:** `parity_diagnostic_only` — `strategy_evidence: false`

---

## Summary

Backtrader **1.9.78.123** ran successfully on deduped H4 data. Exit-reason **share distributions** closely match bespoke deduped forensic replay for all three campaigns. **Trade counts** diverge materially (~20–25% fewer trades in the Backtrader lane), pointing to an **entry / risk-engine / bar-index pipeline gap**, not an exit-precedence bug.

**No campaign verdicts changed.**

---

## Classification by campaign

| Campaign | Trade count | Exit share distribution | Overall |
|---|---|---|---|
| **C008** | MATERIAL_DIVERGENCE (−75 aggregate) | CLOSE_MATCH (max Δ 3.3 pp) | Mixed |
| **C009** | MATERIAL_DIVERGENCE (−71 aggregate) | CLOSE_MATCH (max Δ 1.8 pp) | Mixed |
| **C018** | MATERIAL_DIVERGENCE (−704 vs full bespoke; −39 train / −25 val per split) | CLOSE_MATCH (max Δ 2.5 pp) | Mixed |

Per-split detail: [`research/backtrader_exit_parity/exit_reason_comparison.csv`](../../research/backtrader_exit_parity/exit_reason_comparison.csv)

---

## Primary questions answered

### 1. C008 stop/time-exit split reproduced?

**Yes (distribution).** Bespoke train: 71% stop / 29% time. Backtrader train: 74% stop / 25% time. Validation bespoke: 64%/36%; Backtrader: 63%/37%. Sign split persists; stop expectancy ≈ −1R, time expectancy strongly positive in both engines.

### 2. C009 target/winner-capping reproduced?

**Yes (distribution).** Target share train: 38% bespoke vs 37% Backtrader. Validation target share: 45% vs 46%. Time-exit share remains low (~1–5%). Midline target still caps winners vs C008 time exits.

### 3. C018 protective-stop mechanics reproduced?

**Yes (distribution).** Protective-stop exit share train: 37% vs 37%; validation: 40% vs 41%. Protective arm rate Backtrader aggregate: ~37% vs bespoke mechanism diagnostic ~53% — **arm rate diverges** but protective **exit** share matches. Stop/time/protective mix direction preserved.

### 4. Trade counts close enough?

**No.** Aggregate counts: C008 354→279, C009 403→332, C018 full-window bespoke 1018→314 (per-split counts closer: ~20% gap). Exit distributions remain comparable **within the trades that fire**, so count gap is not driven by exit reclassification.

### 5. Divergence root cause

| Hypothesis | Verdict |
|---|---|
| Data mismatch | **Unlikely** — same deduped SQLite, same splits |
| Indicator warmup mismatch | **Possible contributor** — fewer entries; not fully isolated |
| Fill timing mismatch | **Unlikely** — both `signal_bar_close` |
| Bid/ask modeling mismatch | **Unlikely for exits** — exit shares match |
| Intrabar ordering mismatch | **Unlikely** — fixture tests pass; shares match |
| Stop/target precedence mismatch | **Rejected** — same-bar stop-wins fixtures pass; shares match |
| Protective-stop implementation mismatch | **Partial** — exit share matches; arm rate differs |
| Entry / RiskEngine state in BT loop | **Primary suspect** for count gap |
| Unknown | Residual bar-index or equity-window differences |

---

## Divergence taxonomy (per plan)

| Class | Applies to |
|---|---|
| **PASS** | — (trade counts exceed ±2 tolerance) |
| **CLOSE_MATCH** | Exit-reason shares all splits (≤5 pp delta) |
| **MATERIAL_DIVERGENCE** | Trade counts all campaigns |
| **BLOCKED** | — (Backtrader available; data present) |

---

## Custom engine exit bug suspected?

**No.** Independent Backtrader exit state machine reproduces stop/time/target/protective **mix and pathology direction**. Count gap indicates **entry-side or orchestration** divergence, not stop/time/protective precedence errors in the bespoke engine.

---

## Campaign verdict impact

**None.** C008/C009/C018 remain REJECT. `approved: []` unchanged. No CAMPAIGN_019.

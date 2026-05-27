# CAMPAIGN_018 Failure Analysis for Next Exit Hypothesis

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-002`  
**Evidence class:** `precommit_design_only` — `strategy_evidence: false`

---

## Executive summary

CAMPAIGN_018 executed the precommitted **+1R break-even protective stop** exactly as
designed and **REJECT**ed on primary train gate. Validation improved vs C008 but is
insufficient without train pass. The failure **falsifies the +1R break-even form** of
the protective-stop family for frozen C008 entries — not the entire concept of exit
research, but it closes profit-triggered early protection at +1R as the next test.

---

## Which gates failed

From [`research/campaign_018/gate_result.json`](../../research/campaign_018/gate_result.json):

| gate | result | value |
|---|---|---|
| **G1 train expectancy ≥ 0** | **FAIL** | −0.119 R |
| G2 validation exp > 0 | PASS | +0.194 R |
| G3 validation PF ≥ 1.05 | PASS | 1.58 |
| G4 pairs positive ≥ 2 | PASS | 6/6 |
| G5 trades ≥ 30 | PASS | 142 |
| G6 2× stress validation exp ≥ 0 | PASS | +0.178 R |
| G7 beat C011 null | PASS | margin +0.0071 R |
| G8 protective mechanism active | PASS | 53.3% armed |
| G9 zero target exits | PASS | 0% |
| **G12 full stress_15x exp ≥ 0** | **FAIL** | −0.005 R |

**Screening FAIL → REJECT.** Test lockbox not opened.

---

## Why validation strength was insufficient

Precommit philosophy (carried from C018 gate design): **train is the primary falsifier**.
Validation-only uplift without train pass is explicitly forbidden as a promotion path.

| split | C008 deduped exp R | C018 exp R | delta |
|---|---:|---:|---:|
| train | −0.025 | **−0.119** | **−0.094 worse** |
| validation | +0.161 | +0.194 | +0.033 better |

C018 validation beat C008 but **train deteriorated materially**. The protective stop
converted many would-be −1R hard stops into ~0R scratches and protective exits, but
also **removed winners** that C008's 40-bar time exit would have captured. Net train
damage dominates.

---

## What the protective stop improved

1. **Hard-stop share** fell (~68% → ~47% on combined diagnostics).
2. **Validation expectancy** rose (+0.161 → +0.194 R vs C008).
3. **Zero target exits** — avoided C009 winner-cap failure mode.
4. **Giveback bucket partially addressed** — 37% of trades exited via protective_stop
   at ~0R instead of riding back to −1R.

---

## What it worsened

1. **Train expectancy** — primary gate failure; worse than C008 (−0.119 vs −0.025).
2. **Time-exit tail** — time share fell (~32% → ~16%); delayed-reversion winners reduced.
3. **Full-window stress** — combined 2020–2026 expectancy turned negative (−0.005 R vs
   C008 +0.043 R at stress_15x).
4. **Win rate collapsed on train** — many trades scratched at break-even after touching +1R
   then failing to reach time-exit tail.

Mechanism: profit-triggered protection **fires on favorable excursion** but mean-reversion
often requires **pullback through entry** before the delayed tail. Break-even at +1R
prematurely terminates trades that C008 would hold for 40 bars.

---

## Protective-stop family vs +1R form

| scope | status |
|---|---|
| **+1R break-even protective stop (C018 v0.1.0-c018)** | **Falsified** on train gate |
| Generic "any trailing/protective stop" | **Not tested** — only one form executed |
| Profit-triggered exit at +1R threshold | **Closed** for next campaign — do not retune threshold |

C018 does **not** falsify entry-invalidation or failure-to-revert exits — those target the
**opposite diagnostic bucket** (41–47% of stops never reached +1R favorable).

---

## Financing drag interpretation

From [`C008_C009_C018_FINANCING_EXPOSURE_DIAGNOSTIC.md`](C008_C009_C018_FINANCING_EXPOSURE_DIAGNOSTIC.md):

| split | C018 gross exp R | C018 net exp R | drag R |
|---|---:|---:|---:|
| train | −0.119 | **−0.172** | −0.054 |
| validation | +0.194 | **+0.129** | −0.065 |

Financing **does not explain away train failure** — it worsens it. Validation uplift
survives financing stress (+0.129 net) but remains irrelevant without train pass.
Financing sample path is **paused**; synthetic overlay remains mandatory for any future
execution sprint interpretation.

---

## Backtrader parity confidence

Hardened parity (±1 trade, CLOSE_MATCH exits) confirms C018 exit-reason shares and trade
counts are **independently corroborated**. Custom engine bug is **not suspected**. Future
CAMPAIGN_019 execution should include Backtrader parity replay under `home_currency_v1`
+ `engine_aligned` windows — same requirement as C008/C009/C018 hardening sprint.

---

## Diagnostic split (stop pathology)

From stop/exit diagnostics on deduped C008/C009:

| bucket | share of stop exits | interpretation |
|---|---:|---|
| Never reached +1R favorable | **41–47%** | Bad entry / thesis never engaged / invalidation |
| Reached +1R then stopped at −1R | **53–60%** | Giveback after partial reversion |

C018 targeted the **giveback bucket** via profit-triggered break-even. It **failed train**.
The **invalidation bucket** remains unaddressed by C008/C009/C018 exit rules.

C009 **target** capped winners (~1.18R). C008 **time exit** preserved tail (~3.29R median
MFE on time exits). C018 **protective stop** cut giveback but damaged train tail.

---

## What CAMPAIGN_019 must avoid

1. **+1R break-even or any profit-threshold protective stop** (C018 falsified form).
2. **Threshold retune** (+0.75R, +1.5R, +2R) — overfit surface.
3. **Midline/fixed target** (C009 falsified).
4. **Initial stop distance change** (1.5× ATR retune).
5. **Time stop change** (40-bar retune).
6. **Entry parameter change** — ADX, z-score entry bands, RSI, pair universe.
7. **Validation-winner parameter selection**.
8. **Promotion on validation alone**.

---

## Implication for precommit 002

Another exit hypothesis **is warranted** — but must address the **invalidation bucket**
(thesis failure before +1R favorable), not another profit-triggered protection variant.

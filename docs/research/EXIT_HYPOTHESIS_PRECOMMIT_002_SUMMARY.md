# Exit Hypothesis Precommit 002 — Summary

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-002`  
**Sprint ID:** `EXIT_HYPOTHESIS_PRECOMMIT_002`

> **Precommit / design only** — `strategy_evidence: false`. **No backtest. No approval.**

---

## 1. Branch name

`research-exit-hypothesis-precommit-002` (from `infra-backtrader-entry-parity-hardening-001`)

---

## 2. Commit hashes by phase

| Phase | Commit | Description |
|---|---|---|
| 0 | `680e66f` | Plan + truth audit |
| 1 | `04bd83b` | C018 failure analysis |
| 2 | `6c7451d` | Hypothesis selection memo |
| 3 | `89e94df` | CAMPAIGN_019 precommit scope |
| 4 | `6755898` | Gate design |
| 5 | `babeeda` | Implementation design + execution prompt |
| 6 | `5bacb62` | Archive updates |
| 7 | *(this commit)* | Final summary + validation |

---

## 3. Files changed by phase

| Phase | Key files |
|---|---|
| 0 | `EXIT_HYPOTHESIS_PRECOMMIT_002_PLAN.md` |
| 1 | `CAMPAIGN_018_FAILURE_ANALYSIS_FOR_NEXT_EXIT_HYPOTHESIS.md` |
| 2 | `EXIT_HYPOTHESIS_PRECOMMIT_002_SELECTION_MEMO.md` |
| 3 | `CAMPAIGN_019_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md` |
| 4 | `CAMPAIGN_019_EXIT_HYPOTHESIS_GATE_DESIGN.md` |
| 5 | `CAMPAIGN_019_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md`, `NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT_002.md` |
| 6 | `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `FUTURE_RESEARCH_BACKLOG.md` |
| 7 | `EXIT_HYPOTHESIS_PRECOMMIT_002_SUMMARY.md` |

---

## 4. C018 failure analysis summary

C018 REJECT on **train expectancy −0.119 R** (G1 fail) and **full stress_15x −0.005 R** (G12 fail).
Validation +0.194 R passed but is insufficient without train pass. +1R break-even protective stop
was active (53.3% armed, 37% protective exits) but **worsened train vs C008** (−0.025 R) by
scratching trades that C008's 40-bar time exit would have held for delayed-reversion tail.

---

## 5. Whether another exit hypothesis was selected

**Yes** — exactly one hypothesis pre-registered for future CAMPAIGN_019.

---

## 6. Selected hypothesis

**Label:** `thesis_invalidation_zscore_continuation_exit`

Exit when z-score shows structural continuation failure beyond entry band:
- long: z ≤ −3.0 (entered at z ≤ −2.0)
- short: z ≥ +3.0 (entered at z ≥ +2.0)

Targets **41–47%** of stops that never reached +1R favorable — the bucket C018 did not address.

---

## 7. Candidates rejected and why

| candidate | why rejected |
|---|---|
| Early failure-to-revert window | MFE/window parameters = retune surface |
| Delayed trail after +2R | Profit-triggered; C018 family retune |
| RSI recross invalidation | Ambiguous vs winners; z-score aligned with entry |
| Regime time compression | FRED confound |
| C008-equivalent | No new information |
| No further hypothesis | Invalidation bucket still untested; parity hardened |
| C018 threshold retune | Forbidden |
| C009 midline target | Falsified |

---

## 8. Future CAMPAIGN_019 identity

| field | value |
|---|---|
| Campaign ID | `CAMPAIGN_019` |
| Strategy family | `mean_reversion_thesis_invalidation` |
| Version | `0.1.0-c019` |
| Status | **PRECOMMITTED_NOT_RUN** |

---

## 9. Frozen entry scope

Identical to C008: ADX-14 < 20, z-score ±2.0 with RSI confirmation, 6-pair H4 universe,
0.25% risk, session/spread filters per C008. No entry parameter changes permitted.

---

## 10. Precommitted exit rule

1. Initial stop: 1.5 × ATR-14 (unchanged).
2. Time stop: 40 H4 bars (unchanged).
3. No target; no protective stop; no trailing.
4. **New:** exit at bar close if z-score ≤ −3.0 (long) or ≥ +3.0 (short) → `thesis_invalidation`.
5. Priority: thesis_invalidation → stop → time → EOD.

---

## 11. Gate design summary

**Screening (all required):** train exp ≥ 0, validation exp > 0, PF ≥ 1.05, ≥ 2 pairs positive,
≥ 30 validation trades, 2× stress validation ≥ 0, beat C011 null (+0.010 R margin),
thesis_invalidation rate 5–45%, zero target/protective exits, train ≥ C008 train exp,
full stress_15x ≥ 0.

**Test lockbox (conditional):** test exp ≥ 0, PF ≥ 1.0, ≥ 20 trades.

**Backtrader parity:** ±1 trade, CLOSE_MATCH exits, `home_currency_v1`.

**Maximum status:** RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED — not approval.

---

## 12. Falsification criteria

- Train exp < 0
- Train worse than C008 (−0.025 R)
- Mechanism inert (<5%) or dominant (>45%) without train improvement
- WITHIN_NULL vs C011
- 2× stress validation negative
- Time-exit median MFE < 1.5R
- Financing overlay flips validation net exp ≤ 0
- Backtrader parity gap > ±1 trade

---

## 13. CAMPAIGN_019 executed

**No.**

---

## 14. Backtest run

**No.**

---

## 15. Retuning performed

**No.**

---

## 16. Test lockbox opened

**No.**

---

## 17. Strategy approved

**No.** `configs/approved_strategies.yaml` → `approved: []`.

---

## 18. Paper/demo/live blocked

**Yes.**

---

## 19. Archive/freeze validation results

| Check | Result |
|---|---|
| `pytest tests/ -q` | 1708 passed |
| `ruff check src tests scripts research` | PASS |
| `check_research_freeze.py` | ALL CHECKS PASSED |
| `validate_research_archive.py` | ALL CHECKS PASSED (after summary committed) |
| `scan_artifacts_for_secrets.py` | PASSED |

---

## 20. Recommended next sprint and why

**`research-campaign-019-thesis-invalidation-execution-001`**

Precommit is complete; CAMPAIGN_019 scope, gates, and implementation design are frozen.
Execution sprint should implement and run deduped backtests with Backtrader parity — still
no approval path. Prompt: [`NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT_002.md`](NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT_002.md).

---

## 21. Files to review first

1. [`docs/research/EXIT_HYPOTHESIS_PRECOMMIT_002_SELECTION_MEMO.md`](EXIT_HYPOTHESIS_PRECOMMIT_002_SELECTION_MEMO.md)
2. [`docs/research/CAMPAIGN_019_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md`](CAMPAIGN_019_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md)
3. [`docs/research/CAMPAIGN_018_FAILURE_ANALYSIS_FOR_NEXT_EXIT_HYPOTHESIS.md`](CAMPAIGN_018_FAILURE_ANALYSIS_FOR_NEXT_EXIT_HYPOTHESIS.md)
4. [`docs/research/CAMPAIGN_019_EXIT_HYPOTHESIS_GATE_DESIGN.md`](CAMPAIGN_019_EXIT_HYPOTHESIS_GATE_DESIGN.md)
5. [`docs/research/NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT_002.md`](NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT_002.md)

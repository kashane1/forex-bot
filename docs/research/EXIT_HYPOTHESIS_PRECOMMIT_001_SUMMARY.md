# Exit Hypothesis Precommit Sprint — Summary

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-001`  
**Sprint ID:** `EXIT_HYPOTHESIS_PRECOMMIT_001`

> **Precommit / design only** — `strategy_evidence: false`. **No backtest. No approval.**

---

## 1. Branch name

`research-exit-hypothesis-precommit-001` (from `infra-deduped-c008-c009-rerun-forensic-only-001`)

---

## 2. Commit hashes by phase

| phase | commit | message |
|---|---|---|
| 0 | `b991177` | plan + truth audit |
| 1 | `83ce000` | hypothesis selection memo |
| 2 | `5029465` | CAMPAIGN_018 precommit scope |
| 3 | `e5fc64a` | gate design |
| 4 | `7a34e77` | implementation design (no code) |
| 5 | `2633d11` | execution sprint prompt |
| 6 | `4ef45b8` | archive updates |
| 7 | *(this commit)* | final summary + validation |

---

## 3. Files changed by phase

| phase | files |
|---|---|
| 0 | `EXIT_HYPOTHESIS_PRECOMMIT_001_PLAN.md` |
| 1 | `EXIT_HYPOTHESIS_SELECTION_MEMO.md` |
| 2 | `CAMPAIGN_018_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md` |
| 3 | `CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md` |
| 4 | `CAMPAIGN_018_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md` |
| 5 | `NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md` |
| 6 | `EVIDENCE_INDEX.md`, `FUTURE_RESEARCH_BACKLOG.md`, `EVIDENCE_MANIFEST.json` |
| 7 | `EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md` |

---

## 4. Selected hypothesis

**`delayed_reversion_protective_stop_after_1R`** (catalog A7)

Break-even protective stop at entry price once intra-trade MFE reaches **+1.0R** (initial-risk units). No profit target. Initial hard stop 1.5× ATR-14 and 40-bar time stop unchanged.

---

## 5. Candidates rejected and why

| candidate | rejection |
|---|---|
| Midline target (C009 revival) | Falsified — caps winners ~1.18R |
| A1 volatility-scaled stop | Changes initial stop geometry — stop retune risk |
| A2 regime-dependent time stop | FRED confound + financing complexity |
| A3 counter-signal exit | Targets invalidation, not favorable-then-stopped giveback |
| A4 ATR trail after excursion | Extra trail parameters — higher overfit surface |
| A5 partial + runner bundle | Midline partial leg falsified by C009 |
| A6 no-target C008-equivalent | No new exit information |

---

## 6. Future campaign identity

| field | value |
|---|---|
| Campaign ID | `CAMPAIGN_018` (precommit only — **not executed**) |
| Strategy | `mean_reversion_protective_stop` |
| Version | `0.1.0-c018` |
| Status | pre-registered, research-only |

---

## 7. Frozen entry scope

Identical to C008: ADX-14 < 20, z-score ±2.0 with RSI confirmation, 6-pair H4 universe, 0.25% risk, session/spread filters per C008. **No entry parameter changes permitted.**

---

## 8. Precommitted exit rule

1. Initial stop: 1.5 × ATR-14 at entry.
2. When MFE ≥ +1.0R (first touch), move active stop to **entry price** (break-even).
3. No midline/target exit; no trailing ratchet in v0.1.0-c018.
4. Time stop: 40 H4 bars unchanged.

---

## 9. Gate design summary

**Screening (must all pass to open lockbox):** train exp ≥ 0, validation exp > 0, PF ≥ 1.05, ≥ 2 pairs positive, ≥ 30 validation trades, 2× stress validation exp ≥ 0, beat-null vs C011 (+0.010R margin), protective mechanism active, zero target exits.

**Test lockbox (conditional):** test exp ≥ 0, PF ≥ 1.0, ≥ 20 trades.

**Ceiling:** REVISE maximum even if all pass. Financing overlay mandatory before promotion interpretation.

---

## 10. Falsification criteria

- Train exp < 0 (same as C008/C009)
- WITHIN_NULL vs C011 deduped
- 2× stress validation negative
- Time-exit median MFE < 1.5R (tail collapsed)
- Protective transition on < 5% of trades (inert rule)
- Validation uplift disappears under financing overlay

---

## 11. CAMPAIGN_018 executed?

**No.** Precommit docs only; no `backtests/CAMPAIGN_018*` outputs.

---

## 12. Any backtest run?

**No.**

---

## 13. Retuning performed?

**No.**

---

## 14. Test lockbox opened?

**No.**

---

## 15. Any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

---

## 16. Paper/demo/live blocked?

**Yes.** Loops refuse without approved registry entry.

---

## 17. Archive/freeze validation results

| check | result |
|---|---|
| `pytest tests/ -q` | **1660 passed** (after summary doc) |
| `ruff check src tests scripts research` | **PASS** |
| `python scripts/check_research_freeze.py` | **PASS** |
| `python scripts/validate_research_archive.py` | **PASS** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASS** |

---

## 18. Recommended next sprint and why

**`research-campaign-018-protective-stop-execution-001`**

Precommit is complete with frozen entries, one exit change, gates, and falsification rules. Next step is implement + deduped backtest per [`NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md`](NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md). Run financing overlay during execution. Still no approval path.

---

## 19. Files to review first

1. [`EXIT_HYPOTHESIS_SELECTION_MEMO.md`](EXIT_HYPOTHESIS_SELECTION_MEMO.md) — why this hypothesis, why not retune
2. [`CAMPAIGN_018_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md`](CAMPAIGN_018_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md) — frozen entries + exit rule
3. [`CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md`](CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md) — pass/fail thresholds
4. [`CAMPAIGN_018_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md`](CAMPAIGN_018_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md) — future code plan
5. [`NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md`](NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md) — copy-paste execution prompt

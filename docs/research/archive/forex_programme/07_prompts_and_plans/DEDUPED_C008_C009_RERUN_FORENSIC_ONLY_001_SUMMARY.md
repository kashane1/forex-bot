# Deduped C008/C009 Rerun Forensic-Only Sprint — Summary

**Date:** 2026-05-27  
**Branch:** `infra-deduped-c008-c009-rerun-forensic-only-001`  
**Sprint:** `DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001`

> **Forensic replay / evidence-integrity sprint only** — `strategy_evidence: false`.
> **No approval. No retuning. No CAMPAIGN_018. Test lockbox unopened.**

---

## 1. Branch name

`infra-deduped-c008-c009-rerun-forensic-only-001` (from `research-stop-and-exit-diagnostics-001`)

---

## 2. Commit hashes by phase

| phase | commit | message |
|---|---|---|
| 0 | `bcdd812` | plan doc + truth audit |
| 1 | `6b80fcb` | frozen config reconstruction |
| 2 | `8ed4510` | replay runner + tests |
| 3 | `1118646` | execute deduped replay + compact JSON |
| 4 | `4aa0f9c` | old vs deduped comparison doc |
| 5 | `ccf3673` | deduped exit anatomy + MAE/MFE docs |
| 6 | `638ae7d` | evidence integrity decision memo |
| 7 | `4093ce1` | archive/backlog updates |
| 8 | *(this commit)* | final summary + validation |

---

## 3. Files changed by phase

| phase | files |
|---|---|
| 0 | `docs/research/DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_PLAN.md` |
| 1 | `research/deduped_c008_c009_rerun/frozen_config_reconstruction.json`, `docs/research/C008_C009_FROZEN_CONFIG_RECONSTRUCTION.md` |
| 2 | `scripts/rerun_c008_c009_deduped_forensic.py`, `tests/unit/test_deduped_c008_c009_forensic.py`, `.gitignore` |
| 3 | `research/deduped_c008_c009_rerun/*.json` (7 files), `docs/research/C008_C009_DEDUPED_FORENSIC_REPLAY_RESULTS.md`, runner fix |
| 4 | `docs/research/C008_C009_OLD_VS_DEDUPED_COMPARISON.md` |
| 5 | `docs/research/C008_C009_DEDUPED_EXIT_ANATOMY.md`, `docs/research/C008_C009_DEDUPED_MAE_MFE_DIAGNOSTICS.md` |
| 6 | `docs/research/C008_C009_EVIDENCE_INTEGRITY_DECISION.md` |
| 7 | `docs/research/EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `FUTURE_RESEARCH_BACKLOG.md`, `STRATEGY_STATUS.md` |
| 8 | `docs/research/DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_SUMMARY.md` |

Gitignored forensic trade CSVs: `backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/`, `backtests/CAMPAIGN_009_mean_reversion_midline_deduped_forensic/`

---

## 4. Frozen config reconstruction status

**COMPLETE** — no `BLOCKED_EXACT_CONFIG_NOT_RECONSTRUCTED`. Machine-readable summary in `research/deduped_c008_c009_rerun/frozen_config_reconstruction.json`; human doc in `C008_C009_FROZEN_CONFIG_RECONSTRUCTION.md`.

---

## 5. Replay runner status

**OPERATIONAL** — `scripts/rerun_c008_c009_deduped_forensic.py` with subcommands `preflight`, `replay`, `compare`, `exit-anatomy`. Seven unit tests in `tests/unit/test_deduped_c008_c009_forensic.py`.

---

## 6. Deduped C008 replay status

**SUCCESS** — train 216 / validation 138 trades (base cost); identical counts to original. Train exp **−0.025 R** (original −0.017 R); validation **+0.161 R** (original +0.172 R). Gate **FAIL** (`train_expectancy_gte_zero`). Verdict **REJECT**.

---

## 7. Deduped C009 replay status

**SUCCESS** — train 252 / validation 151 trades (base cost); identical counts to original. Train exp **−0.025 R** (original −0.062 R — material change, gate still FAIL); validation **+0.186 R** (original +0.170 R). Verdict **REJECT**.

---

## 8. Test lockbox opened?

**No.** `test_window_opened: false` in all forensic outputs. 2025–2026 test window remains closed.

---

## 9. C008 old vs deduped comparison

| metric | original | deduped | classification |
|---|---:|---:|---|
| train trades | 216 | 216 | CONFIRMED_DEDUP_SAFE |
| validation trades | 138 | 138 | CONFIRMED_DEDUP_SAFE |
| train exp R | −0.017 | −0.025 | CONFIRMED_DEDUP_SAFE (shape unchanged) |
| validation exp R | +0.172 | +0.161 | CONFIRMED_DEDUP_SAFE |
| train gate | FAIL | FAIL | CONFIRMED_DEDUP_SAFE |
| exit stop share | ~68% | 68.1% | CONFIRMED_DEDUP_SAFE |
| exit time share | ~32% | 31.6% | CONFIRMED_DEDUP_SAFE |

106,286 duplicate H4 rows dropped in preflight; trade ledger unchanged (identical duplicate bars).

---

## 10. C009 old vs deduped comparison

| metric | original | deduped | classification |
|---|---:|---:|---|
| train trades | 252 | 252 | CONFIRMED_DEDUP_SAFE |
| validation trades | 151 | 151 | CONFIRMED_DEDUP_SAFE |
| train exp R | −0.062 | −0.025 | **MATERIAL_CHANGE** (gate still FAIL) |
| validation exp R | +0.170 | +0.186 | CONFIRMED_DEDUP_SAFE |
| exit stop share | ~56% | 56.3% | CONFIRMED_DEDUP_SAFE |
| exit target share | ~41% | 40.9% | CONFIRMED_DEDUP_SAFE |

---

## 11. C008 train fail / validation positive shape persists?

**Yes.** Train negative, validation positive with 6/6 pairs positive and PF > 1.05. Screening gate still fails on train expectancy only.

---

## 12. C009 midline winner-capping persists?

**Yes.** Target exits median ~1.33R vs C008 time exits median ~1.35R aggregate but C008 time median MFE **3.29R** vs C009 target median MFE **1.83R** — winner tail still capped relative to C008 delayed reversion path.

---

## 13. Stop/time split persists?

**Yes.**

- **C008:** 68% stop (−0.80R exp), 32% time (+1.86R exp); train stop-dominated (~71%), validation time-heavy.
- **C009:** 56% stop, 41% target (+1.18R), 2% time — stop/time pathology reframed as stop/target split with time nearly absent.

---

## 14. MAE/MFE refresh findings

| finding | C008 deduped | prior diagnostics |
|---|---:|---:|
| stop ≥1R favorable before stop | 60.17% | 58.86% |
| stop never ≥1R favorable | 39.83% | 41.14% |
| time median MFE R | 3.29 | 3.33 |
| median stop distance pips | 45.33 | ~45 |

C009 MAE/MFE **identical** to prior stop/exit diagnostics after base-cost-only fix (403 trades).

---

## 15. Evidence-integrity decision

Old `LIKELY_CONTAMINATED` label **superseded for descriptive use** by **`DEDUPED_FORENSIC_REPLAY_CONFIRMED`**. Verdicts unchanged **REJECT / research-only**. Exit hypothesis pre-registration **conditionally allowed** on new campaign ID per `FUTURE_EXIT_RESEARCH_GATE.md`. See `C008_C009_EVIDENCE_INTEGRITY_DECISION.md`.

---

## 16. Retuning performed?

**No.** Frozen entry and exit rules; no parameter optimization.

---

## 17. New strategy campaign created?

**No.** Forensic replay paths only (`*_deduped_forensic`); no CAMPAIGN_018.

---

## 18. Any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

---

## 19. CAMPAIGN_018 created?

**No.**

---

## 20. Paper/demo/live remain blocked?

**Yes.** All strategies paper/demo/live = NO; order-capable loops refuse without approved registry entry.

---

## 21. Archive/freeze validation results

| check | result |
|---|---|
| `pytest tests/ -q` | **1658 passed** (after summary doc fixes evidence_index_links) |
| `ruff check src tests scripts research` | **PASS** |
| `python scripts/check_research_freeze.py` | **PASS** |
| `python scripts/validate_research_archive.py` | **PASS** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASS** |

---

## 22. Remaining blockers

- Train expectancy gate FAIL for both C008 and C009
- Test lockbox 2025–2026 unopened
- Multi-day hold financing unmodeled
- Broad strategy search paused
- No approved strategies; paper/demo/live blocked
- C008/C009 not promotion candidates — diagnostic clue only

---

## 23. Recommended next sprint and why

**`research-exit-hypothesis-precommit-001`**

Deduped replay confirmed exit pathology (stop/time split, C009 target capping, MAE/MFE populations) on clean inputs. Evidence integrity sufficient to **pre-register** one exit hypothesis under gate rules — not C008/C009 retune, not promotion.

---

## 24. Files to review first

1. [`C008_C009_EVIDENCE_INTEGRITY_DECISION.md`](C008_C009_EVIDENCE_INTEGRITY_DECISION.md) — authoritative integrity ruling
2. [`C008_C009_OLD_VS_DEDUPED_COMPARISON.md`](C008_C009_OLD_VS_DEDUPED_COMPARISON.md) — headline metric deltas
3. [`C008_C009_DEDUPED_FORENSIC_REPLAY_RESULTS.md`](C008_C009_DEDUPED_FORENSIC_REPLAY_RESULTS.md) — execution record
4. [`research/deduped_c008_c009_rerun/gate_result.json`](../../research/deduped_c008_c009_rerun/gate_result.json) — machine-readable gates
5. [`C008_C009_DEDUPED_EXIT_ANATOMY.md`](C008_C009_DEDUPED_EXIT_ANATOMY.md) — exit reason breakdown
6. [`C008_C009_DEDUPED_MAE_MFE_DIAGNOSTICS.md`](C008_C009_DEDUPED_MAE_MFE_DIAGNOSTICS.md) — adverse excursion refresh

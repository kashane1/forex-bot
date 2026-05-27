# Financing Modeled PnL and Carry Readiness — Summary

**Date:** 2026-05-27  
**Branch:** `research-financing-modeled-pnl-and-carry-readiness-001`  
**Sprint ID:** `FINANCING_MODELED_PNL_AND_CARRY_READINESS_001`

> **Infrastructure sprint complete** — `strategy_evidence: false`, `not_approved: true`. No campaign verdicts changed.

---

## 1. Branch name

`research-financing-modeled-pnl-and-carry-readiness-001`

---

## 2. Commit hashes by phase

| phase | commit |
|---|---|
| 0 | `4d59f20` |
| 1 | `53aba17` |
| 2–3 | `2b37c6a` |
| 4–6 | `1922dae` |
| 7–8 | *(this commit)* |

---

## 3. Files changed by phase

| phase | key files |
|---|---|
| 0 | `FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_PLAN.md` |
| 1 | `modeled_pnl_readiness_audit.json`, `FINANCING_CAPABILITY_AUDIT.md` |
| 2–3 | `manual_csv.py`, `overlay.py`, `apply_modeled_financing_overlay.py`, tests |
| 4–6 | `c008_c009_c018_financing_exposure.json`, exposure diagnostic, carry memo, next sprint prompt |
| 7–8 | EVIDENCE_INDEX, MANIFEST, BACKLOG, this summary |

---

## 4. Financing capability audit findings

- Engine PnL: **UNMODELED**
- Existing overlay: conservative bp/day **ESTIMATED** stress in `src/forex_bot/financing.py`
- Research calculator: per-day rollover events in `research/financing/` (70+ prior tests)
- Observed rates: **not available** — no historical OANDA series, no DAILY_FINANCING capture
- MODELED treatment: **refused** until observed data exists
- Binding blocker for carry: side-specific observed rates + engine/overlay reconciliation

---

## 5. Modeled financing interface status

- Added `FinancingSourceType` enum: `synthetic_fixture`, `manual_csv`, `observed_future`
- Added `source_type` on rate sources
- Added `load_manual_csv_rate_schedule()` for CSV rate tables
- Existing `TableRateSource`, `ConservativeStressRateSource`, calculator unchanged in behavior
- **MODELED still refused** — by design

---

## 6. Engine PnL changed?

**No.** BacktestEngine PnL remains UNMODELED. No opt-in wiring added.

---

## 7. Financing overlay utility status

- `research/financing/overlay.py` — apply financing to trade CSV records
- `scripts/apply_modeled_financing_overlay.py` — CLI for single file or glob
- `scripts/generate_c008_c009_c018_financing_exposure.py` — batch diagnostic generator
- 9 new tests pass

---

## 8. C008/C009/C018 financing exposure findings

| campaign | split | gross exp R | net exp R | drag R |
|---|---:|---:|---:|---:|
| C008 | train | −0.025 | −0.105 | −0.080 |
| C008 | validation | +0.161 | +0.069 | −0.092 |
| C009 | validation | +0.186 | +0.140 | −0.046 |
| C018 | train | −0.119 | −0.172 | −0.054 |
| C018 | validation | +0.194 | +0.129 | −0.065 |

Validation uplift is **partially carry-inflated** (~33–57% reduction gross→net). Train failures **worsen** under financing.

---

## 9. Observed financing used?

**No.**

---

## 10. Synthetic/manual/observed label

**`SYNTHETIC_FINANCING_DIAGNOSTIC`** — conservative stress rate source only.

---

## 11. Carry-readiness conclusion

**Not ready.** Infrastructure for deterministic overlay exists; observed broker financing capture is the binding blocker for MODELED treatment and carry research.

---

## 12. Remaining financing blockers

- No observed DAILY_FINANCING history
- No historical OANDA rate time series
- Engine PnL carry-blind
- Cross-pair conversion deferred
- Holiday calendar absent
- Side-specific carry asymmetry untestable with stress-only source

---

## 13. Campaign verdict changed?

**No.** C008 REJECT, C009 REJECT, C018 REJECT unchanged.

---

## 14. New strategy campaign created?

**No.** No CAMPAIGN_019.

---

## 15. Strategy approved?

**No** — `configs/approved_strategies.yaml`: `approved: []`

---

## 16. Paper/demo/live blocked?

**Yes** — freeze gate confirms loops refuse.

---

## 17. Executor/broker behavior changed?

**No.**

---

## 18. OANDA order API calls?

**No.**

---

## 19. Archive/freeze validation

Run after this commit: pytest, ruff, freeze, archive, secret scan.

---

## 20. Recommended next sprint

**`infra-observed-financing-capture-readonly-001`** — modeled interface works but observed broker financing is missing; read-only DAILY_FINANCING capture is the binding blocker for MODELED treatment.

---

## 21. Files to review first

1. [`C008_C009_C018_FINANCING_EXPOSURE_DIAGNOSTIC.md`](C008_C009_C018_FINANCING_EXPOSURE_DIAGNOSTIC.md)
2. [`CARRY_AND_FINANCING_READINESS_MEMO.md`](CARRY_AND_FINANCING_READINESS_MEMO.md)
3. [`FINANCING_CAPABILITY_AUDIT.md`](FINANCING_CAPABILITY_AUDIT.md)
4. [`research/financing/c008_c009_c018_financing_exposure.json`](../../research/financing/c008_c009_c018_financing_exposure.json)
5. [`research/financing/overlay.py`](../../research/financing/overlay.py)
6. [`scripts/apply_modeled_financing_overlay.py`](../../scripts/apply_modeled_financing_overlay.py)

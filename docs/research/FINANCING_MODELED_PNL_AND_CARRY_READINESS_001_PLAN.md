# Financing Modeled PnL and Carry Readiness — Execution Plan

**Date:** 2026-05-27  
**Branch:** `research-financing-modeled-pnl-and-carry-readiness-001`  
**Sprint ID:** `FINANCING_MODELED_PNL_AND_CARRY_READINESS_001`  
**Type:** Infrastructure / diagnostic only — `strategy_evidence: false`

---

## 1. Purpose

Move financing from estimated/conservative overlay toward **modeled PnL readiness**, so future multi-day H4 strategies, carry-sensitive strategies, and exit variants (including C008/C009/C018 diagnostics) can be judged honestly.

CAMPAIGN_018 is **REJECT** and must **not** be retuned or revived in this sprint.

---

## 2. Non-goals

- Approve any strategy
- Edit `configs/approved_strategies.yaml` (except verify `approved: []`)
- Create CAMPAIGN_019 or run any new strategy campaign
- Retune C008, C009, or C018
- Rerun C018 with modified parameters
- Open the C018 test lockbox
- Enable paper/demo/live
- Modify executor/broker behavior
- Call OANDA order APIs or use live broker credentials
- Commit `.env`, API keys, broker tokens, SQLite DBs, raw candle exports, account statements, or bulky artifacts
- Change C008/C009/C018 campaign verdicts based on synthetic financing

---

## 3. Source artifacts

| artifact | role |
|---|---|
| [`CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md`](CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md) | C018 REJECT context; validation uplift may be carry-inflated |
| [`CAMPAIGN_018_FINAL_INTERPRETATION.md`](CAMPAIGN_018_FINAL_INTERPRETATION.md) | Mechanism worked; train gate failed |
| [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md) | Prior financing calculator sprint status |
| [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md) | Calculator protocol |
| [`src/forex_bot/financing.py`](../../src/forex_bot/financing.py) | Conservative stress overlay + interface |
| [`research/financing/`](../../research/financing/) | Per-day rollover calculator |
| [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md) | Observed capture design (future) |

---

## 4. Current financing status (pre-sprint audit)

| layer | status |
|---|---|
| Engine PnL | **UNMODELED** — no financing accrual in `BacktestEngine` |
| Per-trade overlay | **ESTIMATED** — conservative bp/day debit in `src/forex_bot/financing.py` |
| Research calculator | **ESTIMATED** — per-day rollover events in `research/financing/` |
| Observed rates | **Not available** — no historical OANDA series; no DAILY_FINANCING capture |
| MODELED treatment | **Refused** — placeholder only (`FutureOandaObservedFinancingModel`) |

---

## 5. Safety rules

- All outputs: `strategy_evidence: false`, `not_approved: true`
- `configs/approved_strategies.yaml`: `approved: []`
- Paper/demo/live remain blocked
- Executor/broker unchanged
- No OANDA order API calls
- Synthetic financing labeled `SYNTHETIC_FINANCING_DIAGNOSTIC` — not verdict-changing
- If precommit ambiguity on rate conventions: document `BLOCKED_PRECOMMIT_AMBIGUITY` and stop

---

## 6. No-broker-order rule

Read-only broker/account/transaction access may be documented for a **future** sprint only. This sprint uses fixtures, synthetic schedules, and existing trade CSVs only.

---

## 7. No-strategy rule

No new campaigns. No C018 retune. No approval. Descriptive financing exposure on existing C008/C009/C018 trades only.

---

## 8. Phase plan

| phase | deliverable |
|---|---|
| 0 | This plan + truth audit |
| 1 | `research/financing/modeled_pnl_readiness_audit.json` + `FINANCING_CAPABILITY_AUDIT.md` |
| 2 | Hardened rate-source interface (`FinancingSourceType`, manual CSV loader, fixture source) + tests |
| 3 | `scripts/apply_modeled_financing_overlay.py` + overlay module + tests |
| 4 | C008/C009/C018 financing exposure JSON + diagnostic doc |
| 5 | `CARRY_AND_FINANCING_READINESS_MEMO.md` |
| 6 | `NEXT_SPRINT_PROMPT_AFTER_FINANCING_MODELED_PNL.md` |
| 7 | EVIDENCE_INDEX, MANIFEST, BACKLOG, STRATEGY_STATUS updates |
| 8 | Final validation + `FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_SUMMARY.md` |

---

## 9. Expected artifacts

```
research/financing/modeled_pnl_readiness_audit.json
research/financing/c008_c009_c018_financing_exposure.json
docs/research/FINANCING_CAPABILITY_AUDIT.md
docs/research/C008_C009_C018_FINANCING_EXPOSURE_DIAGNOSTIC.md
docs/research/CARRY_AND_FINANCING_READINESS_MEMO.md
docs/research/NEXT_SPRINT_PROMPT_AFTER_FINANCING_MODELED_PNL.md
docs/research/FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_SUMMARY.md
scripts/apply_modeled_financing_overlay.py
research/financing/overlay.py (or equivalent)
tests/research/test_financing_overlay.py
tests/research/test_financing_source_types.py
```

---

## 10. Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

---

## 11. Blocked conditions

- `approved_strategies.yaml` not empty → stop
- CAMPAIGN_019 created → stop
- Engine PnL wired without opt-in research flag → stop
- Observed financing claimed without observed data → stop
- Campaign verdict changed based on synthetic financing → stop
- Broker order API called → stop

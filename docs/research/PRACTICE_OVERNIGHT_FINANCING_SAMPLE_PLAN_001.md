# Practice Overnight Financing Sample — Planning Sprint

**Date:** 2026-05-27  
**Branch:** `infra-practice-overnight-financing-sample-plan-001`  
**Sprint ID:** `PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001`  
**Type:** Planning / runbook only — `strategy_evidence: false`

---

## 1. Purpose

Create a safe, **human-executed** practice-account financing sample collection plan so the repo can eventually capture non-empty `DAILY_FINANCING` transactions using the existing read-only capture infrastructure (`scripts/capture_observed_financing_readonly.py`).

This sprint produces **docs and runbooks only**. No orders, no code that submits trades, no broker mutation endpoints.

---

## 2. Context (prior sprint)

| artifact | status |
|---|---|
| Read-only capture | **succeeded** (`infra-observed-financing-capture-readonly-001`) |
| Practice credentials | **present** |
| DAILY_FINANCING in 180 days | **0** |
| Parser / sanitizer / capture script | **ready** |
| MODELED financing | **blocked** until non-empty observed samples |

Source docs:
- [`OBSERVED_FINANCING_CAPTURE_READONLY_001_SUMMARY.md`](OBSERVED_FINANCING_CAPTURE_READONLY_001_SUMMARY.md)
- [`OBSERVED_FINANCING_CAPTURE_RESULT.md`](OBSERVED_FINANCING_CAPTURE_RESULT.md)
- [`OBSERVED_FINANCING_READINESS_DECISION.md`](OBSERVED_FINANCING_READINESS_DECISION.md)

---

## 3. Non-goals

- Place, open, close, or modify positions (Cursor or bot)
- Call OANDA order/trade/position mutation endpoints
- Enable paper/demo/live loops
- Approve any strategy; create CAMPAIGN_019; run strategy campaigns
- Retune C008/C009/C018
- Modify executor/broker behavior
- Commit credentials, `.env`, account statements, or raw API dumps

---

## 4. Safety rules

| rule | enforcement |
|---|---|
| Cursor must not submit orders | this sprint is docs-only |
| Human places practice trades manually | OANDA practice UI only |
| Bot remains frozen | `approved: []`; loops refuse |
| Practice environment only | never live account |
| Read-only capture after sample | existing capture script only |
| Sanitized artifacts only in git | raw dir gitignored |

---

## 5. Phase plan

| phase | deliverable |
|---|---|
| 0 | This plan + truth audit |
| 1 | [`PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md`](PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md) |
| 2 | [`POST_SAMPLE_OBSERVED_FINANCING_CAPTURE_CHECKLIST.md`](POST_SAMPLE_OBSERVED_FINANCING_CAPTURE_CHECKLIST.md) |
| 3 | [`OBSERVED_TO_MODELED_FINANCING_BRIDGE_DESIGN.md`](OBSERVED_TO_MODELED_FINANCING_BRIDGE_DESIGN.md) |
| 4 | EVIDENCE_INDEX, MANIFEST, BACKLOG updates |
| 5 | Summary + final validation |

---

## 6. Expected artifacts

```
docs/research/PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001.md
docs/research/PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md
docs/research/POST_SAMPLE_OBSERVED_FINANCING_CAPTURE_CHECKLIST.md
docs/research/OBSERVED_TO_MODELED_FINANCING_BRIDGE_DESIGN.md
docs/research/PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001_SUMMARY.md
```

No code changes. No new scripts that call mutation endpoints.

---

## 7. Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

---

## 8. Blocked conditions

- Any order placement by Cursor or bot code added in this sprint
- Any mutation endpoint called during this sprint
- `approved_strategies.yaml` edited to add a strategy
- CAMPAIGN_019 created
- Claim that observed financing was captured (human sample not yet taken)

---

## 9. Truth audit (phase 0)

| check | result |
|---|---|
| Prior capture summary exists | ✓ |
| Capture result doc exists | ✓ |
| Readiness decision exists | ✓ |
| `capture_observed_financing_readonly.py` exists | ✓ |
| `research/financing/observed.py` exists | ✓ |
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_019 | not created |
| Paper/demo/live | blocked (freeze gate) |
| Executor/broker | unchanged this sprint |

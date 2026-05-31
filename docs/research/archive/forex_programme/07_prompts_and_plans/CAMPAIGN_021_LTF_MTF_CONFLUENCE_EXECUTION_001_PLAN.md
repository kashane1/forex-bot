# CAMPAIGN_021 — LTF MTF Confluence Execution Sprint Plan

**Date:** 2026-05-27  
**Branch:** `research-campaign-021-ltf-mtf-confluence-execution-001`  
**Base:** `main` @ `dc8e0cb` or later (scaffold + gate discipline merged)

## Purpose

Execute gate-disciplined train/validation evidence for `lower_timeframe_mtf_confluence_entry 0.1.0-c021` on M15 with hybrid M1/H4 provenance. Determine whether LTF execution improves train stability versus CAMPAIGN_020 (H4, REJECT).

## Source precommit docs

- `CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md`
- `NEXT_SPRINT_PROMPT_CAMPAIGN_021_LTF_MTF_CONFLUENCE_EXECUTION.md`
- `CAMPAIGN_021_BACKTRADER_PARITY_DESIGN.md`
- `M1_FULL_CORPUS_LTF_LANE_READINESS_DECISION.md`

## Frozen scope

- Identity, parameters, gates, splits — unchanged from precommit
- M15 execution; M1-derived M15/H1/H4; native H4→D1AGG only
- `next_bar_open`, conservative, approval_bound
- Seven majors; splits: train 2020–2022, validation 2023–2024, test 2025–2026-05-20

## Gate order (non-negotiable)

1. Train → if fail: REJECT, lockbox closed, STOP (no validation rescue)
2. Validation (only if train pass) → if fail: REJECT, STOP
3. Backtrader parity (only if train+validation pass) → if fail: REJECT, STOP
4. Test lockbox (only if all above pass) — single run
5. No approval under any outcome

## Non-goals

- No parameter tuning; no rule changes after results
- No paper/demo/live; no OANDA mutations; no live APIs
- No M1-derived D1AGG; no `signal_bar_close`
- No approval registry changes

## Safety rules

- `approved_strategies.yaml` must stay `approved: []`
- Compact committed artifacts; raw trades under `research/campaign_021/raw/` (gitignored)
- No raw M1/DB commits

## Blocked conditions

- `BLOCKED_PRECOMMIT_AMBIGUITY` if implementation ≠ precommit
- `BLOCKED_PARITY` if parity lane unavailable after train+validation pass
- Train-negative / validation-positive → REJECT (no C020-style rescue)

## Expected artifacts

| phase | artifacts |
|---|---|
| 2 | `data_feature_preflight.json` |
| 3 | `train_*.json/csv` |
| 5–6 | `validation_*.json`, `gate_result.json` |
| 7 | `backtrader_parity_result.json` |
| 8 | `test_metrics.json` (only if lockbox opens) |
| 9 | gate docs, interpretation, evidence index updates |

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/run_campaign_021_ltf_mtf_confluence.py --preflight-only
```

## No approval statement

This sprint may not add any strategy to `approved_strategies.yaml`. Maximum status: RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED.

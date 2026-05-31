# CAMPAIGN 021 LTF MTF Confluence Scaffold 001 Plan

**Branch:** `research-campaign-021-ltf-mtf-confluence-scaffold-001`
**Base:** `main` after `infra-m1-full-corpus-validation-and-aggregation-001` (`b0f92e5`)
**Scope:** scaffold and precommit only. No evidence, no approval, no paper/demo/live.

## Purpose

Create CAMPAIGN_021 `lower_timeframe_mtf_confluence_entry 0.1.0-c021`: M15 execution with H1/H4/D1AGG context, M1-canonical lower/intermediate frames, and hybrid D1AGG provenance (native H4→D1AGG). Tests whether tighter M15 entries improve on C020’s H4-only MTF confluence thesis.

## Non-Goals

- No train/validation/test evidence.
- No test lockbox.
- No parameter sweeps or result-driven tuning.
- No CAMPAIGN_021 approval or `approved_strategies.yaml` edits.
- No OANDA calls, broker mutation, or live hosts.
- No M1-derived D1AGG for C021.

## M1 Validation Status (Input)

- 12,793,196 M1 rows, seven majors, 2021-05-27→2026-05-26.
- Inventory PASS; quality WARN (calendar gaps); M5/M15/H1/H4 aggregation PASS.
- H4 drift WARN, 0 OHLC mismatch on overlap.
- M1-only D1AGG not ready; native H4→D1AGG PASS.
- Readiness: `READY_WITH_WARNINGS`.

## Required Hybrid Provenance

| Layer | Source |
| --- | --- |
| M15 execution | M1-derived |
| H1 context | M1-derived |
| H4 context | M1-derived |
| D1AGG context | native H4-derived D1AGG only |

## Phases

0. Plan and baseline audit (this doc).
1. Structural distinctness memo.
2. Precommit parameter freeze.
3. Strategy module + campaign config.
4. Unit/invariant tests.
5. Preflight runner (no evidence).
6. Backtrader parity design.
7. Future execution prompt.
8. Evidence index / manifest / backlog / status.
9. Summary and final validation.

## Validation Commands

- `pytest tests/ -q`
- `ruff check src tests scripts research`
- `python scripts/check_research_freeze.py`
- `python scripts/validate_research_archive.py`
- `python scripts/scan_artifacts_for_secrets.py`
- `python scripts/run_campaign_021_ltf_mtf_confluence.py --preflight-only`

## No-Approval Statement

CAMPAIGN_021 remains `SCAFFOLD_ONLY` / `PRECOMMITTED_NOT_EXECUTED`. C020 stays REJECT. `approved_strategies.yaml` stays `approved: []`.

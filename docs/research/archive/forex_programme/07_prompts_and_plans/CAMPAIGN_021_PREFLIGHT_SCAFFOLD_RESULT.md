# CAMPAIGN_021 — Preflight Scaffold Result

**Date:** 2026-05-27  
**Branch:** `research-campaign-021-ltf-mtf-confluence-scaffold-001`  
**Status:** SCAFFOLD_ONLY — preflight PASS; no evidence run

## Command

```bash
python scripts/run_campaign_021_ltf_mtf_confluence.py --preflight-only
```

## Outcome

| check | result |
|---|---|
| `preflight_ok` | **true** |
| M1 corpus (7 majors) | PASS |
| native H4 rows | 69,648 |
| D1AGG provenance | `native_h4_derived_d1agg` enforced |
| M1-derived D1AGG | rejected in config + validator |
| `fill_timing` | `next_bar_open` |
| `strategy_evidence` | false |
| `test_lockbox_opened` | false |
| `not_approved` | true |

Artifact: `research/campaign_021/preflight_result.json`

## Blocked in scaffold sprint

- `train-validation`, `test`, `full` subcommands return exit 2 with evidence-block message.

## No approval

`configs/approved_strategies.yaml` remains `approved: []`. Paper/demo/live blocked.

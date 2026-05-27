# CAMPAIGN_020 — Preflight Scaffold Result

**Date:** 2026-05-27  
**Branch:** `research-mtf-confluence-candidate-020-scaffold-001`  
**Status:** Preflight scaffold only — **no evidence, no approval**

## Preflight command

```bash
python scripts/run_campaign_020_mtf_confluence.py --preflight-only
python scripts/run_campaign_020_mtf_confluence.py --validate-config
python scripts/run_campaign_020_mtf_confluence.py --emit-plan
```

## What preflight validates

- Campaign YAML `research_metadata` parses (`fill_timing: next_bar_open`)
- Strategy config frozen to `0.1.0-c020` / precommitted EMA parameters
- `trading_enabled` and `allow_order_submission` remain false
- `campaign.not_approved: true`
- Local DB path exists (warns/blocks if `data/campaign_002.sqlite3` missing)
- Warmup feasibility (`warmup_bars_required: 520`)
- Financing declaration present (`financing_mode: none`, overlay required)
- Output directory `research/campaign_020/` writable

## What preflight refuses

- `--execute-evidence` (exit code 2) — full train/validation blocked in scaffold sprint
- Any broker order mutation (script has no broker imports)
- Strategy approval or registry changes

## Future execution sprint must

1. Run train + validation under `next_bar_open` only
2. Apply precommitted gates from `CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md`
3. Run financing overlay sensitivity for holds > 1 day
4. Run Backtrader parity before test lockbox
5. Open test lockbox only if gates + parity pass
6. Update evidence docs honestly — max status `RESEARCH_PASS` / `PROMOTION_REVIEW_REQUIRED`

See `docs/research/NEXT_SPRINT_PROMPT_CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION.md`.

## No evidence / no approval statement

**No train/validation/test verdict exists for CAMPAIGN_020.** `configs/approved_strategies.yaml` remains `approved: []`.

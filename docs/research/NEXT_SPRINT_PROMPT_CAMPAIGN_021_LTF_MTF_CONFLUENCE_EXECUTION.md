# Next Sprint Prompt — CAMPAIGN_021 LTF MTF Confluence Execution

**Branch to create:** `research-campaign-021-ltf-mtf-confluence-execution-001`  
**Base:** latest clean `main` after merging scaffold branch  
**Prerequisite docs:** `CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md`, `CAMPAIGN_021_BACKTRADER_PARITY_DESIGN.md`

## Hard safety rules

1. Run **train + validation only** first — no test until gates pass.
2. **M15** execution; M1-derived M15/H1/H4; **native H4→D1AGG only**.
3. `fill_timing: next_bar_open`, `execution_realism: conservative`, `evidence_use: approval_bound`.
4. Use `htf_align` / LTF alignment — strict warmups, no incomplete HTF bars.
5. **No parameter retuning** from results; frozen YAML `0.1.0-c021`.
6. **No approval**; `approved_strategies.yaml` stays `approved: []`.
7. **No paper/demo/live**; no OANDA order/trade/position mutations; no live APIs.
8. **Backtrader parity** required before test lockbox.
9. Test lockbox opens only if train/validation gates **and** parity pass.
10. Maximum outcome: RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED — not production approval.

## Commands (execution sprint)

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/run_campaign_021_ltf_mtf_confluence.py --validate-config
python scripts/run_campaign_021_ltf_mtf_confluence.py train-validation  # when enabled
```

Scaffold sprint blocks `train-validation` / `test` / `full` subcommands.

## Gates (frozen)

- Train expectancy ≥ 0 (`next_bar_open`)
- Validation expectancy > 0; PF ≥ 1.05; trades ≥ 150 (or justified lower)
- ≥ 4/7 validation pairs positive (or majority)
- 2× cost stress validation expectancy ≥ 0
- Beat C011 deduped null by +0.010R
- Financing overlay if average hold > 1 day
- Backtrader parity PASS before test lockbox

## Deliverables

- `CAMPAIGN_021_TRAIN_VALIDATION_RESULT.md`
- `CAMPAIGN_021_GATE_DECISION.md`
- `CAMPAIGN_021_BACKTRADER_PARITY_RESULT.md`
- Test lockbox doc only if gates + parity pass
- `CAMPAIGN_021_FINAL_INTERPRETATION.md`
- Update `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `STRATEGY_STATUS.md`

## Non-goals

- No M5 default execution in v1
- No M1-derived D1AGG
- No C020 verdict rewrite

# Strategy-Search Pause After USD_JPY Macro-Context 001 — Plan

**Sprint:** `strategy-search-pause-after-usdjpy-macro-context-001`
**Branch:** `research-strategy-search-pause-after-usdjpy-macro-context-001` (from the
macro-context tip `ea18edd`).
**Date:** 2026-05-28
**Status:** documentation / closeout only. **NOT** a strategy sprint, **NOT** a diagnostic
mining sprint, **NOT** CAMPAIGN_024, **NOT** C023, **NOT** approval, **NOT** paper/demo/live.

---

## 1. Purpose

Formally **pause strategy research** on the current data/thesis set, **preserve** the
valuable infrastructure, **document lessons learned**, and **define strict entry criteria**
for any future restart. No new analysis, no new mining, no new thesis. This sprint only
writes/updates documentation and (freeze-safely) status/backlog/index/manifest.

## 2. Scope

- Final pause memo (standing decision `PAUSE_STRATEGY_RESEARCH`).
- Status/backlog/index/manifest updates (no verdict → PASS; preserve `approved: []`).
- Lessons-learned + failure taxonomy.
- Restart criteria (sufficient vs insufficient triggers).
- Next-action options + one recommendation.
- Drafted next prompt (non-strategy: merge-readiness / external-data infra / external-thesis brief).
- Final validation + summary + merge-readiness.

## 3. Prior exhausted lanes (carried in — verified present)

- **Price-structure / technical / microstructure:** C022/C023 pullback family retired;
  USD_JPY microstructure **entry** lane closed; USD_JPY post-entry **trade-management** lane
  closed; volatility-compression→expansion broad thesis falsified; London
  compression-continuation lead failed overfit-hardened confirmation
  (`USDJPY_LONDON_COMPRESSION_CONTINUATION_READINESS_DECISION.md`).
- **Slow macro/rates/calendar tradeability-context:** correctly framed as slow context /
  no-trade filter; lookahead-safe + latency-independent; **no actionable edge** (flat raw
  spread, ~0.50 whipsaw, mechanical event-vol, non-identifiable rate-regime). Verdict
  `PAUSE_STRATEGY_RESEARCH` (`USDJPY_MACRO_REGIME_CONTEXT_READINESS_DECISION.md`).

## 4. Non-goals (explicit)

No CAMPAIGN_024; no C023 execution; no strategy; no campaign; no new diagnostic mining
lane; no verdict change; no metric rewrite; modify `approved_strategies.yaml` only to verify
`approved: []`; no paper/demo/live; no broker/executor/order/live changes; no OANDA
mutation/order calls; no live credentials; no committing `.env`/credentials/DBs/raw
candle dumps/parquet/huge CSVs; **no "one more indicator tweak"**; present **no** existing
lead as actionable.

## 5. Safety rules

Phased; commit after each meaningful phase. Documentation-only; no code that runs a
strategy/campaign. Compact artifacts only. TEST windows remain sealed. `.env` (if used at
all) only for read-only validation; credentials never printed.

## 6. Expected docs

| phase | artifact |
|---|---|
| 0 | this plan |
| 1 | `STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT.md` |
| 2 | updates to `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`, `FUTURE_RESEARCH_BACKLOG.md`, `EVIDENCE_MANIFEST.json` (freeze-safe) |
| 3 | `FOREX_BOT_RESEARCH_LESSONS_LEARNED_001.md` |
| 4 | `STRATEGY_RESEARCH_RESTART_CRITERIA.md` |
| 5 | `NEXT_ACTION_OPTIONS_AFTER_STRATEGY_SEARCH_PAUSE.md` |
| 6 | `NEXT_SPRINT_PROMPT_AFTER_STRATEGY_SEARCH_PAUSE.md` |
| 7 | `STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT_001_SUMMARY.md` |

## 7. Validation commands (Phase 0 baseline + Phase 7 final)

```
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

**Phase 0 baseline (2026-05-28):** pytest **2014 passed, 3 skipped** (pre-existing
data-absence: `test_cost_atlas` H4 store; 2× `test_compare_entries` C008 CSVs); ruff clean;
freeze/archive/secret gates **PASS**. `approved: []`; C023 not executed; C024 absent;
paper/demo loops refuse.

(Note: the prompt referenced `USDJPY_MACRO_REGIME_CONTEXT_001_SUMMARY.md`; the actual file
is `USDJPY_MACRO_REGIME_CONTEXT_TRADEABILITY_001_SUMMARY.md` — present and verified.)

## 8. Explicit no-C024 / no-C023 / no-approval / no-new-mining statement

This sprint creates **no** `CAMPAIGN_024`, executes **no** C023, implements **no** strategy,
runs **no** campaign, starts **no** new diagnostic mining lane, changes **no** verdict,
approves **no** strategy, and leaves paper/demo/live blocked with
`configs/approved_strategies.yaml` = `approved: []`. It is documentation + freeze-safe
status updates only, ending at a formal `PAUSE_STRATEGY_RESEARCH` standing decision and a
merge-readiness summary.

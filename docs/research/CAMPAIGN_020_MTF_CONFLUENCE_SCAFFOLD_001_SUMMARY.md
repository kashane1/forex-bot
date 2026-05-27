# CAMPAIGN_020 — MTF Confluence Scaffold Sprint Summary

**Date:** 2026-05-27  
**Branch:** `research-mtf-confluence-candidate-020-scaffold-001`  
**Verdict:** **SCAFFOLD_ONLY** — precommitted, not executed

## 1. Branch name

`research-mtf-confluence-candidate-020-scaffold-001`

## 2. Base branch / commit

`main` @ `fe34c4d` (`docs(research): record Phase 10 commit hash in sprint summary`)

## 3. Commit hashes by phase

| phase | commit | message |
|---|---|---|
| 0 | `4ff2ee5` | scaffold plan |
| 1 | `5482f26` | structural distinctness memo |
| 2 | `0655132` | precommit freeze |
| 3 | `61b5944` | strategy + config + YAML |
| 4 | `31da436` | unit tests |
| 5 | `8625744` | preflight runner |
| 6 | `1994588` | Backtrader parity design |
| 7 | `888e6a6` | execution sprint prompt |
| 8–9 | `5506ae8` | evidence index + summary |

## 4. Files changed by phase

| phase | primary files |
|---|---|
| 0 | `docs/research/CAMPAIGN_020_MTF_CONFLUENCE_SCAFFOLD_001_PLAN.md` |
| 1 | `docs/research/CAMPAIGN_020_STRUCTURAL_DISTINCTNESS_MEMO.md` |
| 2 | `docs/research/CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md` |
| 3 | `src/forex_bot/strategies/multi_timeframe_confluence_pullback.py`, `src/forex_bot/config.py`, `configs/campaign_020_mtf_confluence_pullback.yaml` |
| 4 | `tests/unit/test_multi_timeframe_confluence_pullback.py` |
| 5 | `scripts/run_campaign_020_mtf_confluence.py`, `research/campaign_020/*` |
| 6 | `docs/research/CAMPAIGN_020_BACKTRADER_PARITY_DESIGN.md` |
| 7 | `docs/research/NEXT_SPRINT_PROMPT_CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION.md` |
| 8 | `docs/research/EVIDENCE_*`, `STRATEGY_STATUS.md`, `FUTURE_RESEARCH_BACKLOG.md`, `src/forex_bot/research_archive.py` |
| 9 | this summary |

## 5. Baseline validation (Phase 0 / Phase 9)

| command | result |
|---|---|
| `pytest tests/ -q` | **PASS** (1789 tests after manifest update) |
| `ruff check src tests scripts research` | **WARN** — 12 pre-existing fixable issues in unrelated fill-timing scripts (not introduced by this sprint) |
| `python scripts/check_research_freeze.py` | **PASS** |
| `python scripts/validate_research_archive.py` | **PASS** (after CAMPAIGN_020 manifest entry) |
| `python scripts/scan_artifacts_for_secrets.py` | **PASS** |
| `git status --short` | clean after commits |

## 6. Structural distinctness

**STRUCTURALLY DISTINCT** — documented in `CAMPAIGN_020_STRUCTURAL_DISTINCTNESS_MEMO.md`. Not C008/C018/C019 exit variant; not C012/C013/C014/C015–C017 retune; differs from C007 by mandatory D1AGG confluence.

## 7. Precommitted strategy identity

`multi_timeframe_confluence_pullback` · `0.1.0-c020` · CAMPAIGN_020

## 8. Universe / timeframe

Seven majors (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF); execution **H4**; HTF **D1AGG**.

## 9. D1AGG / htf_align design

D1AGG from H4 via `aggregate_h4_to_d1`; EMA20/EMA50 on D1 mid close; aligned with `htf_align.align_last_completed` at H4 decision time; bullish/bearish structure per precommit.

## 10. H4 context rules

Long: `close > EMA50`; short: `close < EMA50`; ADX(14) ≥ 18.

## 11. Pullback trigger rules

6-bar pullback to EMA20 ± 0.5×ATR or RSI zone; trigger = EMA20 reclaim cross on completed bar.

## 12. Risk / exit model

ATR×2 hard stop; 24-bar time stop; no TP; no trailing (`hard_stop_or_time`).

## 13. Fill timing / execution realism

`research_metadata`: `fill_timing: next_bar_open`, `execution_realism: conservative`, `evidence_use: approval_bound`, `promotion_eligible: false`.

## 14. Financing declaration

`financing_mode: none`; `financing_overlay_required: true`; observed financing **blocked** pending practice sample.

## 15. Backtrader parity design

`CAMPAIGN_020_BACKTRADER_PARITY_DESIGN.md` — required before test lockbox in execution sprint; no historical parity run here.

## 16. Tests added

`tests/unit/test_multi_timeframe_confluence_pullback.py` — 16 tests (warmup, HTF, pullback, provenance, metadata, config, safety).

## 17. Preflight scaffold result

`python scripts/run_campaign_020_mtf_confluence.py --preflight-only` → `preflight_ok: true` (local DB present). See `CAMPAIGN_020_PREFLIGHT_SCAFFOLD_RESULT.md`.

## 18. Full evidence run?

**No.**

## 19. Train/validation/test verdict?

**None** — SCAFFOLD_ONLY.

## 20. Test lockbox opened?

**No.**

## 21. CAMPAIGN_020 approved?

**No.**

## 22. `approved_strategies.yaml` empty?

**Yes** — `approved: []`.

## 23. Paper/demo/live blocked?

**Yes.**

## 24. Executor/broker behavior changed?

**No.**

## 25. OANDA mutation APIs called?

**No.**

## 26. Live environment used?

**No.**

## 27. Credentials/secrets committed?

**No.**

## 28. Raw data / bulky artifacts staged?

**No** — only small JSON under `research/campaign_020/`.

## 29. C019 verdict unchanged?

**Yes** — REJECT.

## 30. Validation commands run

Listed in §5.

## 31. Remaining WARN / BLOCKED

| item | status |
|---|---|
| Ruff pre-existing in fill-timing comparison scripts | WARN (not sprint-introduced) |
| Observed financing capture | BLOCKED pending practice sample |
| Full CAMPAIGN_020 evidence | BLOCKED until execution sprint |
| Backtrader parity execution | BLOCKED until execution sprint |

## 32. Recommended next sprint

`research-campaign-020-mtf-confluence-execution-001` per `NEXT_SPRINT_PROMPT_CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION.md`.

### Review first

1. `docs/research/CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md`
2. `src/forex_bot/strategies/multi_timeframe_confluence_pullback.py`
3. `configs/campaign_020_mtf_confluence_pullback.yaml`
4. `docs/research/CAMPAIGN_020_STRUCTURAL_DISTINCTNESS_MEMO.md`
5. `tests/unit/test_multi_timeframe_confluence_pullback.py`

## Compact table

| Area | Decision | Files | Tests | Risk | Follow-up |
|---|---|---|---|---|---|
| Thesis | MTF confluence pullback (new family) | strategy module, precommit doc | 16 unit tests | Low — scaffold only | Execution sprint |
| HTF | D1AGG + `htf_align`, no incomplete bars | `multi_timeframe_confluence_pullback.py`, `d1agg_htf` | HTF time ≤ decision | Lookahead if align bypassed | Parity lane |
| Fill | `next_bar_open` approval-bound | campaign YAML `research_metadata` | metadata validation | Optimistic fill if changed | Engine FillModel in execution |
| Evidence | SCAFFOLD_ONLY | manifest, index, status | archive validator ×19 | False promotion | Train/val gates |
| Safety | No approval, no broker | runner refuses `--execute-evidence` | broker import grep | Live if misconfigured | Keep `approved: []` |

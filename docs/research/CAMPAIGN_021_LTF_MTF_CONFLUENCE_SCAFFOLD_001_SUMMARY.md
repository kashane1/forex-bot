# CAMPAIGN_021 — LTF MTF Confluence Scaffold Sprint Summary

**Date:** 2026-05-27  
**Branch:** `research-campaign-021-ltf-mtf-confluence-scaffold-001`  
**Verdict:** **SCAFFOLD_ONLY** — precommitted, not executed

## 1. Branch name

`research-campaign-021-ltf-mtf-confluence-scaffold-001`

## 2. Base branch / commit

`main` @ `b0f92e5` (after merge of `infra-m1-full-corpus-validation-and-aggregation-001`)

## 3. Commit hashes by phase

| phase | commit | message |
|---|---|---|
| 0 | `eeb236e` | scaffold plan |
| 1 | `49ab2b6` | structural distinctness memo |
| 2 | `67fede3` | precommit freeze |
| 3 | `1c7a174` | strategy + config + YAML |
| 4 | `3e3cf09` | unit tests |
| 5 | `58283d4` | preflight runner |
| 6 | `349fe5c` | Backtrader parity design |
| 7 | `72c7aaa` | execution sprint prompt |
| 8 | `d068116` | evidence index + status |
| 9 | `590898e` | scaffold close-out summary |

## 4. Files changed by phase

| phase | primary files |
|---|---|
| 0 | `docs/research/CAMPAIGN_021_LTF_MTF_CONFLUENCE_SCAFFOLD_001_PLAN.md` |
| 1 | `docs/research/CAMPAIGN_021_STRUCTURAL_DISTINCTNESS_MEMO.md` |
| 2 | `docs/research/CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md` |
| 3 | `src/forex_bot/strategies/lower_timeframe_mtf_confluence_entry.py`, `src/forex_bot/config.py`, `configs/campaign_021_ltf_mtf_confluence.yaml`, `src/forex_bot/strategies/__init__.py` |
| 4 | `tests/unit/test_lower_timeframe_mtf_confluence_entry.py` |
| 5 | `scripts/run_campaign_021_ltf_mtf_confluence.py`, `research/campaign_021/preflight_result.json` |
| 6 | `docs/research/CAMPAIGN_021_BACKTRADER_PARITY_DESIGN.md` |
| 7 | `docs/research/NEXT_SPRINT_PROMPT_CAMPAIGN_021_LTF_MTF_CONFLUENCE_EXECUTION.md` |
| 8 | `docs/research/EVIDENCE_*`, `STRATEGY_STATUS.md`, `FUTURE_RESEARCH_BACKLOG.md` |
| 9 | this summary |

## 5. Baseline validation (Phase 0 / Phase 9)

| command | result |
|---|---|
| `pytest tests/ -q` | **PASS** (1849 tests after summary commit) |
| `ruff check src tests scripts research` | **WARN** — pre-existing fixable issues in unrelated fill-timing scripts (not introduced by this sprint) |
| `python scripts/check_research_freeze.py` | **PASS** (after summary indexed) |
| `python scripts/validate_research_archive.py` | **PASS** (after summary indexed) |
| `python scripts/scan_artifacts_for_secrets.py` | **PASS** |
| `git status --short` | clean after commits |

## 6. Structural distinctness

**STRUCTURALLY DISTINCT** — `CAMPAIGN_021_STRUCTURAL_DISTINCTNESS_MEMO.md`. M15 execution + H1 tactical gate + M1-canonical frames; not C020 H4 retune; not C008–C019/C012–C017 families.

## 7. Precommitted strategy identity

`lower_timeframe_mtf_confluence_entry` · `0.1.0-c021` · CAMPAIGN_021

## 8. Universe / timeframe

Seven majors; execution **M15**; context **H1, H4, D1AGG**.

## 9. Data provenance design

| layer | source |
|---|---|
| M15 / H1 / H4 | M1-derived (Postgres canonical corpus) |
| D1AGG | **native_h4_derived_d1agg** only |
| M1-derived D1AGG | forbidden (`validate_c021_data_provenance`) |

## 10. D1AGG hybrid decision

Use native H4→D1AGG until M1→D1AGG day completeness is repaired (M1 full-corpus validation: M1-D1AGG empty). Enforced in YAML, strategy validator, and preflight.

## 11. H1 / H4 context rules

- H4: close vs EMA50 bullish/bearish
- H1: close vs EMA20 + EMA20 slope over 3 completed H1 bars
- D1AGG: EMA20/EMA50 structure (shared classifier with C020 family)

## 12. M15 trigger rules

8-bar pullback touch to EMA20/50; reclaim = close crosses EMA20 in trend direction; ADX(14) ≥ 18.

## 13. Risk / exit model

2.0× M15 ATR(14) hard stop; 32 M15-bar time stop (~8h); no TP; no trailing (`hard_stop_or_time`).

## 14. Fill timing / execution realism

`research_metadata`: `fill_timing: next_bar_open`, `execution_realism: conservative`, `evidence_use: approval_bound`, `promotion_eligible: false`.

## 15. Financing declaration

`financing_mode: none`; `financing_overlay_required: true`; observed financing blocked pending practice sample.

## 16. Backtrader parity design

`CAMPAIGN_021_BACKTRADER_PARITY_DESIGN.md` — required before test lockbox in execution sprint; no historical parity run in scaffold.

## 17. Tests added

`tests/unit/test_lower_timeframe_mtf_confluence_entry.py` — 16 tests (provenance, warmup, pullback/reclaim, provenance fields, metadata, config, broker safety).

## 18. Preflight scaffold result

`python scripts/run_campaign_021_ltf_mtf_confluence.py --preflight-only` → `preflight_ok: true` (7 M1 pairs PASS; 69,648 native H4 rows). See `CAMPAIGN_021_PREFLIGHT_SCAFFOLD_RESULT.md`.

## 19. Full evidence run?

**No.**

## 20. Train/validation/test verdict?

**None** — SCAFFOLD_ONLY.

## 21. Test lockbox opened?

**No.**

## 22. CAMPAIGN_021 approved?

**No.**

## 23. `approved_strategies.yaml` empty?

**Yes** — `approved: []`.

## 24. Paper/demo/live blocked?

**Yes.**

## 25. Executor/broker behavior changed?

**No.**

## 26. OANDA mutation APIs called?

**No.**

## 27. Live environment used?

**No.**

## 28. Credentials/secrets committed?

**No.**

## 29. Raw M1/DB/bulky artifacts staged?

**No** — only compact `research/campaign_021/preflight_result.json`.

## 30. C020 verdict unchanged?

**Yes** — REJECT.

## 31. Validation commands run

Listed in §5.

## 32. Remaining WARN / BLOCKED

| item | status |
|---|---|
| M1 corpus quality | WARN (calendar FX gaps; 0 duplicates) |
| M1-derived D1AGG | BLOCKED for C021 until day completeness repair |
| Ruff pre-existing fill-timing scripts | WARN (not sprint-introduced) |
| CAMPAIGN_021 train/validation evidence | BLOCKED until execution sprint |
| Backtrader parity execution | BLOCKED until execution sprint |

## 33. Recommended next sprint

`research-campaign-021-ltf-mtf-confluence-execution-001` per `NEXT_SPRINT_PROMPT_CAMPAIGN_021_LTF_MTF_CONFLUENCE_EXECUTION.md`.

### Review first

1. `docs/research/CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md`
2. `src/forex_bot/strategies/lower_timeframe_mtf_confluence_entry.py`
3. `configs/campaign_021_ltf_mtf_confluence.yaml`
4. `docs/research/CAMPAIGN_021_STRUCTURAL_DISTINCTNESS_MEMO.md`
5. `tests/unit/test_lower_timeframe_mtf_confluence_entry.py`

## Compact table

| Area | Decision | Files | Tests | Risk | Follow-up |
|---|---|---|---|---|---|
| Thesis | LTF MTF confluence entry (new vs C020) | strategy module, precommit | 16 unit tests | Low — scaffold only | Execution sprint |
| Data | M1 M15/H1/H4 + native D1AGG | campaign YAML `data_provenance` | provenance validator | Wrong D1AGG source | Preflight guard |
| HTF | `htf_align` on H1/H4/D1AGG | strategy + alignment helpers | HTF time ≤ decision | Lookahead if bypassed | Parity lane |
| Fill | `next_bar_open` approval-bound | `research_metadata` | metadata validation | Optimistic fill if changed | Engine in execution |
| Evidence | SCAFFOLD_ONLY | manifest, index, status | archive + freeze gates | False promotion | Train/val gates |
| Safety | No approval, no broker | runner blocks evidence cmds | import grep | Live if misconfigured | Keep `approved: []` |

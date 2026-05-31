# CAMPAIGN_023 — ADX22 Sibling Scaffold Sprint Summary

**Date:** 2026-05-27
**Branch:** `claude/loving-hawking-7ab830`
**Verdict:** **SCAFFOLD_ONLY** — precommitted, not executed

## 1. Identity

`h4_h1_pullback_resolution_entry` · `0.1.0-c023` · CAMPAIGN_023 ·
working name **H4/H1 Pullback Resolution Entry — ADX22** · `promotion_eligible: false`.

## 2. The single intentional delta vs CAMPAIGN_022

| campaign | H4 ADX(14) bias gate |
|---|---|
| CAMPAIGN_022 | `h4_adx_min >= 20.0` |
| CAMPAIGN_023 | `h4_adx_min >= 22.0` |

Held constant (verified by `test_yaml_strategy_block_identical_except_threshold`):
pairs, execution timeframe (M15), context timeframes (H4/H1), no-D1/no-D1AGG scope,
M15 trigger, H1 pullback-holds logic, stop (2.0×M15 ATR14), time stop (32 bars),
spread/session filters, execution realism (`next_bar_open` / conservative), financing
mode (`none`), gates, no-lookahead rules, approved strategies (`[]`), broker/executor
behavior. The two campaigns share **one** strategy class.

## 3. Pre-registration, not post-hoc tuning

C022 is PRECOMMITTED_NOT_EXECUTED — no C022 train/validation/test evidence exists or
was viewed (C022 has no entry in the validated `campaigns` array of
`EVIDENCE_MANIFEST.json`; freeze + archive validators PASS with no C022 verdict).
Choosing ADX22 before any results exist is a pre-registered sensitivity arm. The
`BLOCKED_CONTAMINATED_BY_PRIOR_RESULTS` guard in the precommit does **not** trigger.

> **Update — 2026-05-28.** This section reflects the state when authored (2026-05-27). A
> separate, concurrent CAMPAIGN_022 *execution* sprint has since run C022 to a **REJECT**
> on the same branch, in parallel. Because the ADX22 arm was frozen before any C022
> results existed/were viewed, C023 remains a genuine pre-registration. C023 itself is
> still `SCAFFOLD_ONLY` / unexecuted; C022 is now REJECT (see `STRATEGY_STATUS.md`).

## 4. Branch

`claude/loving-hawking-7ab830` (checked out in worktree
`.claude/worktrees/loving-hawking-7ab830`).

## 5. Commit hashes by phase

| phase | hash | subject |
|---|---|---|
| 0 | `2de981a` | plan doc + C022 baseline audit |
| 1 | `2338ee9` | C023 ADX22 precommit |
| 2 | `4cda3ee` | C023 frozen config YAML |
| 3 | `71cbced` | parameterize `campaign_id` in shared strategy |
| 4 | `7694036` | C023 ADX22 sibling tests |
| 5 | `c7c0ca7` | C023 preflight-only runner |
| 6 | `f54c3e4` | docs/status/archive registration |
| 7 | _this commit_ | final validation + summary + test lint fix |

## 6. Files changed by phase

- **Phase 0:** `docs/research/CAMPAIGN_023_ADX22_SIBLING_PLAN.md` (new).
- **Phase 1:** `docs/research/CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md` (new).
- **Phase 2:** `configs/campaign_023_h4_h1_pullback_resolution_adx22.yaml` (new).
- **Phase 3:** `src/forex_bot/strategies/h4_h1_pullback_resolution_entry.py`
  (`campaign_id` constructor param, default `CAMPAIGN_022`; shared by C022/C023).
- **Phase 4:** `tests/unit/test_h4_h1_pullback_resolution_adx22.py` (new, 13 tests).
- **Phase 5:** `scripts/run_campaign_023_h4_h1_pullback_resolution_adx22.py` (new).
- **Phase 6:** `docs/research/EVIDENCE_INDEX.md`, `docs/research/EVIDENCE_MANIFEST.json`,
  `docs/research/STRATEGY_STATUS.md`, `docs/research/FUTURE_RESEARCH_BACKLOG.md`.
- **Phase 7:** this summary; `EVIDENCE_INDEX.md` summary link; test lint fix.

## 7. Tests

`tests/unit/test_h4_h1_pullback_resolution_adx22.py` — 13 tests: C023 config loads,
version `0.1.0-c023`, trading disabled, M1-derived M15/H1/H4 provenance, rejects
D1/D1AGG keys, H4 bias **blocks at ADX 21.9** and **passes at ADX 22.0** (C022 still
passes at 20.0 on identical data), threshold is the sole discriminator in the full
strategy path, above-gate signals identical except `campaign_id`/`version`, YAML
strategy block differs only by `h4_adx_min` + `version`, no broker/OANDA imports,
approved registry empty. **PASS.** Combined C022 + C023 unit suites: **35 passed.**

Full suite: `pytest tests/ -q` → **1889 passed, 1 skipped, 1 failed**. The single
failure (`tests/unit/entry_parity/test_compare_entries.py::test_c008_entry_comparison_runs`)
is a **pre-existing worktree-data condition** (untracked `research/` parity artifacts
absent in this worktree; passes on a full main checkout) — documented in the C022
scaffold summary and **not introduced by CAMPAIGN_023**.

## 8. Validation commands run

| command | result |
|---|---|
| `pytest tests/ -q` | 1889 passed, 1 skipped, 1 pre-existing failure |
| `ruff check src tests scripts research` | C023 files clean; 18 pre-existing errors in unrelated files |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED (no credential-shaped strings) |
| `git status --short` | only intended C023 changes + pre-existing C021 modifications |

## 9. Confirmations

- **C023 differs from C022 only by the H4 ADX threshold (22 vs 20)** — enforced by tests.
- **No evidence was run** — no train/validation/test; runner is preflight-only and blocks
  execution subcommands (exit 2); test lockbox never opened.
- **No strategy is approved** — `configs/approved_strategies.yaml` remains `approved: []`.
- **Paper/demo/live remain blocked** — C023 YAML `mode: paper`, `trading_enabled: false`,
  `allow_order_submission: false`, `allow_live_trading: false`.
- **No broker/executor/OANDA/order/account/position imports** in strategy code
  (`test_strategy_no_broker_imports`).

## 10. Blockers / deviations (documented honestly)

1. **C022 scaffold was found uncommitted** on this branch (untracked strategy/YAML/docs/
   tests; modified `config.py` and `strategies/__init__.py`). The branch working tree is
   the source of truth. C023 reuses C022's strategy class and config model in place; the
   C023 commits add only C023 artifacts plus the minimal shared `campaign_id`
   parameterization. C022's own files and unrelated CAMPAIGN_021 working changes
   (`lower_timeframe_mtf_confluence_entry.py`, its test, `ledger_inventory_used.json`)
   were left untouched and are **not** staged by this sprint. Consequence: a fresh
   checkout of the C023 commits depends on C022's config model still living in the
   working tree until C022 is itself committed.
2. **Pre-existing full-suite failure** (`test_c008_entry_comparison_runs`) and **18
   pre-existing ruff errors** in unrelated files — neither introduced by C023.
3. **EVIDENCE_MANIFEST.json**: C023 was added as a descriptive top-level section
   (`campaign_023_adx22_sibling`), **not** in the validated `campaigns` array, because a
   no-evidence scaffold cannot satisfy the report/folder/verdict checks — this matches the
   C021 precedent and keeps the freeze green.

## 11. Exact files to review first

1. [`CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md`](CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md)
2. [`../../configs/campaign_023_h4_h1_pullback_resolution_adx22.yaml`](../../configs/campaign_023_h4_h1_pullback_resolution_adx22.yaml)
3. [`../../src/forex_bot/strategies/h4_h1_pullback_resolution_entry.py`](../../src/forex_bot/strategies/h4_h1_pullback_resolution_entry.py) (`campaign_id` param)
4. [`../../tests/unit/test_h4_h1_pullback_resolution_adx22.py`](../../tests/unit/test_h4_h1_pullback_resolution_adx22.py)
5. [`../../scripts/run_campaign_023_h4_h1_pullback_resolution_adx22.py`](../../scripts/run_campaign_023_h4_h1_pullback_resolution_adx22.py)

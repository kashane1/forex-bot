# CAMPAIGN_025 — M5 Donchian + HTF confluence breakout (SCAFFOLD_001 plan)

**Branch:** `research-campaign-025-m5-donchian-htf-confluence-scaffold-001`
**Date:** 2026-05-28
**Status after this sprint:** `SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED`

> This is a **scaffold/precommit sprint only**. No full historical evidence is
> run, no tuning after results, no strategy approval, no paper/demo/live, no
> executor/broker changes, no OANDA mutation/order endpoints, no live
> credentials. The test lockbox stays closed.

---

## Purpose

Stand up a fully pre-committed research scaffold for a lower-timeframe
price-action strategy — **`m5_donchian_htf_confluence_breakout 0.1.0-c025`** —
that places a Donchian breakout *trigger* on M5 execution bars but only fires
when higher timeframes (M15 setup, H1/H4 trend, D1AGG regime) agree.

The sprint produces: a frozen precommit spec, a deterministic research strategy
module, a campaign config, a registry entry, a data-feature preflight runner, a
Backtrader parity design stub, and a distinctness memo — but **no evidence run**.

## Strategy thesis

The earliest Donchian/breakout campaign idea (CAMPAIGN_002 family lineage) was
plausibly *too blunt*: a raw H4 channel break across all seven majors with no
trend/regime gate and optimistic fills. The thesis here is that the breakout is
a sound **price-action trigger** but needs (a) a finer execution timeframe so
the entry is precise, and (b) multi-timeframe agreement so the trigger only
fires inside a supportive trend/regime.

C025 therefore:
1. Uses **H4M1 + H1** to define directional context.
2. Uses **M15** to require local pullback/compression structure (anti-chasing).
3. Uses an **M5 Donchian breakout** as the execution trigger.
4. Uses a **D1AGG** (native-H4-derived) regime filter.
5. Uses an **ATR-based initial stop** and a **time stop** only — no target, no
   trailing, no protective stop.
6. Uses **`next_bar_open`** fills only.

## Why this is distinct from rejected H4/broad campaigns

- **Vs. blunt H4 Donchian (early breakout idea / CAMPAIGN_002 lineage):** the
  breakout *trigger* moves from H4 to **M5**, so entries are precise rather than
  whole-H4-bar coarse, and the H4 channel is replaced by an H4 *trend* gate.
- **Vs. broad seven-pair pattern search (C012, C013, C015–C017):** C025 does
  **not** assume a universal seven-pair edge. The runner reports **pair-level
  diagnostics**, and a future single-pair continuation is allowed **only** if
  pre-committed and justified *before* test evidence.
- **Vs. turnover-amplification failures:** a **pullback/compression precondition
  on M15** is required before any breakout, and trade frequency + spread/ATR
  ratio are tracked, so this is not high-turnover breakout chasing.
- **Vs. optimistic-fill lineage:** **`next_bar_open` only**; no `signal_bar_close`,
  no same-bar entry on the signal bar.
- **Vs. C020/C021 (MTF confluence on M15/H4):** keeps the MTF + `align_last_completed`
  discipline and materialized M1-derived lower timeframes, but the *execution*
  timeframe drops to **M5** and the *trigger* is a Donchian channel break rather
  than an EMA20-reclaim pullback.

## Data provenance

| Stream  | Timeframe | Source |
|---------|-----------|--------|
| Execution | M5     | materialized M1-derived Postgres bars (`source=m1_materialized`) |
| Local setup | M15  | materialized M1-derived Postgres bars |
| Trend context | H1 | materialized M1-derived Postgres bars |
| Trend context | H4 (H4M1) | materialized M1-derived Postgres bars |
| Macro regime | D1AGG | **native H4-derived** aggregation (`native_h4_derived_d1agg`) |

M1-derived D1AGG is **not** used until M1→D1AGG day-completeness is fixed.
M1-derived H4 (H4M1) verification passed with **0 OHLC mismatches** in the
materialization sprint; native H4 remains available for D1AGG aggregation.

## Scaffold-only scope (this sprint)

- Precommit spec doc (frozen rules + gates).
- Deterministic research strategy module + unit tests.
- Campaign config + registry entries.
- `--preflight-only` / `--data-feature-preflight` runner (+ optional tiny
  `--sample-signals-only` bounded window).
- Backtrader parity **design** stub.
- Distinctness + prior-lessons memo.
- Scaffold validation + summary.

## Non-goals (this sprint)

- No full historical evidence run.
- No train/validation/test evidence; **test lockbox stays closed**.
- No tuning after results; no gate changes after results.
- No strategy approval; no promotion-review classification.
- No paper/demo/live; no executor/broker change; no OANDA order/trade/position/
  transaction/live endpoints; no live credentials.

## Safety invariants

- `configs/approved_strategies.yaml` remains `approved: []`.
- Paper/demo/live loops keep refusing every configured strategy.
- Strategy module imports **no** broker/executor/OANDA code.
- No `.env`, credentials, SQLite, raw candle data, or bulky artifacts committed.
- HTF context uses **last-completed** bars only via `align_last_completed`.
- Fills are **`next_bar_open`** only.

## Expected artifacts

- `docs/research/CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_PLAN.md` (this)
- `docs/research/CAMPAIGN_025_PRECOMMIT_M5_DONCHIAN_HTF_CONFLUENCE_SCOPE.md`
- `src/forex_bot/strategies/m5_donchian_htf_confluence_breakout.py`
- `src/forex_bot/research/campaign_025_loader.py`
- `src/forex_bot/research/campaign_025_gates.py`
- `tests/unit/test_m5_donchian_htf_confluence_breakout.py`
- `configs/campaign_025_m5_donchian_htf_confluence_breakout.yaml`
- `scripts/run_campaign_025_m5_donchian_htf_confluence.py`
- `docs/research/CAMPAIGN_025_BACKTRADER_PARITY_DESIGN.md`
- `docs/research/CAMPAIGN_025_DISTINCTNESS_AND_PRIOR_LESSONS_MEMO.md`
- `docs/research/CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_SUMMARY.md`
- `research/campaign_025/preflight/*.json` (compact preflight artifacts)
- Registry updates: `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`,
  `EVIDENCE_MANIFEST.json`, `FUTURE_RESEARCH_BACKLOG.md`.

## Validation commands

```
pytest tests/ -q
ruff check .
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/run_campaign_025_m5_donchian_htf_confluence.py --preflight-only
python scripts/run_campaign_025_m5_donchian_htf_confluence.py --data-feature-preflight
```

## Blocked conditions

- If materialized M5/M15/H1/H4M1 coverage is unavailable for a pair, the
  preflight records `BLOCKED_DATA_PRECONDITION` for that pair instead of
  improvising or falling back silently.
- If D1AGG is unavailable/stale at a decision, **no trade** is allowed.
- If data loading cannot run at all, the sprint documents
  `BLOCKED_DATA_PRECONDITION` and stops rather than fabricating coverage.

## Baseline audit (Phase 0) result

- Branch renamed to `research-campaign-025-m5-donchian-htf-confluence-scaffold-001`;
  worktree clean; based on `origin/main`.
- M1-derived materialization infra present (`scripts/materialize_m1_derived_timeframes.py`,
  `scripts/verify_m1_materialized_coverage.py`,
  `src/forex_bot/data/m1_timeframe_materialization.py`); `STORAGE_GRANULARITY`
  covers M5/M15/H1/H4; native H4→D1AGG aggregation available via
  `forex_bot.backtesting.d1_aggregation.aggregate_h4_to_d1`.
- `configs/approved_strategies.yaml` = `approved: []`; paper/demo loops refuse.
- Baseline validation: **pytest 1996 passed / 3 skipped**, **ruff clean**,
  research-freeze **PASS**, research-archive **PASS**, secret scan **PASS**.

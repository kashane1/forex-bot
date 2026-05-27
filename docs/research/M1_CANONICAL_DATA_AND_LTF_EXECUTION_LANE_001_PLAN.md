# M1 Canonical Data And LTF Execution Lane 001 Plan

**Branch:** `infra-m1-canonical-data-and-ltf-execution-lane-001`
**Base:** `main` at `96074058ac40fa570a8fe91cdfaa35a20f1a98a4`
**Scope:** infrastructure only. No CAMPAIGN_021 evidence, no C020 rerun, no strategy verdict, no strategy approval, no paper/demo/live enablement, no broker mutation calls.

## Purpose

Build a lower-timeframe research lane whose raw source of truth is OANDA practice M1 bid/ask candles stored locally, with M5, M15, H1, H4, and D1AGG generated from M1 for internal consistency. Future candidates can then use M15 by default, M5 optionally, and H1/H4/D1AGG context through the existing completed-bar HTF alignment policy.

## Non-Goals

- Do not create or execute CAMPAIGN_021 evidence.
- Do not rerun CAMPAIGN_020 evidence.
- Do not tune strategy parameters.
- Do not approve any strategy or edit `configs/approved_strategies.yaml`.
- Do not enable paper, demo, or live loops.
- Do not submit, create, close, modify, cancel, or replace broker orders.
- Do not call OANDA order, trade, or position mutation endpoints.
- Do not use live OANDA credentials or hosts.
- Do not commit SQLite databases, Postgres dumps, raw M1 exports, bulky candle data, raw broker payloads, credentials, account IDs, tokens, or authorization headers.

## Safety Rules

All OANDA access in this lane, if executed at all, must be practice-only and restricted to read-only candle endpoints. The ingestion tooling must default to dry run and require an explicit execution flag before any network call. Missing credentials or store configuration must stop as `BLOCKED_READONLY_CREDENTIALS`, `BLOCKED_LOCAL_STORE`, or a more specific local blocker.

`configs/approved_strategies.yaml` was verified as `approved: []`. `check_research_freeze.py` verified paper/demo loop refusal and no strategy approvals. Live trading remains unavailable and out of scope.

## Why H4-Entry-Only Research Is Paused

CAMPAIGN_020 continued the pattern seen in earlier families: train-negative but validation-positive behavior on H4 entries. This suggests H4-only execution may be too blunt for entry timing, and that future research should separate lower-timeframe execution precision from higher-timeframe context instead of extending the current H4-entry campaign lane.

## C020 Result Summary

- Strategy: `multi_timeframe_confluence_pullback 0.1.0-c020`
- Execution timeframe: H4
- HTF: D1AGG via `htf_align`
- Fill timing: `next_bar_open`
- Train: 353 trades, expectancy `-0.035R`
- Validation: 204 trades, expectancy `+0.053R`
- Validation 2x stress: `+0.049R`
- Gate decision: train gate failed, runner stopped, test lockbox unopened
- Verdict: REJECT
- Approval: none; `configs/approved_strategies.yaml` remains `approved: []`

## M1 Canonical Data Thesis

For lower-timeframe research, broker-native H4 mixed with locally generated M15/H1 can introduce subtle convention mismatches. M1 should become the canonical raw source, and all generated research timeframes should be derived locally where possible. Native H4 historical research remains intact and old campaign verdicts are not rewritten.

## Target Timeframes

| Layer | Timeframes | Initial Policy |
| --- | --- | --- |
| Raw source | M1 | OANDA practice bid/ask candles only |
| Execution | M15 default, M5 supported | Future evidence must preserve `next_bar_open` on execution timeframe |
| Context | H1, H4, D1AGG | Future features must use `htf_align.align_last_completed` |

## Existing Modules Inspected

- OANDA candle client: `src/forex_bot/broker/oanda.py`
- Existing read-only Postgres ingestion: `scripts/ingest_oanda_candles_postgres.py`
- Postgres candle store: `src/forex_bot/data/postgres_candle_store.py`
- Candle domain model: `src/forex_bot/domain/candles.py`
- Deduping policy: `src/forex_bot/data/candle_dedupe.py`
- D1AGG aggregation: `src/forex_bot/backtesting/d1_aggregation.py`
- HTF alignment: `src/forex_bot/features/htf_align.py`
- D1AGG HTF helpers: `src/forex_bot/features/d1agg_htf.py`

## Expected Modules

- `src/forex_bot/data/timeframe_aggregation.py`
- `src/forex_bot/features/ltf_htf_alignment.py`
- `src/forex_bot/backtesting/ltf_preflight.py`
- `scripts/ingest_oanda_m1_candles.py`
- `scripts/validate_m1_canonical_store.py`

## Expected Tests

- Synthetic M1 aggregation to M5, M15, H1, H4, and D1AGG
- Missing and incomplete source-minute handling
- Bid/ask OHLC and spread preservation
- No weekend synthetic fill
- Practice-only read-only ingestion safety
- Data-quality findings for missing, duplicate, incomplete, and negative-spread candles
- M5/M15 execution decisions aligned only to completed H1/H4/D1AGG context
- Lower-timeframe backtest preflight preserving `next_bar_open` and execution-bar time-stop semantics

## Blocked Conditions

- `BLOCKED_READONLY_CREDENTIALS`: practice read-only credentials are absent.
- `BLOCKED_LOCAL_STORE`: local durable store is absent or unsafe.
- `BLOCKED_DATE_RANGE`: requested ingestion range is missing or too large for bounded chunked ingestion.
- `BLOCKED_ENDPOINT_SAFETY`: a URL, host, or endpoint is not explicitly allowlisted.

## Baseline Validation

| Command | Result |
| --- | --- |
| `pytest tests/ -q` | PASS, 1789 passed |
| `ruff check src tests scripts research` | FAIL, 14 pre-existing lint findings |
| `python scripts/check_research_freeze.py` | PASS |
| `python scripts/validate_research_archive.py` | PASS |
| `python scripts/scan_artifacts_for_secrets.py` | PASS, value scan skipped because no real OANDA credentials were in environment |
| `git status --short` | clean after reverting test-generated timestamp metadata |

## Explicit No-Approval Statement

This sprint creates infrastructure only. It does not produce strategy evidence, does not create a strategy verdict, does not approve any strategy, and does not unblock paper/demo/live operation.

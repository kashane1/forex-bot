# Candle Aggregation and Timestamp Audit — Result

**Sprint:** Shared Signal and MTF Confluence Audit 001 · Phase 1  
**Branch:** `infra-shared-signal-and-mtf-confluence-audit-001`  
**Classification:** **PASS** (with documented scope limits)

## Files inspected

| Path | Role |
|------|------|
| `src/forex_bot/domain/candles.py` | `Candle`, `CandleFrame`, granularity literals (`D` vs `D1AGG`) |
| `src/forex_bot/data/candle_dedupe.py` | UTC dedupe `keep_last` at load boundary |
| `src/forex_bot/backtesting/d1_aggregation.py` | H4 → `D1AGG` synthetic daily |
| `src/forex_bot/data/repositories.py` | Candle persistence / load |
| `src/forex_bot/broker/oanda.py` | Broker candle fetch |
| `src/forex_bot/loops.py` | Live fetch path |
| `docs/research/D1_AGGREGATION_DESIGN.md` | D1AGG timestamp rationale |
| `tests/unit/test_d1_aggregation.py` | H4→D1AGG OHLC, blackout, incomplete days |
| `tests/unit/test_candle_repo_dedupe.py` | Dedupe policy |
| `tests/unit/test_candle_conventions_audit_001.py` | Frame index, `completed_only`, dedupe (new) |

## Timestamp convention found

| Topic | Convention |
|-------|------------|
| Storage index | `CandleFrame` indexes rows by `Candle.time` (tz-aware UTC after load) |
| OANDA H4/M1/etc. | Broker-sourced; `time` is the candle **period timestamp** as returned by OANDA (project standard: NY `daily_alignment=17`, documented in campaign preflights) |
| `D1AGG` | **Close time of research day = 13:00 NY** (sixth H4 open), deliberately **not** OANDA native D1 open-at-17:00 |
| Native `D` | Marked invalid for backtests (rollover blackout + spread); must not be used for research |

`CandleFrame` docstring states the DataFrame is indexed by candle time; strategies use `df.index[-1]` as the decision bar timestamp. This matches bar-close signal semantics when the engine passes `window = df.iloc[:i+1]` on completed bars only.

## Completed-candle policy

- `Candle.complete` is stored from broker/API.
- Strategies call `ctx.candles.completed_only()` before indicators (e.g. `regime_switcher_atr_percentile`, weekly strategies).
- `aggregate_h4_to_d1` skips `complete=False` H4 rows.
- Incomplete days → classified `incomplete` / `ambiguous`; **no silent emit**.

## Aggregation behavior

| Path | Implementation |
|------|----------------|
| M1 → H1 → H4 → D1 | **Not implemented locally** — campaigns use broker-stored H4 (and native granularities where fetched) |
| H4 → D1AGG | `aggregate_h4_to_d1` — only in-repo multi-bar aggregation for daily research |
| H4 → weekly | `features/weekly_momentum.py`, `features/weekly_volatility.py` — strategy-layer weekly bars from completed H4 |
| Weekend gaps | Not filled with synthetic prices; missing weekdays reported in D1AGG result |
| Duplicate timestamps | `dedupe_candles` — `keep_last`, monotonic UTC |

## Tests added

- `tests/unit/test_candle_conventions_audit_001.py` (3 tests)

Existing evidence: `tests/unit/test_d1_aggregation.py`, `tests/unit/test_candle_repo_dedupe.py`.

## Findings

1. **PASS:** D1AGG aggregation is well-tested, documented, and excludes incomplete H4 and rollover-adjacent sixth bar.
2. **PASS:** Dedupe policy is explicit and tested.
3. **WARN (scope):** No generic 1m/H1 resampling layer — reliance on OANDA alignment is an **assumption** audited at broker-fetch scripts, not re-proven here with live API.
4. **WARN:** `CandleFrame.from_candles` derives mid OHLC from bid/ask when mid missing — acceptable for indicators but strategies using bid/ask directly should not assume mid was broker-native.

## Campaign validity risk

- Campaigns using **native OANDA `D`** would be invalid; repo blocks via design/docs (CAMPAIGN_006).
- Campaigns using **D1AGG** depend on correct H4 store + aggregation; infrastructure risk is **low** given existing tests.
- **H4 timestamp misalignment** (DST / dual-offset duplicates) mitigated by `dedupe_candles` at load — CAMPAIGN_011+ deduped baselines documented separately.

## Classification

**PASS** for in-repo aggregation and complete-flag handling. **WARN** for broker-sourced sub-H4 granularities (no local resampling tests).

# Free / Local Parity Verifier — Sprint-004 Rounding Audit

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-004-rounding-closure`
**Phase:** 1 · `strategy_evidence: false`

A read-only audit of bespoke instrument metadata, sizing, fill,
trailing-stop, and PnL precision, compared against the free / local
verifier. Output: a mismatch table and the minimum verifier-side
fixes to close the gap. **No code changes this phase.**

> No strategy approved. CAMPAIGN_002 remains REJECT. The bespoke
> engine is read-only this phase — no modification.

## 1. Bespoke instrument metadata (source of truth)

Captured by a read-only `SELECT` against
`/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (the same
file Sprint 003 used; no fetch, no API call):

| instrument | display_precision | pip_location | pip_size | trade_units_precision |
|---|---|---|---|---|
| EUR_USD | 5 | −4 | 0.00001 → bespoke; **0.0001 = pip** | 0 |
| GBP_USD | 5 | −4 | (same) | 0 |
| AUD_USD | 5 | −4 | (same) | 0 |
| USD_CAD | 5 | −4 | (same) | 0 |
| USD_CHF | 5 | −4 | (same) | 0 |
| NZD_USD | 5 | −4 | (same) | 0 |
| USD_JPY | 3 | −2 | 0.001 → bespoke; **0.01 = pip** | 0 |

**Important distinction:** `display_precision` and `pip_location`
are different concepts. `pip_size = 10 ** pip_location` gives the
**1 pip** value (0.0001 for USD-quote majors, 0.01 for JPY-quote).
`display_precision` gives the **smallest displayable price tick**
(0.00001 / 0.001 — one decimal smaller). The bespoke
`instrument.round_price(...)` rounds at `display_precision`, i.e.
the *fractional pip*.

## 2. Bespoke `round_price`

`src/forex_bot/domain/instruments.py:45-47`:

```python
def round_price(self, price: Decimal) -> Decimal:
    quant = Decimal(1).scaleb(-self.display_precision)
    return price.quantize(quant, rounding="ROUND_HALF_UP")
```

- Uses `decimal.Decimal.quantize` with `ROUND_HALF_UP`.
- Rounds to 5 decimal places for USD-quote majors, 3 for USD_JPY.
- Half-up means 1.1234**5** rounds to 1.1234**5** (last digit), or
  1.123456 with display_precision=5 rounds to 1.12346 (the 6th
  decimal is ≥ 5).

## 3. Bespoke `round_units`

`src/forex_bot/domain/instruments.py:38-43`:

```python
def round_units(self, units: Decimal) -> Decimal:
    if self.trade_units_precision <= 0:
        return units.to_integral_value(rounding="ROUND_DOWN")
    quant = Decimal(1).scaleb(-self.trade_units_precision)
    return units.quantize(quant, rounding="ROUND_DOWN")
```

`ROUND_DOWN` truncates toward zero. For positive `raw_units` (the
only case in the no-RiskEngine path), this is equivalent to
Python's `int(raw)`.

## 4. Where bespoke rounds and where it doesn't

| location | rounding applied? | source |
|---|---|---|
| Initial stop (in strategy) | **YES** — `round_price` to `display_precision` | `src/forex_bot/strategies/trend_following.py:138` |
| Sized units | **YES** — `round_units` ROUND_DOWN | `src/forex_bot/risk/sizing.py:99` |
| Trailing stop update | **No** — kept at full Decimal precision | `src/forex_bot/backtesting/engine.py:244, 250` |
| Entry fill price | No explicit `round_price` call — pure Decimal arithmetic | `src/forex_bot/backtesting/fills.py:36-52` |
| Exit fill price for stop hit | No — uses the stored `stop_price` (already rounded if initial; not rounded if trailed) | `src/forex_bot/backtesting/engine.py:271, 285` |
| Exit fill price for time / EOD | No — uses raw `bid_close` / `ask_close` Decimals | `src/forex_bot/backtesting/engine.py:277, 291` |
| PnL conversion | No — Decimal arithmetic end-to-end; for USD-base, `gross_quote / exit_price` (the unrounded fill) | `src/forex_bot/backtesting/engine.py:584-606` |

## 5. Verifier behavior (current, post Sprint 003)

| location | verifier behavior | matches bespoke? |
|---|---|---|
| Initial stop | float arithmetic, no rounding | **NO** — bespoke rounds at `display_precision` via `Decimal.quantize(ROUND_HALF_UP)` |
| Sized units | `int(raw)` (Python truncation toward zero, positive raw) | YES (equivalent to ROUND_DOWN for positive) |
| Trailing stop update | float arithmetic, no rounding | YES (bespoke also doesn't round) |
| Entry fill price | float arithmetic | YES (bespoke uses Decimal but no extra rounding) |
| Exit fill price (stop) | float — uses stored `stop_state.stop_price` | YES in structure; NO in precision (verifier's stored stop isn't rounded) |
| Exit fill price (time / EOD) | float `bid_close` / `ask_close` | YES (no rounding either side) |
| PnL conversion | float arithmetic; for USD-base, `gross_quote / exit_price` | YES in structure; sub-pip float precision differs from Decimal |

## 6. Mismatch table

| # | Mismatch | Expected impact | Verifier-only fix |
|---|---|---|---|
| **M1** | **Initial stop is not rounded** to `display_precision`. Verifier stop carries float precision beyond 5 (or 3) decimals. | Borderline `bid_low ≤ stop` (or `ask_high ≥ stop`) comparisons can flip — verifier exits a different bar than bespoke would. Sub-pip float values bias slightly differently from ROUND_HALF_UP. Affects per-pair trade count by a small number and per-pair return by sub-pp. | Add a `round_price` helper to the verifier (Decimal-based, identical formula to bespoke). Call it on the initial stop after `initial_stop_price` returns. |
| **M2** | `InstrumentSpec` does not carry `display_precision` (only `pip_size`). | Cannot apply M1 fix without first surfacing the per-pair display_precision in the verifier metadata table. | Extend `InstrumentSpec` with `display_precision`; populate from the bespoke `Instrument` convention (USD-quote majors → 5; USD_JPY → 3). |
| **M3** | All verifier arithmetic is float; bespoke uses Decimal end-to-end. | Sub-bit precision differences in EMA / ATR / trailing stop / PnL accumulate over thousands of bars. The verifier-vs-bespoke total trade-count delta is +0.49 % (within OK); the largest remaining per-pair return delta is +1.63 pp (USD_CHF, WARN band). | **Not fixed this sprint** — converting the verifier to Decimal end-to-end risks implementing the bespoke engine inside the verifier and sacrificing independence. Float math is the standard verifier convention. |
| **M4** | Trailing stop update not rounded on either side. | None — both engines do the same thing. | No fix needed (re-confirm in Phase 3). |
| **M5** | Sized units rounding (verifier `int(raw)` vs bespoke ROUND_DOWN). | None for positive `raw` — equivalent. | No fix needed. |

## 7. Expected impact

- **M1 + M2** are the only fixes worth applying this sprint.
- They target the most likely cause of borderline stop-pierce flips:
  the verifier's initial stop sitting at sub-pip-fractional values
  the bespoke's rounded stop never visits.
- Expected effect: small but in the right direction. The current
  drift is small (8 trades out of 1,647; per-pair count deltas under
  ±5 trades). M1/M2 might:
  - shift a few borderline trades to match the bespoke side;
  - move 1-2 of the 4 WARN pairs to OK;
  - or leave the comparison at WARN with a smaller-magnitude drift.
- It will **not** convert the verifier to Decimal arithmetic
  end-to-end. The remaining sub-WARN drift after M1/M2 will be
  classified at Phase 4 and either accepted as inherent float
  precision noise or punted to a future, opt-in, Decimal-precision
  sprint.

## 8. Planned verifier-only fixes

| step | change |
|---|---|
| 1 | Add `display_precision: int` field to `research/parity_verifier/models.py::InstrumentSpec`. |
| 2 | Populate `display_precision = 5` for all USD-quote majors, `3` for USD_JPY in `research/parity_verifier/instruments.py`. |
| 3 | Add a `round_price(price: float, display_precision: int) -> float` helper to `research/parity_verifier/rules.py`. Implementation uses `decimal.Decimal(str(price)).quantize(...)` and casts back to float, **identical formula to bespoke** so behavior is by-construction the same. |
| 4 | In `research/parity_verifier/event_loop.py`, after `stop_price = initial_stop_price(...)`, call the new helper to round to `instrument.display_precision`. |
| 5 | Add fixture tests in `tests/research/test_parity_verifier_rules.py` that pin the rounding behavior at 5 / 3 decimal places. |
| 6 | Re-run full-data verifier + comparison. Document before/after. |

## 9. What this audit does NOT propose

- No bespoke-engine edits. The bespoke engine is the source of truth.
- No CAMPAIGN_002 rule changes.
- No conversion of the verifier to Decimal arithmetic (out of scope
  this sprint; preserves verifier independence).
- No strategy approval. CAMPAIGN_002 remains REJECT.
- No paper / demo / live enablement.
- No OANDA API call. The audit reads only already-local files.

## 10. Safety statement

- No `.env` read. No credential value touched.
- No order endpoint exercised.
- No bespoke source file modified (read-only inspection only).
- No CAMPAIGN_002 artifact modified.
- The verifier's `strategy_evidence: false` rail is preserved.

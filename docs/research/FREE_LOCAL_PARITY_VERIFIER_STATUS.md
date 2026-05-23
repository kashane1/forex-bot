# Free / Local Parity Verifier — Status

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-001`
**Phase:** 7 · `strategy_evidence: false`

The headline status of the free / local independent parity verifier
after the implementation sprint. Per-phase detail lives in the doc
links below.

> Verification only. This status describes the state of the
> *measurement instrument*, not of any strategy. **It cannot approve
> a strategy.** CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked.

## Headline

The free / local independent parity verifier is **implemented and
fully fixture-tested**. The full seven-pair, full-window comparison
against the bespoke no-RiskEngine reference (1,647 trades) is
**BLOCKED locally** because the gitignored H4 export CSVs are not
present on this branch. The implementation is ready; the data is the
blocker.

## Verifier implementation status

| layer | status | notes |
|---|---|---|
| Package skeleton | done | `research/parity_verifier/` |
| Independent indicators (EMA / ATR / Donchian) | done | re-derived from canonical definitions, no bespoke imports |
| Independent strategy rules (entry / stop / trailing / exit / fill / sizing / PnL) | done | per the mapping spec §4–§7, no bespoke imports |
| Minimal event loop | done | bar-by-bar, single position per pair, deterministic |
| Comparison harness | done | tolerance ladder + divergence taxonomy from `LEAN_PARITY_COMPARISON_METHOD.md` |
| Markdown rendering | done | `reporting.render_verifier_result_md` / `render_comparison_md` |
| Script entry point | done | `scripts/run_free_local_parity_verifier.py`, exit code 2 when every pair is blocked |
| Import-isolation rail | enforced | a pytest grep test rejects any `forex_bot` import in the verifier package |

## Fixture-level test status

All four verifier-side test files pass.

| file | cases | status | proves |
|---|---|---|---|
| `tests/research/test_parity_verifier_models.py` | 19 | PASS | Bar OHLC consistency, candle-series sortedness/uniqueness, config invariants, the `strategy_evidence: false` and `risk_engine_used: false` rails, instrument metadata, data loaders against the committed authoritative JSON, no-forex_bot-import grep |
| `tests/research/test_parity_verifier_indicators.py` | 16 | PASS | EMA recursion + alpha; ATR Wilder seed + recursion + gap handling; Donchian prior-bar convention (current-bar high does not enter); zero-length / mismatched-input rejection |
| `tests/research/test_parity_verifier_rules.py` | 31 | PASS | entry / no-entry branches incl. trend-filter block + ATR floor; long/short symmetric initial stop; trailing-stop ratchet up/down only; exit ladder precedence (stop → time → EOD); bid/ask-aware fills; 0.25%-risk sizing for USD-quote and USD-base pairs; PnL conversion |
| `tests/research/test_parity_verifier_event_loop.py` | 8 | PASS | empty + flat series; uptrend-drop with stop exit; persistent uptrend with time / trailing exit; no-lookahead rail (last-bar spike does not back-propagate); authoritative config shape loads; USD_JPY divide-by-mid path |
| `tests/research/test_parity_verifier_compare.py` | 11 | PASS | OK / WARN / FAIL ladder for trade count, expectancy, return; missing-pair → `data_mismatch`; pair status is worst of metrics; BLOCKED report shape; full-shape smoke vs the real bespoke reference (1,647 trades, 7 pairs); None-expectancy graceful handling |

**85 verifier-side fixture tests pass.** Full repo suite: 473 passes
(388 pre-sprint + 85 verifier).

## Full-data run status

- **Local seven-pair H4 CSVs:** ABSENT (gitignored regenerable bulk).
- **Bespoke reference JSON:** present (committed).
- **Authoritative parameter JSON:** present (committed).
- **Verifier run on real candles:** **BLOCKED**. The script exits 2
  and the markdown summary lists the blocked pairs; the comparison
  report carries a BLOCKED row per pair. See
  [`FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md).

## Comparison status

- **Fixture-level comparison:** PASS — 11 cases.
- **Full-data comparison:** BLOCKED — no verifier result was produced
  for the seven pairs.
- See [`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md).

## Divergence classification

- **Fixture level:** NONE — every fixture test passed without
  divergence.
- **Full data level:** N/A — no comparison was run, so no divergence
  to classify.
- The taxonomy is in place (mapping spec §3 / `compare.py` /
  `models.DivergenceClassification`) for the first full-data run.

## Bug-finding status

- **Verifier bugs fixed during this sprint:** 1 fixture-assertion
  bug. The `test_uptrend_then_drop_produces_long_entry_and_stop_exit`
  test originally asserted `exit_price < entry_price` (assumed the
  trade lost). The fixture's price walk produced a winning
  trailing-stop exit (entry 1.0052, exit 1.0133 at the ratcheted
  stop). The assertion was corrected to `exit_price ==
  pytest.approx(final_stop_price)`, which holds for both winning and
  losing stops. **No bug in the verifier production code was found
  by this fix** — the test expectation was wrong, the implementation
  was right.
- **Bespoke-engine bugs found:** None. The verifier was never run
  against real candles on this branch (CSVs absent), so the bespoke
  engine could not yet be exercised end-to-end against an
  independent implementation.

## What the verifier proves

- The verifier package implements the CAMPAIGN_002 H4 `trend_following
  0.1.0` strategy and engine mechanics from the mapping spec, with
  every primitive (EMA / ATR / Donchian / entry / exit / stop /
  trailing / fill / sizing / PnL) re-derived from canonical
  definitions and not copied from `src/forex_bot/`.
- A grep-enforced import rail confirms the verifier package never
  imports from the bespoke engine.
- Fixture-level tests pin every documented convention and produce
  85 passing cases; no fixture-level divergence was observed.
- The script entry point reports BLOCKED cleanly when its inputs are
  absent, never silently producing zero-trade "success".

## What the verifier does NOT prove

- It does not corroborate the bespoke engine on real candles — that
  requires the absent CSVs.
- It does not approve any strategy. CAMPAIGN_002 remains REJECT.
- It does not lift the research freeze.
- It does not enable any paper / demo / live loop.
- It does not contact any broker, cloud, or external service.
- A fixture-level pass is necessary but not sufficient for
  independent-engine corroboration.

## Explicit safety state

- **No strategy approved.** `configs/approved_strategies.yaml`:
  `approved: []`.
- **CAMPAIGN_002 remains REJECT** (re-confirmed by the archive
  validator on every commit this sprint).
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` both refuse via the empty registry; no `live-loop`
  command exists in the CLI.
- **No broker credentials used.** No OANDA call, no `.env` sourced,
  no live or practice credential read by any verifier code path.
- **No orders submitted.** This sprint touches no broker, no
  exchange, no execution surface.
- **No QuantConnect / LEAN usage.** The retirement decision stands.
  No `lean login`, no `lean init`, no `lean backtest`. No QC
  credential was requested, read, written, or committed.

## Cross-links

- Sprint plan: [`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md)
- Indicator fixtures: [`FREE_LOCAL_PARITY_VERIFIER_INDICATOR_FIXTURES.md`](FREE_LOCAL_PARITY_VERIFIER_INDICATOR_FIXTURES.md)
- Rule fixtures: [`FREE_LOCAL_PARITY_VERIFIER_RULE_FIXTURES.md`](FREE_LOCAL_PARITY_VERIFIER_RULE_FIXTURES.md)
- Event-loop status: [`FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md)
- Comparison status: [`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md)
- Retirement decision: [`QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`](QUANTCONNECT_LEAN_RETIREMENT_DECISION.md)
- Design: [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md)

# Free / Local Parity Verifier — Status

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-001`
**Phase:** 7 · `strategy_evidence: false`
**Re-confirmed:** `infra-free-local-parity-verifier-002-full-data-run`
Phase 5 — the data unblock was attempted and could not be performed
under the sprint rules (no local `data/oanda_h4_research.sqlite3`, no
`.env` with OANDA practice credentials, no `OANDA_*` env vars in the
shell). The verifier script was invoked end-to-end against the absent
CSVs and produced a clean BLOCKED state (7 × BLOCKED, exit code 2, no
crash, no fabricated data). The comparison harness was re-run
programmatically against the real bespoke no-RiskEngine reference
(1,647 trades) and produced a structurally identical seven-row
BLOCKED report. **Verifier bugs found: 0. Bespoke-engine bugs found:
N/A** (engine not exercised; no real-candle cross-check possible
without the CSVs). Detail:
[`FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md),
[`FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md),
[`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md)
"Sprint-002 re-run record" section.

**Re-confirmed:** `infra-free-local-parity-verifier-003-with-data`
Phase 6 — the guarded OANDA-practice rehydrate + export + verifier
sprint was executed and also stayed BLOCKED for the same reasons
(no `.env`, all six probed `OANDA_*` env vars unset, no SQLite
store). The rehydrate script ran in `--verify` mode only (no API
call). No OANDA endpoint was contacted. No orders were submitted.
The 1,647-trade no-RiskEngine bespoke reference scope was explicitly
re-asserted before the comparison harness was invoked
(`total_trades == 1647`, `risk_engine_used is False`). The
comparison produced an identical seven-row BLOCKED report. Detail:
[`FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md),
[`FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md),
[`FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md),
[`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md)
"Sprint-003 re-run record" section.

**UPDATED:** `infra-free-local-parity-verifier-003-with-data`
mid-sprint pivot — the user corrected my worktree-scoped inventory
mistake by pointing out that `.env` lives at the **main repo root**
(not visible from inside a git worktree) and that
`/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` already
contains the full CAMPAIGN_002 H4 dataset. With the user's explicit
authorization, the sprint completed end-to-end **with zero OANDA
network calls** (no rehydrate fetch needed; the existing local
SQLite had the data). The verifier ran across all seven pairs
(zero blocked, zero crashes).

**Initial run (pre-debug):** 1,586 trades vs 1,647 bespoke
(−3.70 %, within OK), overall comparison **FAIL** on EUR_USD return
delta +2.41 pp. The divergence was systematic (verifier
consistently less bad on every pair).

**Phase 5 debug (verifier-side only, no bespoke change):** two
verifier bugs identified and fixed.
- **Bug #1:** initial stop was anchored at the post-slippage
  `entry_price` instead of the bar's mid `close` (bespoke's
  convention). Fixed in `rules.py`.
- **Bug #2:** event loop blocked same-bar re-entry after an exit;
  bespoke processes exits first, then evaluates new entries on the
  same bar. Fixed in `event_loop.py`.

**Post-debug:** **1,655 trades vs 1,647 (Δ +0.49 %, OK)**. Per-pair
3 / 7 OK (GBP_USD, USD_JPY, AUD_USD), 4 / 7 WARN, **0 / 7 FAIL**.
Overall comparison **WARN** (down from FAIL). Largest remaining
delta is USD_CHF return +1.63 pp (WARN band), plausibly Decimal-vs-
float precision and the missing `instrument.round_price(...)` step
on the verifier side. **Both engines agree every pair is
loss-making on the no-RiskEngine path; CAMPAIGN_002 stays REJECT
under either measurement.**

Verifier-side bugs fixed this turn: **2**. Bespoke-engine bugs
found: **0**.

Full detail:
[`FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md`](FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md),
[`FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md`](FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md),
and the "Sprint-003 UNBLOCKED" + "Sprint-003 Phase 5 debug — post-fix
comparison" sections of
[`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md).

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

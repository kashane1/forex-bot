# Free / Local Parity Verifier — Rule Fixtures

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-001`
**Phase:** 3 · `strategy_evidence: false`

What the verifier's independent strategy-rule evaluation pins, derived
from `docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md` §4–§7 and the
authoritative parameters in
`research/lean_parity/lean_parity_config.json` — never copied from
`src/forex_bot/strategies/trend_following.py`.

Tests: [`tests/research/test_parity_verifier_rules.py`](../../tests/research/test_parity_verifier_rules.py).
Implementation: [`research/parity_verifier/rules.py`](../../research/parity_verifier/rules.py).

> A fixture-level pass is necessary but **not sufficient**. It does
> not approve a strategy, does not lift the freeze, and does not
> imply a full-data run will agree with the bespoke reference.
> CAMPAIGN_002 remains REJECT.

## Frozen rules pinned

### Entry (`evaluate_entry`)

- ``in_position=True`` short-circuits — no new entry while one is
  open.
- Any NaN among EMA fast / EMA slow / close / Donchian high / Donchian
  low / ATR returns no entry.
- ``atr_floor_pips`` honoured if set (CAMPAIGN_002 uses ``{}``, so the
  floor is disabled — but the verifier must still apply it correctly
  for any future re-run that sets one).
- **Long:** ``EMA_fast > EMA_slow`` *and* ``close > donchian_high`` —
  strict-inequality breakout against the prior-bar Donchian band.
- **Short:** ``EMA_fast < EMA_slow`` *and* ``close < donchian_low``.
- **No-entry** otherwise (including: close at the band but not past
  it; correct trend filter but no breakout; correct breakout but
  wrong trend).

Fixtures: 7 cases — in-position short-circuit, NaN block, long entry,
short entry, no-entry-at-band, trend filter block, ATR floor block.

### Initial stop (`initial_stop_price`)

- Long: ``entry - atr × atr_stop_multiple``.
- Short: ``entry + atr × atr_stop_multiple``.
- ``Side.FLAT`` raises ``ValueError`` — the verifier never calls this
  for a no-position state.

Fixtures: 3 cases — long, short, FLAT rejection.

### Trailing stop (`ratchet_trailing_stop`)

- Long candidate: ``bid_close − atr × trailing_multiple``. Raises the
  stop only; never lowers it. Returns ``(new_stop, moved)``.
- Short candidate: ``ask_close + atr × trailing_multiple``. Lowers
  the stop only; never raises it.
- The ``moved`` flag drives the exit-reason label: a never-ratcheted
  exit is ``STOP``; a ratcheted exit is ``TRAILING_STOP``.

Fixtures: 2 cases — long ratchet up only, short ratchet down only.
Each fixture includes a "no-move" follow-up call to confirm the
ratchet direction is unidirectional.

### Exit ladder (`evaluate_exit`)

Per mapping spec §5, on each bar after entry, in this exact order:

1. Adverse stop (long: ``bid_low ≤ stop`` → exit at ``stop``; short:
   ``ask_high ≥ stop`` → exit at ``stop``). Reason is ``STOP`` if the
   stop never moved, ``TRAILING_STOP`` otherwise.
2. Time stop (``bars_held ≥ max_bars_in_trade`` → exit at ``bid_close``
   long / ``ask_close`` short, reason ``TIME``).
3. End of data on the last bar (exit at ``bid_close`` / ``ask_close``,
   reason ``EOD``).
4. Otherwise no exit.

The verifier does **not** implement take-profit or opposite-signal
exit — these do not exist for ``trend_following 0.1.0``.

Fixtures: 7 cases — long stop, trailed-long-stop label, short stop,
time stop, EOD, no-exit, and an explicit precedence test where stop
AND time AND last-bar all fire together (stop wins).

### Bid/ask-aware fill (`fill_entry_price`)

- ``spread_pips = (ask_close − bid_close) / pip_size``.
- ``slip_pips = max(fixed_slippage_pips, spread_pips × multiplier)``.
- Long entry = ``ask_close + slip_pips × pip_size``.
- Short entry = ``bid_close − slip_pips × pip_size``.

Fixtures: 3 cases — long uses ask, short uses bid, fixed-slippage
floor applies when spread is zero.

### Sizing (`size_position`)

0.25%-of-equity per trade (mapping spec §6):

- ``risk_amount = nav × risk_per_trade_pct / 100``.
- ``stop_distance_pips = |entry − stop| / pip_size``.
- ``pip_value_home`` is ``pip_size`` for USD-quote pairs and
  ``pip_size / mid_price`` for USD-base pairs (USD_JPY, USD_CAD,
  USD_CHF).
- ``raw = risk_amount / (stop_distance_pips × pip_value_home)``;
  ``units = floor(raw)``.
- Stop distance zero → zero units. Non-USD-quote / non-USD-base pair
  → ``ValueError``.

Fixtures: 5 cases — EUR_USD basic (expected 250 units exactly),
USD_JPY with the divide-by-mid conversion (expected 375 units),
floor-to-int behaviour (328 units, not 328.94…), zero-distance →
zero units, unsupported currency pair raises.

### PnL conversion (`trade_pnl`)

- ``diff = (exit − entry)`` for long; ``(entry − exit)`` for short.
- ``gross_quote = diff × units``.
- USD-quote pair → ``gross_home = gross_quote``.
- USD-base pair → ``gross_home = gross_quote / exit_price``.

Fixtures: 4 cases — long EUR_USD positive PnL, short EUR_USD negative
PnL, USD_JPY divide-by-exit conversion, unsupported currency pair
raises.

## Long/short symmetry

Every entry, stop, ratchet, and exit rule has dedicated fixtures for
both directions. The implementation funnels both through the same
control flow (single ``Side`` enum, single switch in each function);
the fixtures cover the asymmetric pieces explicitly (long uses
bid_close for trailing / bid_low for stop pierce; short uses ask_close
for trailing / ask_high for stop pierce).

## No-lookahead behaviour

The Donchian convention from Phase 2 (``donchian_high[t] =
max(high[t-L..t-1])`` — prior bars only) is the primary no-lookahead
rail. The rule fixtures further confirm that:

- entry evaluation is keyed off ``close[t]`` and ``donchian_high[t]``
  computed from prior bars only;
- exit evaluation uses bar ``t``'s own bid/ask high/low (the bar the
  stop is being checked against), not bar ``t+1``;
- the event loop (Phase 4) calls these functions strictly in
  per-bar order, never peeking ahead.

## Ambiguities found and resolutions

| ambiguity | resolution |
|---|---|
| The original `campaign_002_h4_spec.md` table lists `min_atr_pips` per pair, but the authoritative `lean_parity_config.json` shows `min_atr_pips: {}` (empty). | Verifier follows the **authoritative JSON** (empty floor), exactly as the mapping spec §4 instructs (the spec file itself notes the table is stale). The fixture exercises both `atr_floor_pips=None` and a non-None value so the gate works correctly if a future re-run sets one. |
| The mapping spec §5 wording "exit at stop" is unambiguous for the verifier (the fill is exactly at `stop_price`). It carries a known Lean-mechanics caveat about gap fills — that caveat is no longer relevant since LEAN is retired. | Verifier exits exactly at `stop_price`, matching the bespoke engine's behaviour. |
| `trade_pnl` for USD-base pairs converts through the **exit** price (mapping spec §6). | Confirmed by the `test_trade_pnl_usd_jpy_converts_through_exit_price` fixture (exactly `375 / 151`). |

No ambiguity is being silently guessed. Anything not specified by the
mapping spec or the authoritative config raises ``ValueError`` rather
than picking a default.

## Fixture-test status

- 31 rule fixtures — **all pass**.
- Combined with Phase 1 (19 model / data-loader / instrument) and
  Phase 2 (16 indicator) — **66 verifier-side fixture tests pass**.
- Full repo pytest with all three test files — **454 passes** (388
  pre-sprint + 66 verifier-side).

## What this does NOT prove

- It does not prove the bespoke engine is correct. A divergence
  surfaced by Phase 4 / 5 is a finding to localize, not a verdict on
  the bespoke side.
- It does not approve any strategy. ``configs/approved_strategies.yaml``
  remains ``approved: []``.
- It does not enable any paper / demo / live loop.
- It does not contact any broker, cloud, or external service.

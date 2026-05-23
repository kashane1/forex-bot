# Free / Local Parity Verifier — Indicator Fixtures

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-001`
**Phase:** 2 · `strategy_evidence: false`

What the verifier's independent EMA / ATR / Donchian implementations
pin, and why. Every fixture's expected value is derived from the
canonical mathematical definition (or hand-computed for a chosen tiny
input) — never copied from the bespoke engine. The bespoke engine's
indicator file at `src/forex_bot/strategies/indicators.py` is the
*subject* the verifier checks against, not the *oracle* it copies
from.

Tests live at [`tests/research/test_parity_verifier_indicators.py`](../../tests/research/test_parity_verifier_indicators.py).
Implementation: [`research/parity_verifier/indicators.py`](../../research/parity_verifier/indicators.py).

## Pinned behaviour

### EMA

- Recursive ``alpha = 2 / (L + 1)`` — verified by the
  ``test_ema_alpha_is_two_over_l_plus_one`` fixture (zeros + a single
  shock; the post-shock value pins alpha exactly).
- ``min_periods = L`` — output is ``NaN`` for the first ``L − 1``
  samples, the ``L``-th sample is seeded at ``values[L-1]`` (the
  pandas ``ewm(adjust=False)`` convention re-derived without pandas).
- A constant input series returns a constant output once warmup ends.
- ``ema(values, 0)`` raises ``ValueError``.

### ATR (Wilder)

- True range at bar ``i``:
  ``TR_i = max(high_i − low_i, |high_i − close_{i-1}|, |low_i − close_{i-1}|)``.
  The first bar has no previous close, so ``TR_0 = high_0 − low_0`` —
  pinned by ``test_atr_first_tr_uses_high_minus_low_when_no_prev_close``.
- Wilder smoothing: ``alpha = 1 / L``, seeded at the simple average of
  the first ``L`` TR values; outputs are ``NaN`` for the first
  ``L − 1`` samples. ``test_atr_wilder_recursion`` constructs a
  constant-TR seed window plus a single shock and checks the recursion
  numerically: ATR(4) seed 1.375 + shock TR 2.5 → ATR_4 = 1.65625.
- Gaps that make ``|high − prev_close|`` or ``|low − prev_close|``
  exceed ``high − low`` correctly dominate TR — pinned by
  ``test_atr_handles_gap_correctly``.
- Mismatched-length inputs and zero ``length`` raise ``ValueError``.

### Donchian (prior-bar convention)

- ``donchian_high[t] = max(high[t-L..t-1])`` — the high of the
  **prior** ``L`` completed bars, **excluding** the current bar. This
  is the mapping spec §3 wording and is the no-look-ahead behaviour
  the bespoke engine implements as ``high.shift(1).rolling(L).max()``.
- The verifier explicitly tests that a current-bar high *higher* than
  every prior high does **not** enter ``donchian_high[t]`` —
  ``test_donchian_high_uses_prior_bars_only`` constructs exactly that
  case (high 100.0 at the current bar; donchian remains the prior
  maximum 5.0).
- ``test_donchian_breakout_against_prior_high`` documents the
  comparison the entry rule uses: ``close[t] > donchian_high[t]`` is
  a strict-inequality breakout against the prior maximum.
- Zero ``length`` raises ``ValueError`` for both
  ``donchian_high`` and ``donchian_low``.

## Warmup assumptions

| indicator | first non-NaN index |
|---|---|
| EMA(L) | ``L - 1`` |
| ATR(L) | ``L - 1`` |
| Donchian(L) | ``L`` (the window must contain ``L`` prior bars) |

The verifier's event loop respects these — entries cannot fire until
all four series (EMA_fast, EMA_slow, ATR, Donchian high/low) are
finite at the current bar. ``rules.evaluate_entry`` is tested
end-to-end on NaN inputs in Phase 3.

## Donchian prior-bar convention — extra emphasis

The mapping spec calls out specifically that Lean's built-in
``DonchianChannel`` indicator includes the **forming** bar — using it
without modification would be a look-ahead bug. The verifier's
``donchian_high`` / ``donchian_low`` mirror the bespoke engine's
``high.shift(1).rolling(L).max()`` shape exactly, but the
implementation is independent (a plain Python ``max()`` over a slice,
no pandas).

## Known differences from the bespoke implementation

None identified during Phase 2. The verifier and the bespoke engine
implement the *same definitions* but in different languages /
libraries:

- Bespoke uses pandas (``ewm`` / ``rolling``); the verifier uses a
  plain-Python recursion and slicing.
- Bespoke produces ``pd.Series`` with a ``DatetimeIndex``; the
  verifier produces a flat ``list[float]``.

The numerical convention is the same. If a Phase 4 / 5 / 6 run reveals
a divergence on real candles, it will be classified under the
divergence taxonomy and traced before being attributed to either side.

## Fixture-test status

- 16 indicator fixtures — **all pass**.
- 19 model / data-loader / instrument fixtures (Phase 1) — **all pass**.
- Full repo pytest with these new tests added — **407 → 423 passes**
  (with the Phase 1 19 already counted).

## What this does NOT prove

- It does not prove the bespoke engine is correct. The fixtures pin
  the verifier's behaviour; the bespoke engine is checked against
  the same spec in its own unit tests.
- It does not approve any strategy. CAMPAIGN_002 remains REJECT.
  ``configs/approved_strategies.yaml`` remains empty.
- It does not enable any paper / demo / live loop.
- It does not contact any broker, cloud, or external service.

A fixture-level pass is **necessary** for the verifier to be
trustworthy. It is not **sufficient** — full-data corroboration vs the
bespoke reference comes in Phases 4 and 5 (subject to local CSV
availability, gitignored bulk data).

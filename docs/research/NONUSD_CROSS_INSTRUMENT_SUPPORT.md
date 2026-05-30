# Non-USD Cross Instrument Support

**Sprint:** `research-nonusd-cross-ingestion-and-cost-models-001` (Phase 1)
**Status:** infrastructure only — no strategy, no campaign, no approval.

## What was added

A single source of truth for non-USD FX cross metadata:
`src/forex_bot/domain/cross_instruments.py`. It is **additive** — the
seven USD majors (`m1_corpus_validation.MAJOR_PAIRS`) are left exactly as
they were, as the control/baseline universe.

### Registry (`CrossSpec`)

Each cross carries: tier (`primary` = wave-1 required, `extended` =
wave-1 optional), qualitative `cost_band` + `est_spread_pips`, an
**explicit** `conservative_bp_per_day` (per cross, *not* the majors'
table-max fallback), an `is_carry_cross` flag, `structural_breaks`, and
derived price conventions. Price conventions are validated in
`__post_init__`:

- **JPY-quote crosses** (EUR_JPY, GBP_JPY, AUD_JPY, NZD_JPY):
  `pip_location = -2`, `display_precision = 3`, `pip_size = 0.01`.
- **All other crosses** (EUR_GBP, EUR_CHF, GBP_CHF, EUR_AUD):
  `pip_location = -4`, `display_precision = 5`, `pip_size = 0.0001`.

A `CrossSpec` refuses any pair with a USD leg, any malformed name, any
unknown cost band, and any negative cost figure.

### Registered wave-1 crosses

| Cross | Tier | Quote | Pip | Carry | Structural break |
|-------|------|-------|-----|-------|------------------|
| EUR_GBP | primary | GBP | 0.0001 | no | — |
| EUR_JPY | primary | JPY | 0.01 | yes | — |
| GBP_JPY | primary | JPY | 0.01 | yes | — |
| AUD_JPY | primary | JPY | 0.01 | yes | — |
| NZD_JPY | extended | JPY | 0.01 | yes | — |
| EUR_CHF | extended | CHF | 0.0001 | no | 2015-01-15 SNB floor removal |
| GBP_CHF | extended | CHF | 0.0001 | no | — |
| EUR_AUD | extended | AUD | 0.0001 | no | — |

### Instrument factory

`cross_instrument(name)` builds a domain `Instrument` via the existing,
tested `Instrument` model — so pip handling, display precision,
`round_price`, `price_to_pips`, and `pips_to_price` flow through one
already-covered code path rather than a parallel implementation.

## Integration points (additive)

`m1_corpus_validation` now exposes:

- `NONUSD_CROSS_PAIRS` — re-exported from the registry.
- `SUPPORTED_PAIRS = MAJOR_PAIRS + NONUSD_CROSS_PAIRS` — the union that
  ingestion/materialization gates widen to in later phases.

`MAJOR_PAIRS` is unchanged, so every campaign loader that imports it
(`campaign_021/022/025/026_loader`) is unaffected. The inventory check's
`extra_pairs` anomaly list now excludes registered crosses (they are
supported additions, not anomalies); `missing_pairs` still tracks the
seven-major control universe so a missing major is still flagged.

## Pip-convention confirmation

`tests/unit/test_cross_instruments.py` asserts JPY crosses resolve to
`0.01` pips / 3 dp and non-JPY crosses to `0.0001` pips / 5 dp, that the
`Instrument` factory round-trips pips, that EUR_CHF carries the 2015 SNB
break, and that `MAJOR_PAIRS` is byte-for-byte the original seven and
disjoint from the crosses.

## Why a cross is not a major (carried into cost modelling, Phase 4)

P&L on a cross accrues in its **quote currency**, which is not USD;
converting risk/notional to USD needs a separate quote/USD rate. Carry is
genuinely **two-legged** (base-leg rate minus quote-leg rate). The
majors' `financing.notional_usd`/`risk_usd` assume one USD leg and are
therefore invalid for crosses — Phase 4 builds cross-specific cost models
rather than copying those assumptions.

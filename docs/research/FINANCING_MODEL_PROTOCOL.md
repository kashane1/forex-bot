# Financing Model Research Protocol

**Date:** 2026-05-23 · **Branch:** `research-financing-model-001` · Phase 2
`strategy_evidence: false`

The protocol the new `research/financing/` module follows: what
it takes, what it produces, how it handles calendar, currency,
and missing-rate cases, and what must be true before its outputs
can influence a paper / demo / live promotion decision.

> This document does not approve any strategy. CAMPAIGN_002
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## 1. Target purpose

`research/financing/` is a **research-grade, conservative
financing adjustment** calculator. It runs off-engine, against
hand-built or committed inputs, and produces diagnostic
artifacts that document a campaign's financing posture more
expressively than the existing per-trade bp/day overlay.

It is **not**:

- a backtest engine
- a broker-data fetcher
- a `MODELED` financing model in the
  `FinancingTreatment` sense (the existing
  `src/forex_bot/financing.py` gate is authoritative; this
  module's outputs report `ESTIMATED` at best — see §13)
- a paper / demo / live enabler

It **is**:

- a deterministic per-day rollover-event log generator
- a long-vs-short asymmetric carry calculator
- a calendar-aware (weekend skip + optional Wednesday triple
  rollover) accruer
- a pluggable rate-source consumer with explicit
  missing-rate fallbacks
- a per-position summary + position-set aggregate + JSON +
  markdown reporter
- a forward seam for an observed-rate source once
  `DAILY_FINANCING` capture starts

## 2. Supported inputs

### 2.1 `PositionInterval`

One closed position to compute financing for.

| field | type | meaning | required |
|---|---|---|:--:|
| `position_id` | str | opaque identifier (caller-supplied) | ✓ |
| `instrument` | str | e.g. `EUR_USD`, `USD_JPY` | ✓ |
| `side` | `"long"` \| `"short"` | direction | ✓ |
| `units` | Decimal | unsigned units (always positive; `side` carries direction) | ✓ |
| `entry_price` | Decimal | quote-currency price at open | ✓ |
| `open_time` | datetime (UTC) | when the position opened | ✓ |
| `close_time` | datetime (UTC) | when the position closed | ✓ |
| `home_currency` | str | account home currency (`USD` default) | optional |

Validation invariants:

- `close_time > open_time`
- `units > 0`
- `entry_price > 0`
- `instrument` matches `^[A-Z]{3}_[A-Z]{3}$`
- `home_currency` matches `^[A-Z]{3}$`

### 2.2 `FinancingRateSource`

Abstract source of (long, short) annualized financing rates per
(date, instrument). Required v1 implementations:

- **`TableRateSource`** — wraps a per-(date, instrument) table of
  `(long_rate, short_rate)` tuples. Used for hand-built fixtures
  and for any future committed historical-rate file.
- **`ConservativeStressRateSource`** — wraps a constant per-pair
  `(long_bp_per_day, short_bp_per_day)` table, defaulting to the
  bp/day table from `src/forex_bot/financing.py` extended with an
  explicit short side (long = short = table value, the worse of
  the two — same conservatism as the existing overlay). Returns
  the same value on every date. **Default for stress-only mode.**

Each source declares:

- `name: str` — identifier embedded in metadata
- `treatment: FinancingTreatment` — `ESTIMATED` for the two v1
  sources; never `MODELED` (the existing gate's `MODELED` slot is
  reserved for the future observed-rate path)
- `rate_for(date, instrument) -> RatePair | None` — `None` means
  "no rate known for this date" (the calculator handles fallback
  per §6)

### 2.3 `FinancingCalculatorConfig`

| field | type | default | meaning |
|---|---|---|---|
| `rollover_hour_utc` | int | 21 | the UTC hour treated as the rollover boundary (≈17:00 NY → 21:00 UTC in summer; the choice is documented, not learned) |
| `triple_swap_weekday` | int \| None | 2 (Wednesday) | weekday whose rollover counts triple; `None` disables triple-swap (deferred-friendly) |
| `skip_weekends` | bool | True | if True, no rollover event is recorded for Saturday or Sunday (no carry over the weekend itself — Wednesday's triple covers Sat+Sun+Mon) |
| `missing_rate_policy` | enum | `conservative` | see §6 |
| `home_currency` | str | "USD" | default home currency for conversion |
| `conservative_fallback_bp_per_day` | float | 1.2 | bp/day used by the `conservative` missing-rate policy; matches `_DEFAULT_BP_PER_DAY` in the existing overlay |

## 3. Supported outputs

### 3.1 `DailyFinancingEvent`

One rollover event for one position.

| field | type | meaning |
|---|---|---|
| `position_id` | str | from `PositionInterval` |
| `instrument` | str | from `PositionInterval` |
| `date_utc` | date | the rollover date (UTC) |
| `weekday` | int | 0=Monday, … 6=Sunday |
| `rollover_multiplier` | int | 1 normally, 3 on triple-swap day |
| `rate_long_annual_bp` | float \| None | rate used for the long side (None if missing-rate fallback fired) |
| `rate_short_annual_bp` | float \| None | rate used for the short side |
| `applied_side` | `"long"` \| `"short"` | which side this position pays/receives |
| `applied_rate_bp_per_day` | float | rate translated to bp/day (annual / 365) on the applied side |
| `notional_home` | float | position notional in home currency (see §5) |
| `cashflow_home` | float | signed cashflow in home currency (debit = `<0`, credit = `>0`); see §4 for sign rules |
| `cashflow_home_stress` | float | the always-`≤0` conservative version (`min(cashflow_home, 0)`) — never assumes a credit |
| `rate_source_name` | str | provenance |
| `rate_was_missing` | bool | True if the source returned None and a fallback was used |
| `notes` | list[str] | per-event diagnostics (e.g. "triple swap", "missing rate — conservative fallback") |

### 3.2 `PositionFinancingSummary`

One row per `PositionInterval`.

| field | type |
|---|---|
| `position_id` | str |
| `instrument` | str |
| `side` | `"long"` \| `"short"` |
| `events` | `list[DailyFinancingEvent]` |
| `rollovers` | int |
| `cashflow_home_total` | float |
| `cashflow_home_stress_total` | float |
| `rate_was_missing_any` | bool |

### 3.3 `FinancingRunReport`

The position-set aggregate, ready for dump.

| field | type |
|---|---|
| `config` | `FinancingCalculatorConfig` |
| `rate_source_name` | str |
| `rate_source_treatment` | `FinancingTreatment` |
| `home_currency` | str |
| `positions` | `list[PositionFinancingSummary]` |
| `event_count` | int |
| `cashflow_home_total` | float |
| `cashflow_home_stress_total` | float |
| `missing_rate_event_count` | int |
| `strategy_evidence` | literal `False` (Pydantic-enforced rail) |
| `financing_treatment` | mirrors `rate_source_treatment` |
| `financing_in_engine_pnl` | literal `False` |
| `financing_is_live_blocker` | literal `True` (this module is **never** the source of `MODELED` financing — see §13) |
| `generated_at_utc` | datetime |

## 4. Sign convention

A **debit** (the account pays) is `<0`. A **credit** (the account
receives) is `>0`. This matches the OANDA `DAILY_FINANCING`
convention preserved in `ObservedFinancingEvent.financing`
([`src/forex_bot/domain/transactions.py:68`](../../src/forex_bot/domain/transactions.py)).

For a position of side `s` on instrument with annualized rate
`r_s` (in basis points), unit notional `N`, multiplier `m`:

```
daily_rate    = r_s / 10_000 / 365
cashflow_home = sign(s, r_s) * |daily_rate * m| * N
```

where `sign(s, r_s)`:

- a positive rate on the favourable side → credit (`+1`)
- a negative rate on the favourable side or a positive rate on
  the unfavourable side → debit (`−1`)

The exact convention applied in v1 (the simple, conservative
one):

- `applied_rate_bp_per_day = r_s_annual / 365` for the position's
  own side, with sign **always negative** in stress mode (the
  module never credits in stress mode; see §3.1's
  `cashflow_home_stress`).
- In `realistic` mode (`TableRateSource` with explicit signed
  rates per side per date), the sign of `cashflow_home` follows
  the sign of the rate verbatim — credits are allowed in
  `cashflow_home` but **never** in `cashflow_home_stress`.

## 5. Currency conversion

All cashflows are reported in `home_currency`. V1 handling:

- **`home_currency == quote_currency` (e.g. USD home, EUR_USD):**
  `notional_home = units * entry_price`, no conversion needed.
- **`home_currency == base_currency` (e.g. USD home, USD_JPY):**
  `notional_home = units` (units are already home-currency
  denominated).
- **Cross pairs (e.g. USD home, EUR_GBP):** v1 falls back to the
  conservative bp/day fallback (§6) and sets
  `rate_was_missing=True`, plus a note "cross-pair conversion
  deferred — conservative fallback applied". Strict cross-pair
  conversion is **deferred** (§9).

A v1.1+ extension could accept a `home_quote_map: dict[date, dict[str, Decimal]]`
to convert any cross at any rollover date. Out of scope for v1.

## 6. Missing-rate behaviour

When `rate_source.rate_for(date, instrument)` returns `None`, the
calculator applies the `missing_rate_policy`:

| policy | behaviour |
|---|---|
| `conservative` (default) | use `conservative_fallback_bp_per_day` as the applied bp/day, with sign `−1` (always a debit), set `rate_was_missing=True`, add note "missing rate — conservative fallback bp/day=<value>" |
| `skip` | emit no event for that date; mark `rate_was_missing=True` on the summary; only used by callers who explicitly accept the underestimate risk and document why |
| `error` | raise `MissingFinancingRateError`; only used by callers who guarantee the rate source covers every date |

Default `conservative` matches the spirit of the existing
overlay: never let a missing rate silently produce a 0 cost.

## 7. Daily rollover convention

For a `PositionInterval` `[open_time, close_time)`:

1. Build the candidate rollover-date set: every UTC date `d` such
   that the moment `d` at `rollover_hour_utc` falls **strictly
   inside** `(open_time, close_time)`. A position opened *after*
   the rollover on day `d` does not get day `d`'s rollover; a
   position closed *before* the rollover on day `d` does not get
   day `d`'s rollover.
2. If `skip_weekends` is True, drop any candidate date whose
   weekday is Saturday or Sunday.
3. For each remaining date `d`:
   - `multiplier = 3` if `triple_swap_weekday is not None` and
     `d.weekday() == triple_swap_weekday`, else `1`.
   - `(long_rate, short_rate) = rate_source.rate_for(d, instrument)`
     or fallback per §6.
   - Compute event per §3.1 + §4.

`triple_swap_weekday = 2` (Wednesday) matches typical broker
conventions: Wednesday's rollover accrues Saturday + Sunday +
Monday's financing on top of Wednesday's, because spot settles
T+2.

## 8. Weekend and holiday handling

- **Weekends:** default skip; triple-swap on Wednesday covers
  them. Setting `skip_weekends=False` and `triple_swap_weekday=None`
  yields a flat 7-days-per-week accrual (an option for pessimistic
  stress runs).
- **Holidays:** v1 has **no holiday calendar**. Missing holidays
  are treated as ordinary rollover days; if the rate source has
  no rate for a holiday, the missing-rate policy fires. This is
  deliberately conservative (you pay an estimated rate on every
  open day, holiday or not) and avoids embedding a stale or
  jurisdiction-specific calendar in research-only code.

A v1.1+ extension could accept `holiday_dates: set[date]` per
instrument. Out of scope for v1.

## 9. Feature classification

### Required in v1

1. `PositionInterval` model with validation invariants.
2. `FinancingRateSource` interface + `TableRateSource` +
   `ConservativeStressRateSource`.
3. `FinancingCalculatorConfig` with v1 defaults.
4. `DailyFinancingEvent`, `PositionFinancingSummary`,
   `FinancingRunReport` Pydantic models with
   `strategy_evidence: false` rail.
5. `calculate_position(...)` and `calculate_run(...)` pure
   functions over local inputs.
6. Daily rollover convention per §7 (per-date events strictly
   inside `(open_time, close_time)`, configurable
   `rollover_hour_utc`).
7. Weekend skip default.
8. Wednesday triple-swap default (with knob to disable).
9. Missing-rate conservative fallback.
10. Long / short asymmetry via `TableRateSource` returning
    `(long_rate, short_rate)`.
11. Stress mode: side-symmetric pessimistic bp/day from
    `ConservativeStressRateSource`, debit-only
    (`cashflow_home_stress`).
12. Same-day open + close → zero rollover events (no rollover
    boundary crossed → no rollover).
13. Home-currency conversion for USD-base and USD-quote pairs.
14. JPY precision: rate / pip arithmetic uses `Decimal`
    intermediaries where it affects per-cent results; output
    floats are sufficient for diagnostics.
15. `render_summary_md(report)` and `dump_events_json(report)` —
    pure, deterministic, no I/O.
16. Grep-enforced import isolation rail: no file under
    `research/financing/` imports from `forex_bot` (test in
    `tests/research/test_financing_models.py`).
17. Pydantic-enforced `strategy_evidence: false` on every report
    model.

### Optional in v1 (implemented if cheap, otherwise deferred)

- A `default_stress_rate_source()` helper returning a
  `ConservativeStressRateSource` populated from the same bp/day
  table as `src/forex_bot/financing.py` (re-stated locally to
  preserve import isolation).
- `dump_events_json` with stable key ordering and ISO-8601 dates.

### Deferred

- Cross-pair home conversion (any pair where neither base nor
  quote is the home currency). V1 falls back to the conservative
  bp/day fallback for crosses and flags the event.
- Holiday calendars.
- Observed-rate `FinancingRateSource` backed by
  `ObservedFinancingEventRepo`. The seam exists (a future
  `ObservedRateSource` class can wrap the repo); v1 does not
  implement it because (i) the table is empty under the freeze
  and (ii) `research/financing/` may not import from
  `forex_bot`. Implementing it requires either a duplicated
  read-only model or a host script that converts events to a
  `TableRateSource` outside the package.
- `MODELED` `FinancingTreatment` for any source in this module.
  `MODELED` remains reserved for the future
  `FutureOandaObservedFinancingModel` path in
  `src/forex_bot/financing.py`.
- Engine-PnL integration. The bespoke `BacktestEngine` is not
  modified.

## 10. Conservative fallback behaviour

The `conservative` missing-rate policy uses a configurable
bp/day debit (default `1.2`, matching `_DEFAULT_BP_PER_DAY` in
the existing overlay). It is intentionally pessimistic.

`cashflow_home_stress` is **always ≤ 0** regardless of policy or
rate source:

```python
cashflow_home_stress = min(cashflow_home, 0.0)
```

A report's headline "stressed total" therefore upper-bounds the
*loss* from financing; it never lets a credit show up to mask a
debit elsewhere.

## 11. Stress-test mode

A pure stress run:

- `rate_source = ConservativeStressRateSource(...)` (default
  table; both sides equal to the worse-side bp/day; signs forced
  to debit-only).
- `missing_rate_policy = "conservative"`.
- `triple_swap_weekday = 2`, `skip_weekends = True`.

Result: `cashflow_home == cashflow_home_stress` (always ≤ 0).
The `FinancingRunReport` reports `financing_treatment =
ESTIMATED`. No claim is made about historical accuracy.

A pessimistic-flat run:

- as above, but `skip_weekends = False` and
  `triple_swap_weekday = None` → flat 7-days-per-week debit.

These are diagnostic; they only show "even under this
pessimistic financing assumption, the result is / is not
*additionally* killed". A pass tells you nothing about whether
real financing would credit or debit, only that the worst case
is bounded.

## 12. Deterministic reproducibility requirements

- Given identical inputs and config, two runs must produce
  bit-identical JSON output. Tests pin this.
- No `datetime.now()` inside calculation paths;
  `FinancingRunReport.generated_at_utc` is the only timestamp
  the module reads from the clock, and it must be injectable in
  tests (`now=` arg defaulting to `utcnow`).
- No randomness, no I/O, no environment-variable reads.
- Decimal arithmetic on cents-scale results to avoid binary
  float drift on JPY-precision pairs (e.g. `USD_JPY` with
  pip_location -2). Internal floats are acceptable for
  diagnostic outputs.

## 13. What must be true before paper / demo promotion

The existing `financing_treatment_blocks_approval` gate in
`src/forex_bot/financing.py` is authoritative.

The new `research/financing/` module is `ESTIMATED` at best. A
campaign using its outputs:

- **may** pass the paper / demo financing gate (same as the
  existing `ConservativeStressFinancingModel`),
- **must not** mark `financing_treatment = MODELED` based on
  this module's outputs alone,
- **must not** be promoted to live based on this module.

For a campaign to legitimately reach `MODELED`:

1. Forward-capture `DAILY_FINANCING` transactions for ≥ 60
   rollovers across the traded universe (the existing
   `ObservedFinancingEventRepo` is the recorder).
2. Build a `MODELED` `FinancingModel` (e.g. an implementation
   of `FutureOandaObservedFinancingModel`) reconciled against
   observed data within a tight tolerance.
3. Wire that model into engine PnL (a new opt-in code path,
   never silently changing historical reproducibility).
4. Get a documented human approval per the strategy approval
   process.

None of these happen in this sprint.

## 14. Output naming and conventions

- `position_id` strings are caller-supplied and opaque to the
  module. Callers should not encode credentials, raw account
  ids, or sensitive metadata into them.
- The module never reads, writes, or transmits credentials.
- JSON dumps use UTF-8, sorted keys, ISO-8601 dates, and 2-space
  indent.
- Markdown rendering is plain CommonMark with no inline HTML.
- Numeric outputs round to 6 decimal places for display;
  internal computation keeps full precision.

## 15. Cross-links

- This sprint's plan:
  [`FINANCING_MODEL_001_PLAN.md`](FINANCING_MODEL_001_PLAN.md)
- Current assumptions audit:
  [`FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`](FINANCING_MODEL_CURRENT_ASSUMPTIONS.md)
- Existing per-trade overlay:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Observed-event capture:
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Decision for CAMPAIGN_002:
  [`../financing_decision.md`](../financing_decision.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

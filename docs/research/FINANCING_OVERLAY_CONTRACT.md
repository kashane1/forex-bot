# Financing Overlay Contract

**Module:** `src/forex_bot/research/financing_overlay.py`  
**Runner:** `scripts/apply_financing_overlay_to_trade_ledgers.py`

## Input contract (trade ledger row)

| Field | Required | Notes |
|-------|----------|-------|
| `instrument` | Yes | Pair id |
| `side` | Yes | `long` / `short` |
| `entry_time` | Yes | ISO-8601 |
| `exit_time` | Yes | Repaired from `bars_held` if ≤ entry |
| `units` | Yes | Position size |
| `entry_price` | Yes | |
| `stop_price` | Preferred | R denominator via `forex_bot.financing.risk_usd` |
| `pnl` | Yes | Home currency gross |
| `r_multiple` | Yes | Gross R |
| `bars_held` | Yes | Hold duration; H4 default 4h/bar |
| `campaign_id` | Ledger meta | |
| `account_currency` | Default USD | |

## Financing rate contract

| Field | Notes |
|-------|-------|
| `instrument` | |
| `long_rate` / `short_rate` | Per rollover day |
| `effective_date` | Calendar date key |
| `source` | e.g. `default_stress`, `manual_fixture_table` |
| `synthetic` | Boolean — must be true for stress/fixture tables |
| `triple_rollover` | Via `FinancingCalculatorConfig` weekday rule |

## Output contract (per ledger summary)

| Field | Description |
|-------|-------------|
| `financing_home` | USD carry (stress total) |
| `financing_r` | financing_home / risk_usd |
| `adjusted_pnl_home` | gross + financing |
| `adjusted_r` | gross_r + financing_r (if risk > 0) |
| `financing_mode` | Mode enum value |
| `rate_source` | Source label |
| `days_held` | bars × hours_per_bar / 24 |
| `rollover_events` | Count from calculator |
| `triple_rollover_events` | Events with multiplier ≥ 3 |
| `warnings` | Repair / unavailable / synthetic labels |

## Modes

| Mode | Behavior |
|------|----------|
| `none` | Gross metrics only; drag = 0 |
| `synthetic_fixture` | `default_stress_rate_source()` |
| `manual_observed_fixture` | Merged `rates_two_week_*.json` + synthetic warning |
| `unavailable` | No rates; overlay skipped |

## Tests

`tests/unit/test_financing_overlay_local_first.py` — long/short signs, multi-day accrual, zero-day repair, none vs synthetic, manifest schema, fixture labeling.

## No-approval statement

Contract is diagnostic infrastructure only.

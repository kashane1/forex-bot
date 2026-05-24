# Edge-discovery study (real data) — real_event_window_continuation_vs_reversal

> Exploratory lab output. Not a strategy verdict; does not approve,
> promote, or change any campaign status. CAMPAIGN_014 remains
> REJECT and CAMPAIGN_011 remains the null model.

## Provenance

- data_kind: `real`
- pair universe: `['AUD_USD', 'EUR_USD', 'GBP_USD', 'NZD_USD', 'USD_CAD', 'USD_CHF', 'USD_JPY']`
- date coverage: `2021-07-02 13:00:00+00:00` → `2025-11-10 14:00:00+00:00`
- inputs:
  - `campaign_trades` — `backtests/CAMPAIGN_014_calendar_event_window_anomaly` — rows=`720` — sha256=`(per-fold per-pa…`
  - `event_fixture_json` — `research/calendar/fixtures/campaign_014_events.json` — rows=`281` — sha256=`584a19a8182bb338…`
  - `campaign_walk_forward_results` — `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json` — rows=`1177` — sha256=`ac6e72942d1a016c…`
- limitations:
  - CPI events are NOT in the committed fixture — coverage is NFP / FOMC / ECB / BoJ / BoE only.
  - Per-trade event class is matched by nearest event within ±24h; trades that don't fall within any event window are bucketed as 'unattributed' rather than dropped silently.
  - This study aggregates over CAMPAIGN_014's published trades — it does NOT re-execute any backtest, change the CAMPAIGN_014 REJECT verdict, or claim strategy evidence.
  - The null baseline is the CAMPAIGN_011 published aggregate_expectancy_r (-0.0024); the lab does NOT regenerate the null here.

## Aggregate vs CAMPAIGN_011 null

- CAMPAIGN_014 overall mean R: **`-0.1477`**
- CAMPAIGN_011 null mean R: **`-0.0024`**
- Gap: **`-0.1453` R** → band: **`materially_below_null`**
- Material-gap floor: `+0.05` R

## Per-class breakdown (matched within ±24h of an event)

| class | n | mean R | median R | win rate | long share | avg spread (pips) | dominance % |
|---|---:|---:|---:|---:|---:|---:|---:|
| BoE | 53 | +0.0129 | -0.4016 | 0.453 | 0.585 | 1.77 | 0.074 |
| BoJ | 47 | -0.0010 | -0.0016 | 0.404 | 0.340 | 1.65 | 0.065 |
| ECB | 49 | +0.0842 | +0.0051 | 0.531 | 0.449 | 1.49 | 0.068 |
| NFP | 571 | -0.1946 | -0.1062 | 0.359 | 0.497 | 1.71 | 0.793 |

- Trades unattributed to any event window: **0** / 720
- Event classes in fixture with zero matched trades: `['FOMC']`

## Continuation vs reversal (long vs short by class)

| class | n long | long mean R | long win rate | n short | short mean R | short win rate |
|---|---:|---:|---:|---:|---:|---:|
| BoE | 31 | -0.2478 | 0.419 | 22 | +0.3802 | 0.500 |
| BoJ | 16 | -0.0019 | 0.375 | 31 | -0.0006 | 0.419 |
| ECB | 22 | -0.2028 | 0.545 | 27 | +0.3180 | 0.519 |
| NFP | 284 | -0.2218 | 0.349 | 287 | -0.1677 | 0.369 |

## Notes

- Exploratory output only — does not approve any strategy.
- CAMPAIGN_014 remains REJECT; this study aggregates its published trades.
- Lab graduation criteria for any future event-window candidate require gap_r >= +0.05 R AND a non-dominant per-class distribution (see EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md).

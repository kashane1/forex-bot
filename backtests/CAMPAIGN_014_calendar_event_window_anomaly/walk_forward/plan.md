# Walk-Forward Plan — CAMPAIGN_014_calendar_event_window_anomaly

> `strategy_evidence: false`. The harness produces fold plans, not strategy verdicts. A clean plan does not approve a strategy.

- Universe: `2020-01-01` → `2026-05-20`
- Split style: `rolling`
- Parameter mode: `frozen`
- Fold count: **8**

## Notes

- Inherits CAMPAIGN_010/011/012/013 plan verbatim (7-pair OANDA-practice H4 universe, 8 folds rolling/frozen 540/180/180/180 days).
- Strategy: calendar_event_window_anomaly 0.1.0-c014 (C7).
- Event fixture: research/calendar/fixtures/campaign_014_events.json (281 events; 2020-01-01 → 2026-05-20 coverage).
- Fixture date-verification audit: PARTIAL — PROCEED WITH EXPLICIT CAVEAT (see CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md).
- Walk-forward is one of several gates; passing it does NOT approve the strategy.

## Folds

| # | train | validation | test |
|---|---|---|---|
| 0 | `2020-01-01` → `2021-06-23` | `2021-06-24` → `2021-12-20` | `2021-12-21` → `2022-06-18` |
| 1 | `2020-06-29` → `2021-12-20` | `2021-12-21` → `2022-06-18` | `2022-06-19` → `2022-12-15` |
| 2 | `2020-12-26` → `2022-06-18` | `2022-06-19` → `2022-12-15` | `2022-12-16` → `2023-06-13` |
| 3 | `2021-06-24` → `2022-12-15` | `2022-12-16` → `2023-06-13` | `2023-06-14` → `2023-12-10` |
| 4 | `2021-12-21` → `2023-06-13` | `2023-06-14` → `2023-12-10` | `2023-12-11` → `2024-06-07` |
| 5 | `2022-06-19` → `2023-12-10` | `2023-12-11` → `2024-06-07` | `2024-06-08` → `2024-12-04` |
| 6 | `2022-12-16` → `2024-06-07` | `2024-06-08` → `2024-12-04` | `2024-12-05` → `2025-06-02` |
| 7 | `2023-06-14` → `2024-12-04` | `2024-12-05` → `2025-06-02` | `2025-06-03` → `2025-11-29` |

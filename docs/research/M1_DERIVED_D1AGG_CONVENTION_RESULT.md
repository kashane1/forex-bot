# M1 Derived D1AGG Convention Result

**Overall status:** WARN (M1-only path); native H4 reference path PASS
**Convention:** Five completed H4 candles (17:00→13:00 NY) per OANDA trading day, timestamp at 13:00 NY close (`D1AGG`).

## Finding

| Source | D1AGG bars (EUR_USD example) | Status |
| --- | ---: | --- |
| M1 → H4 → D1AGG | 0 aggregated | WARN |
| Native H4 → D1AGG | ~1,294 | PASS |

M1-derived H4 produces ~5.2k strict H4 bars, but almost every OANDA trading day is classified **incomplete** when requiring six complete native-slot H4 candles built from M1 (gaps at day boundaries / missing minutes). Native H4 in the store still aggregates to ~1,294 clean D1AGG days.

## Comparison

- Overlap OHLC mismatches: 0 (no M1-derived D1AGG bars to compare).
- Incomplete/ambiguous day counts on M1 path dominate (~1,285+ incomplete days per pair).

## C021 / LTF Confluence Implication

- **Safe now:** M15/M5 execution and H1/H4 context from M1-derived aggregates.
- **D1AGG context for scaffold:** use **native H4-derived D1AGG** from the existing store until an M1 H4 completeness repair sprint closes day-level gaps.
- Does **not** block CAMPAIGN_021 **scaffold** if hybrid provenance is explicit in config/docs.

**Artifacts:** `d1agg_convention_summary.json`, `d1agg_by_pair.csv`

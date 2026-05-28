# M1 Full Corpus LTF Lane Readiness Decision

**Classification:** `READY_WITH_WARNINGS`
**Recommended next sprint:** `research-campaign-021-ltf-mtf-confluence-scaffold-001` (scaffold only — no evidence)

## Inputs

| Layer | Result | Blocks C021 scaffold? |
| --- | --- | --- |
| M1 inventory | PASS — 12,793,196 rows, 7/7 pairs | No |
| M1 quality | WARN — calendar close gaps; no dupes/OHLC violations | No |
| Aggregation M5/M15/H1/H4 | PASS | No |
| H4 drift vs native | WARN — 0 OHLC mismatch on overlap; native-only bars | No |
| D1AGG from M1 | WARN — 0 bars; native H4→D1AGG ~1,294/pair | No if hybrid D1AGG documented |
| LTF/HTF alignment | WARN — no lookahead; D1AGG unavailable on M1-only | No with hybrid |
| LTF preflight | WARN — D1AGG empty on M1-only path | No with hybrid |

## Decision

The **M1 canonical corpus is validated** for lower-timeframe infrastructure. M15 (and M5) execution plus H1/H4 context from M1-derived aggregates are viable. CAMPAIGN_021 scaffold may proceed with explicit provenance:

1. Execution: M1 → M15 (default), M5 optional.
2. Context: M1 → H1/H4.
3. D1AGG: **native H4 → D1AGG** from Postgres until M1-derived trading-day completeness is repaired.
4. **Materialized lane (2026-05-28):** M5/M15/H1/H4M1 available under `source=m1_materialized` via `scripts/materialize_m1_derived_timeframes.py`. CAMPAIGN_021 loader reads these by default.

## Not Approved

- No strategy approval.
- No paper/demo/live enablement.
- No CAMPAIGN_021 evidence in this sprint.

## Optional Repair Sprint (non-blocking)

`infra-m1-h4-trading-day-completeness-001` — improve M1→H4 slot completeness so M1→D1AGG matches native convention (if pure-M1 provenance is required).

## Repair Ingestion

Not required for scaffold.

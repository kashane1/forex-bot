# COT Feature Ingest Design

**Diagnostic only** — `strategy_evidence: false`. **Status: DESIGN_ONLY** for sprint 001.

## Report type

**Traders in Financial Futures (TFF)** — CFTC disaggregated report with leveraged funds and asset manager categories. Preferred over legacy Legacy report for FX/Treasury/VIX positioning research.

## Target contracts (future sprint)

| asset | contract / market | priority |
|---|---|---|
| EUR | Euro FX futures | high |
| GBP | British Pound futures | high |
| JPY | Japanese Yen futures | high |
| AUD | Australian Dollar futures | medium |
| CAD | Canadian Dollar futures | medium |
| CHF | Swiss Franc futures | medium |
| USD index | DX futures if mapped cleanly | medium |
| Treasuries | 2Y/10Y/Ultra Treasury futures | optional |
| VIX | VIX futures | optional |

## Target fields

- leveraged funds: long, short, net
- asset managers: long, short, net (optional)
- open interest
- percent-of-OI where CFTC publishes

## Weekly release / availability lag

- CFTC publishes TFF typically **Friday 3:30 p.m. ET** for Tuesday report date.
- **No-lookahead rule:** use `release_timestamp` (Friday 19:30 UTC approximate) as availability, not Tuesday `report_date`.
- Conservative lag option: `report_date + 3 calendar days @ 00:00 UTC` (matches weekly alignment helper).

## Mapping uncertainty

- Contract name ↔ pair mapping requires maintained lookup table.
- Roll / continuous contract logic is out of scope for sprint 001.
- Net positioning sign conventions must be documented per field.

## Why optional this sprint

- Core confluence diagnostics require daily FRED macro series first.
- COT adds weekly dimension and mapping maintenance cost.
- Live CFTC bulk download/API wiring deferred to `infra-cot-positioning-feature-ingest-001`.

## Sprint 001 deliverable

- Fixture-backed parser stub: `research/cross_asset_features/cot_parser.py` (EUR net only).
- Existing fixture: `tests/fixtures/cross_asset/cot_eur_net.csv`.
- Status output in feature availability: **DESIGN_ONLY** (parser exists; no live ingest).

## No trading claims

COT positioning is research context only. No strategy evidence. No approval path.

# Parity Export Schema Remediation — Result

**Classification:** **WARN** (Backtrader strong; Lean retired)

## Documented fields (Backtrader / bespoke exports)

| Field | Status |
|-------|--------|
| `fill_timing` | In `write_trades_csv`, `write_summary_json` |
| `exit_reason` | In trades CSV |
| Price source | Implicit bid/ask in adapter; documented in `BACKTRADER_DATA_ADAPTER_SPEC.md` |
| `gap_fill_policy` | In summary JSON |
| `campaign_id` | Optional via `write_summary_json(**extras)` — not default |
| `available_data_cutoff` | Available on `Signal` model; export deferred |

## Lean

**Design-only / retired** — no cloud run, no auth this sprint.

## Tests

Existing `tests/unit/backtrader_lane/*`, `tests/research/test_parity_verifier_*` — no new tests required.

## Gaps

- Trade-level `campaign_id` / `available_data_cutoff` columns not added to CSV (artifact width / hash stability)
- Signal-level provenance not yet wired into Backtrader lane

## Recommendation

Next parity sprint: export provenance in **diagnostic** parity bundles only, not historical CAMPAIGN_001–009 folders.

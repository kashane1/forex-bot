# Spread / Cost Regime and Financing Sensitivity Linkage

**Sprint:** `infra-observed-cost-financing-overlay-local-first-001`

## What could be linked

| Dimension | Source | Join key |
|-----------|--------|----------|
| Pair spread / ATR ratio | `research/cost_atlas/pair_session_spread_atr.csv` | `instrument` |
| Cost-hostile windows | `research/cost_atlas/cost_hostile_windows.json` | date + pair |
| Hold bucket | Overlay `overlay_summary_by_hold_bucket.csv` | derived from `bars_held` |
| Financing drag | `overlay_summary_by_pair.csv` | `instrument` |

## What could not be linked (this sprint)

- **Session** at trade level — not stored in campaign trade CSVs; would need bar timestamp → session map replay
- **Weekday** — requires per-trade calendar extraction (future overlay enhancement)
- **Spread paid** — column exists (`spread_paid_pips`) but not aggregated into financing overlay runner yet

## Structurally cost-sensitive patterns (from cost atlas + overlay)

- **Asia / London open** sessions: higher spread/ATR in atlas for several G10 pairs
- **Multi-day holds (3–7d, 7d+):** financing drag scales with rollover count; dominates weekly C016/C017
- **USD_JPY / carry legs:** financing stress and spread stress overlap in prior audits

## Future precommit rules (infrastructure recommendation)

1. Approval-bound multi-day strategies must declare `financing_mode` in campaign manifest
2. Weekly/overnight strategies require financing overlay on trade ledger before promotion review
3. Require `next_bar_open` fill timing unless explicitly justified (separate WARN remediation)
4. Observed financing capture sprint required before treating carry-adjusted metrics as gate inputs

## No strategy recommendation

This document does not recommend enabling any strategy or changing verdicts.

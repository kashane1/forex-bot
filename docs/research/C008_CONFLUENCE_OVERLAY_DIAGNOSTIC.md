# C008 Confluence Overlay Diagnostic

**Diagnostic only** — `strategy_evidence: false`

Source: `research/c008_post_mortem/c008_confluence_overlay.json` — ConfluenceScore computed at each trade entry using existing MTF + cross-asset + cost atlas framework. **Not** A-grade profitability claim.

## C008 grade distribution

| split | A | B | C | REJECT | exp R |
|---|---:|---:|---:|---:|---:|
| train | 88 | 84 | **44** | 0 | −0.025 |
| validation | 74 | 64 | **0** | 0 | +0.161 |
| overall | 162 | 148 | 44 | 0 | +0.048 |

Validation trades received **no C grades**; train had 44 C-grade entries (all with `risk_off_headwind`).

## Top reason codes (C008)

| code | count |
|---|---:|
| d1_aligned | 317 |
| grade_a | 162 |
| usd_headwind | 155 |
| grade_b | 148 |
| risk_off_headwind | 44 |
| grade_c | 44 |
| mixed_htf | 37 |

`cross_asset_missing` **absent** (full-window FRED ingest complete).

## Train losers vs validation winners

| cohort | A | B | C | exp R |
|---|---:|---:|---:|---:|
| train losers (156) | 60 | 64 | 32 | −0.789 |
| validation winners (44) | 22 | 22 | 0 | +2.106 |

Even A/B graded train trades lost when stopped out. Grades describe context, not trade outcome — **no confluence lift claim**.

## C009 comparison (same framework)

| split | exp R | A | B | C |
|---|---:|---:|---:|---:|
| C009 train | −0.025 | 97 | 101 | 54 |
| C009 validation | +0.186 | 78 | 73 | 0 |

C009 train slightly worse than C008; confluence mix broadly similar. Midline exit did not remove C-grade train concentration.

## What this explains

- Train period included more `risk_off_headwind` / C-grade contexts.
- Validation period aligns with cleaner A/B mix — **descriptive**, not causal proof.
- Confluence framework now operational on C008 entries but does **not** justify approval.

## Disclaimer

Descriptive overlay only. No tuning. No strategy approved.

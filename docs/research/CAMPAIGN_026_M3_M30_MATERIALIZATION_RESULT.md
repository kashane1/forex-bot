# CAMPAIGN_026 — M3 / M30 materialization result (Phase 2)

**Status: PASS.** M3 and M30 materialized from canonical M1 for all seven majors;
full-window SQL verification and a bounded exact re-aggregation cross-check both pass
with zero violations. No broker/network calls. No raw data committed.

## Commands run

```
PYTHONPATH=$PWD/src python scripts/materialize_campaign_026_m3_m30.py
# (verify-only re-run: ... --verify-only)
```

Driver: [`scripts/materialize_campaign_026_m3_m30.py`](../../scripts/materialize_campaign_026_m3_m30.py).
It calls the library `materialize_pair` / `verify_materialized_pair` directly and
writes only to `research/campaign_026/materialization/`, so the shared
`research/m1_timeframe_materialization/` canonical manifests are **not** clobbered.

## Network / broker calls

**None.** Derivation reads canonical M1 (`source=oanda-practice-m1`) already in
Postgres. `network_or_broker_calls: false` in the manifest. No OANDA endpoints, no
live credentials.

## Row counts (upserted) and coverage

Elapsed 497.1s. Config hash `f9b7246b79a0635c` (unchanged — see Phase 1 design).
All pairs span **2021-05-27 → 2026-05-26**.

| Pair | M3 rows | M3 omitted | M30 rows | M30 omitted |
|---|---|---|---|---|
| EUR_USD | 606,857 | 13,043 | 56,671 | 5,604 |
| GBP_USD | 602,436 | 16,728 | 55,863 | 6,411 |
| USD_JPY | 608,321 | 11,400 | 57,767 | 4,508 |
| AUD_USD | 591,765 | 26,763 | 52,459 | 9,802 |
| USD_CAD | 601,816 | 17,473 | 55,339 | 6,939 |
| USD_CHF | 573,219 | 40,198 | 50,192 | 12,072 |
| NZD_USD | 594,912 | 22,606 | 52,125 | 10,149 |
| **Total** | **≈ 4.18M** | — | **≈ 380K** | — |

Omitted blocks are incomplete buckets (weekend/session edges, M1 gaps) dropped by the
`omit` completeness policy — never fabricated. USD_CHF has the most omissions,
consistent with its thinner M1 history (also seen in C025).

## Verification status

**PASS for all 7 pairs × {M3, M30}.**

- **Full-window SQL checks** (every stored bar): `duplicate_buckets=0`,
  `misaligned_buckets=0` (every timestamp on a 3-/30-min boundary, zero seconds),
  `ohlc_ordering_violations=0` (high ≥ o/c, low ≤ o/c, high ≥ low for bid & ask),
  `bidask_ordering_violations=0` (ask_c ≥ bid_c), `incomplete_buckets_stored=0`.
- **Exact re-aggregation cross-check** (bounded 45-day sample per pair): re-aggregated
  M1→M3/M30 and asserted byte-for-byte OHLC equality with stored bars — `missing=0`,
  `extra=0`, `ohlc_mismatches=0` for all pairs.
- **M30-from-M1 vs M30-from-M15**: not separately materialized; M30 derives directly
  from M1 (bucket-start, complete-only), the same canonical source as M15, so the two
  would agree by construction on complete buckets. Direct-from-M1 is authoritative.

## Warnings

- USD_CHF thinner coverage (more omitted blocks) — expected, not a defect.
- The shared `m1_timeframe_materialization.verify_materialized_pair` has a latent
  cosmetic bug in its mismatch-label f-string (`field` vs `price_field`) that would
  only execute on an OHLC mismatch; none occurred, so it never triggered. Out of scope
  for this sprint (not C026 code); flagged for a future cleanup.

## Local files (committed — compact JSON only, no raw candles)

Under `research/campaign_026/materialization/`:
`m3_m30_materialization_manifest.json`, `m3_coverage_summary.json`,
`m30_coverage_summary.json`, `m3_m30_ohlc_verification.json`,
`m3_m30_gap_summary.json`, `m3_m30_provenance_summary.json`.

The materialized **bars themselves** live in Postgres (`market_data.candles`,
`source=m1_materialized`, granularity `M3`/`M30`) and are **not** committed.

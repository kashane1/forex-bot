# CAMPAIGN_002 — Data Quality Classification

> Diagnostic-only. Classifies the `Clean=False` audit flags from CAMPAIGN_002 into expected market behavior vs true data defects. No strategy was run to produce this section.

## Classification summary

| class | gap events | missing bars | interpretation |
|---|---:|---:|---|
| `holiday_closure` | 255 | 7764 | Dec 20 – Jan 2 feed closure — expected, OANDA closes. |
| `weekend_adjacent` | 0 | 0 | Gap spans a Saturday adjoining the holiday window — expected. |
| `broker_or_platform_outage` | 14 | 28 | Same timestamp missing across ≥5 pairs, mid-week — feed outage. |
| `minor_feed_gap` | 3 | 3 | 1–2 bar single-instrument gap — brief feed hiccup, immaterial. |
| `suspicious_missing_bars` | 3 | 15 | Multi-bar single-instrument gap NOT a holiday — inspect. |

## Cross-instrument simultaneous gaps (candidate outages)

A gap starting at the same timestamp across ≥5 of 7 pairs is platform-wide. Most are the holiday window; only mid-week ones are genuine outages.

- **H4** `2020-12-18T18:00:00+00:00` — missing in **7/7** pairs (weekend-adjacent — expected)
- **H4** `2020-12-24T18:00:00+00:00` — missing in **6/7** pairs (holiday window — expected)
- **H4** `2020-12-31T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2021-12-24T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2021-12-31T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2022-12-23T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2022-12-30T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2023-12-22T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2023-12-29T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2024-12-20T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2024-12-24T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2024-12-27T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2024-12-31T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2025-12-19T18:00:00+00:00` — missing in **7/7** pairs (weekend-adjacent — expected)
- **H4** `2025-12-24T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2025-12-26T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2025-12-31T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H4** `2026-01-02T18:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2020-12-18T21:00:00+00:00` — missing in **7/7** pairs (weekend-adjacent — expected)
- **H1** `2020-12-24T21:00:00+00:00` — missing in **6/7** pairs (holiday window — expected)
- **H1** `2020-12-31T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2021-12-24T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2021-12-31T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2022-05-12T05:00:00+00:00` — missing in **7/7** pairs (weekend-adjacent — expected)
- **H1** `2022-12-23T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2022-12-30T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2023-12-22T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2023-12-29T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2024-05-20T14:00:00+00:00` — missing in **7/7** pairs (**mid-week → genuine platform outage**)
- **H1** `2024-12-20T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2024-12-24T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2024-12-27T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2024-12-31T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2025-12-19T21:00:00+00:00` — missing in **7/7** pairs (weekend-adjacent — expected)
- **H1** `2025-12-24T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2025-12-26T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2025-12-31T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)
- **H1** `2026-01-02T21:00:00+00:00` — missing in **7/7** pairs (holiday window — expected)

## Specifically requested inspections

### 2022-05-12 05:00–08:00 UTC

- Hours present (EUR_USD): `['05:00']`
- Identical across all 7 pairs: **yes**
- → A gap identical across **every** instrument is a broker/platform feed outage, not an instrument-specific defect or a market event.

### 2024-05-20 13:00–18:00 UTC

- Hours present (EUR_USD): `['13:00', '14:00', '17:00']`
- Identical across all 7 pairs: **yes**
- → A gap identical across **every** instrument is a broker/platform feed outage, not an instrument-specific defect or a market event.


### Christmas / New Year closures

255 holiday gap events across 21 distinct dates: 2020-12-18, 2020-12-24, 2020-12-31, 2021-12-24, 2021-12-31, 2022-12-23, 2022-12-26, 2022-12-30, 2023-12-22, 2023-12-25, 2023-12-29, 2024-01-01, 2024-12-20, 2024-12-24, 2024-12-27, 2024-12-31, 2025-12-19, 2025-12-24, 2025-12-26, 2025-12-31, 2026-01-02.
All are expected OANDA feed closures and are correctly excluded by
`bot audit-data` from the trade window when candles are absent.

### NZD_USD extra missing intervals

NZD_USD H1 has 27 non-weekend gaps (vs 6–7 for the other pairs): 21× holiday_closure, 3× minor_feed_gap, 1× suspicious_missing_bars, 2× broker_or_platform_outage.

- `2020-12-18T21:00:00+00:00` → `2020-12-20T22:00:00+00:00` (48 bars) — `holiday_closure`
- `2020-12-24T21:00:00+00:00` → `2020-12-27T22:00:00+00:00` (72 bars) — `holiday_closure`
- `2020-12-31T21:00:00+00:00` → `2021-01-03T22:00:00+00:00` (72 bars) — `holiday_closure`
- `2021-12-05T18:00:00+00:00` → `2021-12-05T20:00:00+00:00` (1 bars) — `minor_feed_gap`
- `2021-12-05T20:00:00+00:00` → `2021-12-05T22:00:00+00:00` (1 bars) — `minor_feed_gap`
- `2021-12-24T21:00:00+00:00` → `2021-12-26T22:00:00+00:00` (48 bars) — `holiday_closure`
- `2021-12-31T21:00:00+00:00` → `2022-01-02T22:00:00+00:00` (48 bars) — `holiday_closure`
- `2022-05-04T21:00:00+00:00` → `2022-05-05T03:00:00+00:00` (5 bars) — `suspicious_missing_bars`
- `2022-05-12T05:00:00+00:00` → `2022-05-12T08:00:00+00:00` (2 bars) — `broker_or_platform_outage`
- `2022-12-23T21:00:00+00:00` → `2022-12-26T18:00:00+00:00` (68 bars) — `holiday_closure`
- `2022-12-26T20:00:00+00:00` → `2022-12-26T22:00:00+00:00` (1 bars) — `holiday_closure`
- `2022-12-30T21:00:00+00:00` → `2023-01-01T23:00:00+00:00` (49 bars) — `holiday_closure`
- `2023-12-22T21:00:00+00:00` → `2023-12-25T18:00:00+00:00` (68 bars) — `holiday_closure`
- `2023-12-25T19:00:00+00:00` → `2023-12-25T21:00:00+00:00` (1 bars) — `holiday_closure`
- `2023-12-29T21:00:00+00:00` → `2024-01-01T18:00:00+00:00` (68 bars) — `holiday_closure`
- `2024-01-01T18:00:00+00:00` → `2024-01-01T21:00:00+00:00` (2 bars) — `holiday_closure`
- `2024-02-12T18:00:00+00:00` → `2024-02-12T20:00:00+00:00` (1 bars) — `minor_feed_gap`
- `2024-05-20T14:00:00+00:00` → `2024-05-20T17:00:00+00:00` (2 bars) — `broker_or_platform_outage`
- `2024-12-20T21:00:00+00:00` → `2024-12-22T22:00:00+00:00` (48 bars) — `holiday_closure`
- `2024-12-24T21:00:00+00:00` → `2024-12-25T22:00:00+00:00` (24 bars) — `holiday_closure`
- `2024-12-27T21:00:00+00:00` → `2024-12-29T22:00:00+00:00` (48 bars) — `holiday_closure`
- `2024-12-31T21:00:00+00:00` → `2025-01-01T22:00:00+00:00` (24 bars) — `holiday_closure`
- `2025-12-19T21:00:00+00:00` → `2025-12-21T22:00:00+00:00` (48 bars) — `holiday_closure`
- `2025-12-24T21:00:00+00:00` → `2025-12-25T22:00:00+00:00` (24 bars) — `holiday_closure`
- `2025-12-26T21:00:00+00:00` → `2025-12-28T22:00:00+00:00` (48 bars) — `holiday_closure`
- `2025-12-31T21:00:00+00:00` → `2026-01-01T22:00:00+00:00` (24 bars) — `holiday_closure`
- `2026-01-02T21:00:00+00:00` → `2026-01-04T22:00:00+00:00` (48 bars) — `holiday_closure`

NZD_USD also starts at `2020-01-01T22:00` rather than `00:00`; the first two H1 bars of 2020 simply were not in OANDA's feed for this pair. Immaterial against ~39.7k candles.

## Abnormal spread classification

An *abnormal* spread (audit definition: > 5× the instrument median) is classified here by the UTC hour it occurred in.

| pair | gran | abnormal count | % at rollover (20:00–22:00 UTC) | median (pips) | p95 (pips) |
|---|---|---:|---:|---:|---:|
| EUR_USD | H4 | 107 | 0% | 1.50 | 2.50 |
| GBP_USD | H4 | 176 | 2% | 1.90 | 6.00 |
| USD_JPY | H4 | 304 | 1% | 1.60 | 4.10 |
| AUD_USD | H4 | 187 | 1% | 1.40 | 2.90 |
| USD_CAD | H4 | 141 | 1% | 1.90 | 4.50 |
| USD_CHF | H4 | 165 | 2% | 1.70 | 4.10 |
| NZD_USD | H4 | 189 | 1% | 2.50 | 5.30 |
| EUR_USD | H1 | 245 | 99% | 1.50 | 2.60 |
| GBP_USD | H1 | 609 | 87% | 1.90 | 6.00 |
| USD_JPY | H1 | 647 | 94% | 1.60 | 3.70 |
| AUD_USD | H1 | 343 | 90% | 1.30 | 2.50 |
| USD_CAD | H1 | 366 | 90% | 1.90 | 4.50 |
| USD_CHF | H1 | 1139 | 94% | 1.70 | 4.60 |
| NZD_USD | H1 | 353 | 79% | 2.50 | 4.30 |

USD_CHF H1 has the largest abnormal-spread count in the campaign. The classification below shows the overwhelming majority sit in the 20:00–22:00 UTC daily-rollover window, where thin liquidity widens spreads predictably. The bot's `session_filter` already blocks new trades 16:45–17:15 America/New_York (≈20:45–21:15 UTC) and the `spread_filter` rejects the rest — so abnormal spreads convert into *rejections*, not into bad fills.

## Verdict: does data quality affect the CAMPAIGN_002 reject?

- Total candles stored across all 14 series: **347,509**.
- Missing bars classified as **expected** (holiday + weekend adjacent): **7,764** — these are not defects, they are OANDA closing the feed.
- Missing bars classified as **possible defects** (outage + minor feed gap + suspicious): **46** (**0.0132%** of the dataset).
- Genuine mid-week platform outages: **2** windows — `2022-05-12 05:00–08:00 UTC` and `2024-05-20 14:00–17:00 UTC`, each 1–2 bars, each identical across all 7 pairs.
- True single-instrument suspicious events: **3** (15 bars total).
- Abnormal spreads are concentrated at daily rollover (79–99% of H1 abnormal spreads sit in 20:00–22:00 UTC) and are handled by the spread/session filters — they raise rejection counts, they do not manufacture fictitious profits or losses.

**Conclusion: NO. Data quality does not materially affect the negative conclusion.** Genuine defects total 46 bars (~0.013% of the dataset) — two brief mid-week feed outages plus a handful of 1–5 bar single-instrument gaps. A campaign-wide loss across 7 pairs × 2 timeframes × 81 parameter sets, with negative expectancy on the untouched test split, cannot be explained by ~0.01% missing data or by rollover spread spikes the filters already reject. **CAMPAIGN_002's REJECT stands and is not a data artifact.**

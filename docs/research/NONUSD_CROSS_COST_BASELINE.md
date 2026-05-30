# Non-USD Cross Cost Baseline (Sprint 001, Phase 5)

**Sprint:** `research-nonusd-cross-data-population-001`
**Source:** measured M1 close spreads `(ask_c − bid_c)/pip_size` over
2021-05-26 → 2026-05-26 (the same window as the majors).
**Status:** **DESCRIPTIVE ONLY.** No edge discovery, no factor work, no
strategy, no campaign. These are spread/cost facts about the data, not
signals.

## Spread distribution (pips) — crosses

| Cross | n (M1) | mean | median | p90 | p99 | std |
|-------|--------|------|--------|-----|-----|-----|
| EUR_GBP | 1,823,232 | 1.68 | 1.4 | 1.8 | 8.4 | 1.28 |
| AUD_JPY | 1,857,000 | 2.26 | 1.9 | 2.5 | 11.7 | 1.76 |
| EUR_CHF | 1,811,686 | 1.97 | 1.6 | 2.1 | 12.3 | 1.72 |
| EUR_JPY | 1,841,779 | 2.45 | 2.1 | 2.9 | 13.1 | 1.70 |
| GBP_CHF | 1,838,790 | 2.74 | 2.2 | 3.0 | 19.9 | 3.22 |
| NZD_JPY | 1,845,840 | 2.85 | 2.5 | 3.3 | 14.7 | 2.24 |
| EUR_AUD | 1,849,425 | 3.25 | 2.6 | 4.1 | 17.8 | 2.72 |
| GBP_JPY | 1,852,770 | 3.67 | 3.1 | 4.1 | 17.3 | 3.04 |

## Spread distribution (pips) — USD majors (control)

| Major | mean | median | p90 | p99 | std |
|-------|------|--------|-----|-----|-----|
| AUD_USD | 1.45 | 1.3 | 1.5 | 4.9 | 0.79 |
| EUR_USD | 1.63 | 1.5 | 1.7 | 4.9 | 0.65 |
| NZD_USD | 1.74 | 1.5 | 1.9 | 7.0 | 1.21 |
| USD_CHF | 1.86 | 1.6 | 1.9 | 11.8 | 1.56 |
| USD_JPY | 1.83 | 1.7 | 2.1 | 7.3 | 0.94 |
| GBP_USD | 2.14 | 1.9 | 2.3 | 9.9 | 1.50 |
| USD_CAD | 2.06 | 1.9 | 2.3 | 7.3 | 1.06 |

## Session spread medians (pips)

| Instrument | asian | london | overlap | ny |
|------------|-------|--------|---------|----|
| EUR_GBP | 1.4 | 1.4 | 1.6 | 1.5 |
| EUR_JPY | 2.0 | 1.9 | 2.5 | 2.1 |
| GBP_JPY | 3.0 | 2.9 | 3.6 | 3.3 |
| AUD_JPY | 1.9 | 1.9 | 2.3 | 2.0 |
| *EUR_USD (major)* | 1.5 | 1.5 | 1.6 | 1.6 |
| *USD_JPY (major)* | 1.7 | 1.6 | 1.9 | 1.7 |

Session bins follow the cost-atlas convention (asian = 22:00–06:00 UTC,
london 06:00–12:00, overlap 12:00–16:00, ny 16:00–22:00).

## Findings (descriptive)

1. **Crosses are wider than the comparable majors**, but the gap varies:
   - **EUR_GBP (median 1.4p)** is *competitive with the tightest majors*
     (EUR_USD 1.5p, AUD_USD 1.3p) — the cheapest cross.
   - **AUD_JPY (1.9p)** and **EUR_CHF (1.6p)** are moderate, in the band of
     the wider majors (GBP_USD/USD_CAD 1.9p).
   - **GBP_JPY (3.1p)** and **EUR_AUD (2.6p)** are the widest — roughly 1.5–2×
     the typical major.
   - Measured medians match the feasibility study's qualitative bands
     (near-major EUR_GBP/EUR_JPY; moderate AUD_JPY/EUR_CHF/EUR_AUD; wide
     GBP_JPY/NZD_JPY/GBP_CHF).

2. **Tail risk is materially higher on crosses.** Cross p99 spreads run
   **8.4–19.9p** vs majors **4.9–11.8p**, and spread **volatility (std) is
   ~1.3–3.2p vs ~0.65–1.5p** for majors. GBP_CHF and GBP_JPY have the
   fattest tails. Crosses are not just wider on average — they are *less
   stable*, which matters more for any cost-sensitive strategy than the
   median.

3. **Right-skew.** For every cross `mean > median` by more than on the
   majors (e.g. GBP_JPY mean 3.67 vs median 3.1), confirming occasional
   wide-spread excursions (rollover, news, thin sessions) pull the average up.

4. **Session shape mirrors the majors.** Spreads are tightest in the
   london session, widen through the london/NY overlap, and the overlap
   p90 (not shown here; see validation doc) captures rollover/news spikes —
   the same intraday shape the majors show, just shifted wider.

## Interpretation (still descriptive)

This baseline **confirms the standing thesis**: non-USD crosses are a
**breadth/replication expansion, not a cost fix**. Their spreads — and
especially their tails and volatility — are wider than the majors that the
whole prior programme was *already* cost-defeated on. EUR_GBP (and to a
lesser extent AUD_JPY / EUR_CHF) are the only crosses whose central spread
approaches major-pair levels; the JPY/AUD-wide crosses carry a clearly
higher cost wall.

**No edge claim is made or implied.** Whether any cross supports a
cost-surviving effect is a *future* front-gate question, explicitly out of
scope for this sprint. The `cost_models` round-trip + two-legged-carry
machinery (built in the prior sprint) will consume these measured spreads
when that question is eventually asked.

Artifacts: `research/nonusd_cross_population/cost_baseline.{json,csv}`.

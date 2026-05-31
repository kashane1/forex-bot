# Carry Factor — Construction (Phase 2)

**Sprint:** `research-carry-factor-validation-001` · Phase 2
**Type:** factor **exposure** construction — research-only. No forward returns are
computed in this phase; no trades, no entry/exit, no PnL, no cost, no approval.
**Date:** 2026-05-31.

Implements §4 of the frozen [CARRY_FACTOR_PROTOCOL.md](CARRY_FACTOR_PROTOCOL.md).
Code: `research/carry/carry_factor.py`; runner `scripts/run_carry_factor_validation.py`;
artifacts under `research/carry/factor_validation/`. Tests:
`tests/research/carry/test_carry_factor.py` (11 passed).

---

## 1. Inputs (both reused unmodified)

| Input | Source | Role |
|---|---|---|
| Per-currency monthly interbank rate | `docs/research/carry_rates/rate_series.csv` → `carry_rates.monthly_rate_matrix` | the carry **signal** |
| Month-end spot mid (7 majors) | `data/campaign_002.sqlite3` H1, `(bid_c+ask_c)/2`, last bar per month | the **return** substrate |

The study window resolves to **61 month-starts** (2021-05 → 2026-05); the realised
count is read from the artifact, not assumed.

## 2. From 7 majors to 8 currencies and 15 instruments (no-arbitrage)

- **USD value of each currency** (`currency_usd_levels`): base-majors give USD-per-base
  directly (EUR_USD → EUR); quote-majors invert (USD_JPY → JPY = 1/price); USD ≡ 1.
  This yields all **8** currencies' USD-value series from the 7 real-data majors.
- **Instrument log-price** (`instrument_log_levels`): `ln price(B_Q) = lnL_B − lnL_Q`,
  reconstructing all **15** instruments' gross mid path by no-arbitrage. A unit test
  (`test_instrument_return_is_sum_of_usd_legs`) pins this identity.

This is the construction that lets the full cross-section be studied **gross** without
the 8 crosses' own bars — and it carries **no** cost information (deliberately, this is
a gross study).

## 3. Carry exposures built (the only Phase-2 output)

At each monthly rebalance, with the rate signal lagged **1 month** (primary, §3 of the
protocol):

- **Currency HML-3** (`hml_weights`, k=3): long top-3 / short bottom-3 of the 8
  currencies by interbank rate, equal weight, **dollar-neutral** (Σw=0) with **gross
  exposure 2** (Σ|w|=2). Unit tests confirm neutrality and that it longs the top / shorts
  the bottom.
- **Currency HML-2** (k=2) and **rank-weighted** (continuous, rank-centered, Σ|w|=2) —
  robustness variants.
- **Instrument HML-4** (m=4): long top-4 / short bottom-4 of the 15 instruments by carry
  — the secondary consistency layer.

## 4. Realised exposure composition (read from the artifact)

The currency HML-3 book is, over the 61 months, an almost **static** tilt — the carry
ranking barely moves (month-over-month Spearman rank stability **0.984** for currencies,
**0.991** for instruments):

| Side | Currencies (months in basket / 60 rebalances) |
|---|---|
| **Long (high rate)** | USD (57), GBP (44), NZD (42), CAD (19), AUD (18) |
| **Short (low rate)** | EUR (60), JPY (60), CHF (60) |

So the book is, essentially every month: **short JPY / CHF / EUR (the funders), long
USD / GBP / NZD (the high-yielders)** — the textbook carry tilt. Mean gross exposure is
2.0 by construction. The instrument HML-4 layer concentrates the same bet (its longs are
dominated by JPY-crosses such as AUD_JPY/NZD_JPY, i.e. *more* short-JPY exposure).

**This near-static, JPY-funded character is the single most important property of the
exposure** — it is what later makes the timing-null (shuffled-timestamp) degenerate and
the premium dependent on the JPY leg (Phases 4–5).

## 5. What was NOT built

No forward return, no Sharpe, no signal-to-trade mapping, no entry/exit, no cost, no
approval. Phase 2 produces **weights and their composition only**; the response is
measured in Phase 3 against the frozen protocol.

# CAMPAIGN_027_RECENCY_AND_ROBUSTNESS_INTERPRETATION

**Status:** TRAIN/VALIDATION EXECUTION — Phase 7 / REJECT_TRAIN_GATE /
TEST_LOCKBOX_CLOSED / NOT_APPROVED. Branch
`research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`.

Addresses the pre-registered known risk that 2024 and 2026-partial were
weak/negative in the front gate. Because the frozen rule **failed the train gates**,
validation (2023–2024) was **not run** — so the 2024 recency gate could not even be
reached. This document interprets the year/pair/session robustness that *is*
available (train) and states the deterioration verdict.

> Inputs: `research/campaign_027/train_validation/recency_risk_report.json`,
> `train_metrics.json`, `pair_metrics_train.csv`, `year_metrics_train.csv`.

---

## Year-by-year metrics (train; conservative expectancy/trade)

| year | expectancy (conservative) | sign |
|---|---|---|
| 2020 | −0.00057092 | − |
| 2021 | −0.00029217 | − |
| 2022 | +0.00119291 | + |

Only **1/3** train years positive. The two earliest years are negative; the entire
apparent train edge is a **single-year (2022) artifact**.

## 2023 vs 2024 validation comparison

**Not available.** Validation was not run (train gates failed; validation is
confirmation, never a rescue). The 2024 recency gate
(`validation_2024_not_materially_negative`) was therefore never reached — the
campaign was rejected upstream of it.

## Is 2024 materially negative?

**Undetermined this sprint** (validation not run). The front-gate evidence already
flagged 2024 negative under conservative cost; nothing here rehabilitates it, and
the train evidence (only 2022 positive) gives no reason to expect 2023–2024 to
clear the gate. The recency risk is **unresolved and unfavourable**, consistent
with the precommit's binding kill condition #4.

## Is 2026 outside validation/test (or only diagnostic)?

2025–2026 sit entirely inside the **sealed test lockbox** (2025-01-01 →
2026-05-20), which was **not opened or read** this sprint. 2026 is neither
validated nor diagnosed here — it remains sealed.

## Pair robustness (train; conservative expectancy/trade)

| pair | expectancy | sign |
|---|---|---|
| AUD_USD | +0.00223 | + |
| EUR_USD | +0.00056 | + |
| NZD_USD | +0.00045 | + |
| USD_CAD | +0.00044 | + |
| USD_JPY | −0.00052 | − |
| USD_CHF | −0.00082 | − |
| GBP_USD | −0.00197 | − |

4/7 positive, but the edge is **concentrated in AUD_USD** (+0.00223, ≈4× the next
pair); three pairs are clearly negative. The front gate claimed 6/7 pair-robustness
on the *information* subset — the realized execution shows only 4/7 and a single
dominant pair. Notably **USD_JPY is negative** on the realized ledger, confirming
the precommit's "USD_JPY is not a standalone thesis / `LIKELY_SELECTION_NOISE`"
caution: the cost-advantaged pair does not carry the strategy.

## Session robustness

Entries are restricted by the frozen quiet-session filter to {asia, london}. The
filter-ablation confirms `f_quiet_session` adds edge (+0.00034) on the campaign's
own data, so the session structure itself is robust — but it is not enough to lift
the realized post-cost result over the gates.

## Is the idea deteriorating?

**Yes, on the available evidence.** The realized, executable version of the front-
gate information signal:

- is post-cost **net-marginal** (expectancy +0.00012, PF 1.043) and **negative
  under 2× cost stress** — inside the cost band, as warned;
- is **single-year-dominated** (only 2022 positive) — the filters did **not** cure
  the year-fragility on the campaign's own ledger;
- is **single-pair-dominated** (AUD_USD), with USD_JPY negative;
- loses its third retained filter (`f_strong_extension`) on re-derivation
  (forking-path).

These are exactly the pre-registered kill conditions (#1-ish marginal, #3 pair
concentration, #4 recency/year, #6 filter ablation, #7 cost stress).

## Should it proceed to parity?

**No.** Parity is only warranted for a rule that passed train + validation. This
rule failed multiple binding train gates; building Backtrader parity for a rejected
rule would be wasted effort (see
[`CAMPAIGN_027_BACKTRADER_PARITY_READINESS.md`](CAMPAIGN_027_BACKTRADER_PARITY_READINESS.md)).

## Should it be rejected?

**Yes — `REJECT_TRAIN_GATE`.** The information edge is real but does not become a
tradable, cost-surviving, robust strategy on a clean split. Per the freeze, the
verdict is REJECT, not a re-tune.

## No-approval statement

No strategy is approved. `configs/approved_strategies.yaml` stays `approved: []`.
The test lockbox was not opened; paper/demo/live remain blocked.
</content>

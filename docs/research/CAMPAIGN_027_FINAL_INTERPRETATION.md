# CAMPAIGN_027_FINAL_INTERPRETATION

**Status:** TRAIN/VALIDATION EXECUTION — Phase 9 / **REJECT_TRAIN_GATE** /
TEST_LOCKBOX_CLOSED / NOT_APPROVED. Branch
`research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`.

Final verdict for the single idea that survived the edge-discovery front gate
(`h4_filtered_zscore_reversion 0.1.0-c027`), after running train evidence on the
campaign's own ledgers under the binding conservative cost.

---

## Final verdict

**REJECT_TRAIN_GATE.** The frozen rule failed **4 of 8 binding train gates**.
Validation was not run (confirmation, not a rescue); the test lockbox stays sealed.
Per the freeze, the verdict is REJECT — not a re-tune. The campaign is closed.

## Did the front-gate signal survive real train/validation?

**No (it did not reach validation).** The front-gate *information* signal is real
and reproduced (the strategy sits above the structure-matched null at ~90th
percentile on every informative mode). But the campaign existed to test whether
that information became a **tradable** strategy on a clean split with the approval-
bound execution model (`next_bar_open` + protective stop + conservative financing
cost). On the campaign's own train ledger it did **not**: the realized post-cost
edge is net-marginal and fails profit-factor, year-robustness, cost-stress, and
filter-ablation gates — so validation was never reached.

## Did edge remain after conservative cost?

**Barely, then no.** Train conservative expectancy is +0.00011974/trade (PF 1.043,
hit 0.50) — inside the cost-assumption band, exactly as the precommit warned. Under
**2× cost stress it goes negative** (−0.00007745, PF 0.973). The edge does not
clear the cost band robustly.

## Did 2024 recency risk kill the idea?

**It never had to.** The idea was rejected upstream at the train gate, so the 2024
recency gate (in the un-run validation window) was never reached. But the train
year profile (only 2022 positive; 2020 and 2021 negative) is itself a
single-year-dominance failure, and the front gate had already flagged 2024 negative
— the recency risk is unresolved and unfavourable.

## Did filters still add edge?

**Two of three retained filters: yes; the third: no.** On the campaign's own train
funnel, `f_low_vol` (+0.000572) and `f_quiet_session` (+0.000339) re-derive
`FILTER_ADDS_EDGE`. `f_strong_extension` (|z|≥2.5) adds only +0.000034 →
`FILTER_ONLY_REDUCES_SAMPLE` — the pre-registered **filter forking-path risk**
materializing (front gate had +0.000208). The dropped filters behave as expected
(`f_long_side` hurts → short-only confirmed; `f_cost_adv_pair` only reduces sample).

## Did matched-null still pass?

**Yes (information), and it was never the weak point.** Above the structure-matched
null on timestamp / session / full modes (pctl 90); `side_shuffled` degenerate for
a short-only ledger. The null means are negative, so "above null" = "loses less
than random," not "makes money." The matched-null gate passed; the realized
profitability gates did not.

## Did pair / year robustness pass?

**No.** Pairs 4/7 positive but **AUD_USD-dominated** (≈4× the next pair) with
USD_JPY negative; years **1/3** positive (single-year 2022 artifact). Both fall
short of the robust, broad-based edge a tradable strategy needs.

## Did cost stress pass?

**No.** 2× conservative cost turns train expectancy negative (−0.00007745).

## Is Backtrader parity warranted?

**No — `DEFER_PARITY_REJECTED`.** Parity reproduces a *passing* result before
promotion; there is no passing result. See
[parity readiness](CAMPAIGN_027_BACKTRADER_PARITY_READINESS.md).

## Why no approval is granted

Approval is a separate, reviewed human edit to
`configs/approved_strategies.yaml`, available only after a precommitted champion
passes train + validation, survives Backtrader parity, and clears a human-gated
single-use test. CAMPAIGN_027 failed at the first of those (train). Nothing is
approved; `approved: []` is unchanged; `promotion_eligible: false`;
`paper_demo_live_enabled: false`; the test lockbox was not opened.

## Recommended next step

**Close the `h4_filtered_zscore_reversion` family** (the last surviving
edge-discovery front-gate idea). Mark CAMPAIGN_027 `REJECT_TRAIN_GATE` in the
status/index/manifest/backlog. Revival requires a **new external thesis or new
data** (per the standing restart criteria) — **not** a parameter tweak, a different
filter set, a long side, or a re-mined window, all of which are forbidden by the
freeze. Practically: the wafer-thin reversion *information* on H4 is genuine but is
consumed by realized execution friction and conservative cost; the program's
front-gate battery (now including the matched-null/filter-ablation/cost-feasibility
lab) correctly admitted one borderline idea and the campaign discipline correctly
rejected it before any capital or lockbox exposure. The lab remains the mandated
front gate for any future search.

## No-approval statement

No strategy is approved. `configs/approved_strategies.yaml` stays `approved: []`.
The test lockbox was not opened; paper/demo/live remain blocked. No
broker/executor/OANDA endpoint was touched.
</content>

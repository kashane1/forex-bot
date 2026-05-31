# C1 High-Volatility Front-Gate Screen — Plan (Phase 0 audit)

**Status:** PLAN (front-gate screen only; no campaign, no strategy, no approval)
**Date:** 2026-05-29
**Branch:** `research-c1-high-volatility-frontgate-001` (off clean `origin/main`)
**Type:** front-gate SCREEN (pre-registered, single pass). **Not** a campaign,
**not** a strategy, **not** entry/exit rules, **not** train/validation/test.
Freeze intact.

---

## 0. What this screen is

The C1 factor-validation sprint (`research-c1-factor-validation-001`, on
`origin/main`) returned **`FACTOR_FRONT_GATE_CANDIDATE`** for
`C1_trend_cont_long` (fade full H4+H1+M15 bullish alignment → 30–60-min downward
reversion). Audited conclusions (read from the committed C1 docs):

- **Genuine factor** — sign negative on **7/7** majors; null-surviving on EUR_USD
  (matched-Z60 −4.21) and USD_JPY (−3.55). (`C1_CROSS_PAIR_STUDY.md`)
- **Persistent** across years (neg 5/6) and all 4 sessions; reversion grows
  monotonically with volatility (hi-ATR tertile t −3.78) and extension.
  (`C1_REGIME_STABILITY_STUDY.md`)
- **Not a USD artifact** — no base/quote sign-flip, symmetric long/short, low
  cross-pair synchrony. (`C1_USD_CONFOUND_STUDY.md`)
- **Not a spec mirage** — sign stable in 55/56 spec×pair perturbations.
  (`C1_ROBUSTNESS_STUDY.md`)
- **Cost-defeated unconditionally** (best EUR_USD 0.73× spread), but one
  **volatility-conditioned** path showed positive spread-adjusted reversion that
  survived an outlier check. (`C1_COST_REALISM_STUDY.md`, `C1_FACTOR_VERDICT.md`)

This screen tests **that one path** — and only it — under realistic execution
assumptions, with a **pre-committed** pass/fail rule, to decide whether it merits
a future campaign *scaffold*. It is the single screen the verdict authorised.

## 1. The make-or-break question

> Does **volatility-conditioned C1 mean-reversion** survive realistic execution
> assumptions, beat a matched null, and prove stable — strongly enough to justify
> a future campaign scaffold?

Three outcomes only: `FAIL_FRONT_GATE`, `INCONCLUSIVE`, `PASS_FRONT_GATE`.

## 2. Integrity rules specific to a screen

- **The hypothesis and all numeric thresholds are frozen in Phase 1
  (`C1_HIGH_VOL_HYPOTHESIS.md`) and committed BEFORE any conditioned number is
  computed.** No threshold is altered after viewing results. No parameter is
  optimised. This is the whole point of a front gate.
- **Same-corpus caveat, stated up front.** The volatility path was *discovered*
  on this very 2021–2026 corpus (EUR_USD/USD_JPY) during validation. A true
  hold-out does not exist here (the hard rules forbid train/val/test, and the
  store has no extra data). The screen therefore treats **GBP_USD as the
  least-contaminated (quasi-out-of-sample) third pair** — it was *not* one of the
  two pairs the cost cells were read from — and leans on **year/session
  stability** as the persistence proxy. This limitation is acknowledged, not
  assumed away; it caps the strongest possible verdict.
- Every figure is read back from a committed CSV on disk (the C1 validation event
  panels already on `origin/main`, plus this screen's null CSVs).

## 3. Method (reuse only; invent nothing)

- **Event data:** reuse the committed per-pair C1 event panels
  `docs/research/c1_validation/{eur_usd,usd_jpy,gbp_usd}_c1_events.csv` (each row:
  a C1 rising-edge event with session/year, event-bar spread, H4-ATR volatility,
  signed extension, and 5/10/15/30/60-min forward `ret/mfe/mae`). The high-vol
  subset is a deterministic filter on these (Phase 1 defines it).
- **Nulls (Phase 4):** a small new runner `scripts/run_c1_highvol_frontgate.py`
  re-derives C1_long events on EUR_USD/USD_JPY/GBP_USD and computes, for the
  **high-vol subset**, the matched / random / vol-matched nulls via the locked
  `m1_response_matrix` samplers. No trade mechanics.
- **No positions, no stops, no targets, no PnL, no optimisation, no
  network/OANDA/credentials.** Cost is applied analytically to forward returns.

## 4. Phase map

| Phase | Doc | Question |
|---|---|---|
| 0 | `C1_HIGH_VOL_FRONTGATE_PLAN.md` (this) | audit + plan |
| 1 | `C1_HIGH_VOL_HYPOTHESIS.md` | **freeze** pairs, vol def, threshold, inclusion, and the PASS/FAIL/INCONCLUSIVE rule |
| 2 | (results committed) | event study on the high-vol subset (5/10/15/30/60) |
| 3 | `C1_HIGH_VOL_COST_STUDY.md` | does it survive realistic cost? |
| 4 | `C1_HIGH_VOL_NULL_COMPARISON.md` | still statistically distinct vs matched/random/unconditional? |
| 5 | `C1_HIGH_VOL_STABILITY.md` | concentrated or persistent (year/session/pair)? |
| 6 | `C1_HIGH_VOL_FRONTGATE_DECISION.md` | apply the frozen rule → one verdict |
| 7 | `NEXT_PROMPT_AFTER_C1_HIGH_VOL_FRONTGATE.md` | next-step prompt (only if PASS) |
| 8 | `C1_HIGH_VOL_FRONTGATE_SUMMARY.md` | validation gates + full report |

## 5. Hard rules (whole sprint)

No CAMPAIGN_032, no campaign, no strategy, no entry/exit rules, no
train/validation/test, no approval, no paper/demo/live, no OANDA, no credentials,
**no post-hoc parameter optimisation, pre-committed thresholds only**. A `PASS`
authorises (does not create) at most a future campaign *scaffold* — a separate,
later decision.

## 6. Files to review first

`C1_FACTOR_VERDICT.md` → `C1_COST_REALISM_STUDY.md` → this plan →
`C1_HIGH_VOL_HYPOTHESIS.md` (Phase 1).

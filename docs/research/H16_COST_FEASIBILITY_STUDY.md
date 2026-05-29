# H16 — cost-feasibility study (Phase 4)

**Sprint:** `research-non-time-bar-overshoot-frontgate-001` · Phase 4
**Artifacts:** [`cost_study.json`](../../research/h16_overshoot_frontgate/cost_study.json),
[`distribution_study.json`](../../research/h16_overshoot_frontgate/distribution_study.json).

> Cost model = C029's: round-trip ≈ mean spread + 2 × 0.2-pip slippage. Compares the
> *pre-cost* conditional fade move (Phase 3) to realistic round-trip cost. No PnL.

---

## 1. Cost vs the conditional move

| pair | round-trip cost (pips) | extreme-bucket mean fade by horizon (h1 / h2 / h3) | top-5% tail (h1 / h2 / h3) | exceeds cost anywhere? |
|---|---:|---|---|:--:|
| EUR_USD | 2.02 | +0.60 / +0.38 / +1.09 | −2.26 / +0.23 / +1.66 | **No** |
| GBP_USD | 2.65 | −0.20 / +2.02 / +2.34 | −0.98 / +3.41 / +4.33 | **No** |
| USD_JPY | 2.52 | −0.39 / +1.03 / −0.66 | +0.28 / +3.22 / −1.22 | **No** |

The script's `extreme_exceeds_cost_by_horizon` flag is **False for every pair at every
horizon**.

## 2. Answers to the Phase-4 questions

- **How large is the observed move?** The conditional fade move in the extreme bucket is
  ≈ −0.7 … +2.3 pips, **within ~1 SEM of zero** (Phase 3). The most positive values are
  at h2/h3 on GBP/JPY — longer holds that would also start to incur overnight financing.
- **How large is expected cost?** Round-trip ≈ **2.0–2.65 pips** at the *pair-average*
  spread. But large overshoots arrive with **wider** spreads (extreme-bucket spread
  2.7–2.8 pips on USD_JPY/GBP vs 1.5–2.0 small), so the **relevant** cost for the bars
  H16 would fade is **higher** than the average — the table above is therefore
  optimistic and still fails.
- **Does any conditional effect materially exceed cost?** **No.** No bucket/horizon mean
  exceeds even the average round-trip cost, let alone the elevated extreme-bucket cost.
  The one nominally-largest value (GBP top-5% h3 ≈ +4.33) is a single-pair, longest-
  horizon, small-sample tail that is *not* outside the null (Phase 5) and would face
  wider spread + incipient financing.
- **Is the effect strongest during expensive sessions?** The largest overshoots
  concentrate in **rollover_late** (the most expensive, fattest-spread window) and the
  London/NY overlap — so any nominal effect is **adversely** sited for cost.
- **Does the effect disappear after cost normalisation?** There is no pre-cost effect to
  begin with (Phase 3); after cost it is unambiguously **net-negative or null**.

## 3. Verdict contribution

H16 hits the **cost-defeated** falsifier (#3): the conditional move never exceeds
round-trip cost on any pair or horizon, and the cost is *worst* precisely on the
large-overshoot bars the thesis targets. This is the same structural failure mode as
C029 / C026 / C031 — cost dominates a non-existent or wafer-thin gross effect.

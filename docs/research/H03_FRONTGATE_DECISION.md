# H03 thin-move fade — front-gate decision (Phase 6)

**Sprint:** `research-non-time-bar-thin-move-frontgate-001` · Phase 6

---

## Verdict

# `FAIL_FRONT_GATE`

H03 (thin-move fade) **does not deserve a campaign scaffold.** The screen found a weak,
correctly-signed *average* tilt (low-participation bars fade slightly more positive than
high-participation bars on most cells) — more than H16 showed — but that tilt is
**non-monotone, coin-flip at the reversion-rate level, cost-feasible on only one pair,
inside the shuffled null on every pair, and confounded** by the fact that "thin" 30-pip
bars are really *fast, large-overshoot, wide-spread, off-hours* completions. It is most
parsimoniously the already-failed H16 overshoot effect plus bid-ask bounce, not an
independent participation edge.

> This is a **screen** verdict, not a campaign verdict. No campaign was created, nothing
> was approved, no lockbox was opened, no train/validation/test evidence was produced,
> paper/demo/live remain blocked, the research freeze is intact.

## Decision against the pre-registered falsifiers (hypothesis §5 / plan §7)

| falsifier | result | evidence |
|---|:--:|---|
| #1 No gradient (participation carries no monotone info) | ✅ met | non-monotone: medium ≥ low on EUR h1, USD_JPY h2/h3; GBP low−high +0.13→−0.51; peak reversion is often the *middle* bucket (Phase 3) |
| #2 Wrong sign (continuation) | ◑ partial | ultra-thin tail is **continuation** on EUR h1 (−1.48) and GBP h3 (−0.72); USD_JPY low h3 negative (−0.68) (Phase 3) |
| #3 Cost-defeated | ✅ met (2/3 pairs) | GBP & USD_JPY low buckets never beat their own (wider) cost; only EUR_USD clears, h2/h3 only, as fat-tailed drift (Phase 4) |
| #4 Null-indistinguishable | ✅ met | 0/18 cells beat the 95th-pct shuffled null; lone EUR low-h3 p_ge=0.0525 is multiple-comparison-expected + cost-confounded; no lift over unconditional (Phase 5) |
| #5 Single-pair artifact | ✅ met | every favourable read (cost survival, near-significant null) is **EUR_USD only**; GBP ≈ null, USD_JPY low-bucket fails cost & flips negative at h3 |

Reversion rate ≈ **0.50** on every pair/bucket/horizon (range 0.467–0.547) — directional
coin-flips, as with H16 and the rest of the repo's FX-direction history.

## Why this is `FAIL_FRONT_GATE` and not `INCONCLUSIVE`

`INCONCLUSIVE` was pre-defined (hypothesis §5) as a **weak-but-present, correctly-signed
effect that is cost-positive AND null-beating on ≥ 1 pair with suggestive evidence on a
second** — genuinely "needs more data". H03 fails that bar on the decisive leg:

- **Null-beating on zero pairs.** No cell crosses the 95th-percentile shuffled null. The
  one borderline cell (EUR_USD low h3, p_ge 0.0525) is *inside* the null, is
  multiple-comparison-expected over 18 cells, is the longest/most-drift-contaminated
  horizon, and is cost-confounded. A front gate must not hold open a candidate that does
  not beat its matched null anywhere.
- The cost-positive pair (EUR_USD) and the near-null pair are the **same single pair**,
  and the effect there is **fat-tailed drift** (mean grows with horizon while reversion
  rate stays 0.50), not a harvestable fade.
- The sample is **ample** (2,132–4,403 bars/pair), so this is not a power problem — it is
  a "flat, null-internal, confounded" result. More data of the same kind would not change
  the verdict; only a *new* thesis or *new* data would.

The honest classification of a correctly-signed tilt that is null-internal, cost-confined
to one pair, and confounded by a failed prior hypothesis is **FAIL**, not INCONCLUSIVE.

## Why this is not `PASS`

PASS (plan §6) required **all** of: a monotone participation gradient; the low/ultra-thin
move materially exceeding cost at a tradeable horizon; the effect outside the shuffled
null and above the unconditional baseline; on ≥ 2 of 3 pairs. **None** hold:
non-monotone, cost-cleared on one pair only, null-internal everywhere, no baseline lift.

## Scope / honesty notes

- Tested as pre-registered: **30-pip range bars**, **EUR_USD/GBP_USD/USD_JPY**, **C029
  train window**, **1–3-bar** horizons, **tick-count volume** participation with per-pair
  tertiles + a bottom-decile ultra-thin tail. No optimisation, no threshold sweep, no
  lockbox read.
- This does **not** claim participation is uninformative for *every* bar type / threshold
  / horizon / instrument in existence — only that the pre-registered, externally-motivated,
  cost-feasible formulation of H03 shows no campaign-worthy edge on this corpus. That is
  exactly what a front-gate screen is for.
- The single near-significant cell is treated as multiple-comparison noise (C028), not
  chased into a campaign.

## Consequences

- **H03 is abandoned.** It was the **last** pre-registered candidate on the non-time-bar
  thesis-discovery shortlist (H01 deferred, H05/H12 lower-ranked overlays, H16 already
  `FAIL_FRONT_GATE`).
- The non-time-bar lane's stop-criterion (discovery sprint: *"if both H16 and the H03
  fallback fail matched-null-post-cost on ≥ 2 pairs, directional/conditional non-time-bar
  search is exhausted on this corpus"*) is now **triggered.** The lane decision is made in
  [`NON_TIME_BAR_LANE_FINAL_DECISION.md`](NON_TIME_BAR_LANE_FINAL_DECISION.md) (Phase 7).
- Nothing is approved; the freeze is intact; the non-time-bar lane remains PAUSED for
  campaigns (and is recommended for retirement on this corpus — Phase 7).

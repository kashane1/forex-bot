# H16 overshoot-exhaustion fade — front-gate decision (Phase 6)

**Sprint:** `research-non-time-bar-overshoot-frontgate-001` · Phase 6

---

## Verdict

# `FAIL_FRONT_GATE`

H16 (overshoot-exhaustion fade) **does not deserve a campaign scaffold.** The screen
found no measurable exhaustion effect, no cost-survivable move, and nothing
distinguishable from a null. This is a clean, decisive fail.

> This is a screen verdict, not a campaign verdict. No campaign was created, nothing was
> approved, no lockbox was opened, paper/demo/live remain blocked.

## Decision against the pre-registered criteria

The FAIL criteria (plan §6 / hypothesis §6) were: *no effect; effect disappears after
cost; effect indistinguishable from null.* **All three are met — independently.**

| falsifier | result | evidence |
|---|:--:|---|
| #1 No gradient (overshoot has no conditional info) | ✅ met | mean fade does not rise with bucket; EUR small (+2.58) > extreme (+0.60); GBP/JPY extreme ≈ 0 or negative (Phase 3) |
| #2 Wrong sign (continuation, not reversion) | ✅ partial | top-5% tail leans to **continuation** at h1 on EUR (−2.26) and GBP (−0.98) (Phase 3) |
| #3 Cost-defeated | ✅ met | conditional move never exceeds round-trip cost (2.0–2.65 p) on any pair/horizon; cost is *worse* on large-overshoot bars (wider spreads) (Phase 4) |
| #4 Null-indistinguishable | ✅ met | extreme bucket *below* the unconditional baseline on all 3 pairs; 8/9 shuffle-null cells inside the null; the one borderline cell is cost-defeated single-pair noise (Phase 5) |

Reversion rate ≈ **0.50** on every pair/horizon (coin-flip), and every extreme-bucket
mean fade is **within ~1 SEM of zero**. The hypothesised exhaustion simply is not there.

## Why this is not `INCONCLUSIVE`

`INCONCLUSIVE` would require a weak-but-present signal needing more data. That is not the
case: the sample is ample (2,132–4,403 bars/pair), the measurement is clean, and the
result is not "small and uncertain" — it is **flat (no gradient), coin-flip
(rev ≈ 0.50), null-internal, and cost-negative** on all three pairs simultaneously. The
evidence positively supports "no effect", not "not enough evidence".

## Why this is not `PASS`

PASS required a measurable effect that survives cost, beats the null, and holds on ≥ 2
pairs. **None** of those hold. There is no effect to carry forward.

## Scope / honesty notes

- This screen tested H16 on **30-pip range bars**, **3 majors**, the **C029 train
  window**, at **1–3 bar** horizons, as pre-registered. It does **not** claim overshoot
  is uninformative for *every* bar type / threshold / horizon in existence — only that
  the pre-registered, externally-motivated, cost-feasible formulation of H16 shows no
  edge here. That is exactly what a front-gate screen is for.
- No optimisation was performed; the single near-significant cell (GBP h3) is treated as
  multiple-comparison noise, per the C028 lesson, not chased.

## Consequences

- **H16 is abandoned.** It is removed from the live shortlist (it remains documented).
- The lane's pre-registered **fallback was H03 (thin-move fade)**. Whether to spend one
  final screen on H03 or to close directional non-time-bar search is addressed in
  [`NEXT_PROMPT_AFTER_H16_FRONTGATE.md`](NEXT_PROMPT_AFTER_H16_FRONTGATE.md).
- Nothing is approved; the freeze is intact; the non-time-bar lane remains PAUSED for
  campaigns.

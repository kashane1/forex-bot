# C1 High-Volatility Cost Study (Phase 3)

**Status:** RESULT (descriptive; no verdict here, no positions, no trading)
**Date:** 2026-05-29
**Branch:** `research-c1-high-volatility-frontgate-001`
**Cost model:** the **frozen** Phase-1 model — `cost_rt = mean_spread_hivol +
slippage`, slippage 0.5 pip (primary) / 1.0 pip (stress); captured
`net = |mean_ret_60| − cost_rt`; economically meaningful iff `net ≥ +0.20` at
0.5-pip slippage. Figures read from the high-vol event panels.

## 1. Net-of-cost at the 60-min horizon (frozen model)

```
pair      mean_ret60   spread   |mean|/spread   net(slip 0.5)   net(slip 1.0)
EUR_USD     -1.777     1.633        1.09           -0.355          -0.855
USD_JPY     -2.094     1.827        1.15           -0.233          -0.733
GBP_USD     -1.258     2.114        0.60           -1.356          -1.856
```

## 2. Reading

- **The reversion barely clears the raw spread on the two primaries** (1.09× and
  1.15×) and **fails to clear it on GBP_USD** (0.60×).
- **After the pre-committed 0.5-pip slippage, net is negative on all three pairs**
  (−0.36 / −0.23 / −1.36). None reaches the +0.20-pip "economically meaningful"
  bar; both primaries are below break-even.
- **The 1.0-pip stress** pushes them further negative (−0.86 / −0.73 / −1.86).
- **Session structure does not rescue the pre-committed hypothesis.** The
  favourable pockets seen in validation were *session-conditioned* (EUR_USD London
  hi-vol, USD_JPY Tokyo hi-vol). The frozen hypothesis is **high-vol regime, all
  sessions** (no session filter, as specified), and across all sessions the
  unfavourable windows (EUR_USD Tokyo/offhours ≈ 0; USD_JPY London −0.79) drag the
  blended net below cost. Re-introducing a session filter now would be exactly the
  post-hoc optimisation the front gate forbids.
- **Execution realism makes it worse, not better.** Phase 2 showed mean adverse
  excursion exceeds favourable at every horizon (e.g. EUR_USD 60-min MAE 10.87 vs
  MFE 8.29) and `hit(neg) ≈ 0.53`. Capturing the mean would require an exit policy
  surviving a larger typical adverse swing than the edge itself — and high-vol
  spreads spike and gap beyond their mean, so the constant `mean_spread_hivol`
  charge is, if anything, optimistic.

## 3. Answer to the Phase-3 question

**Does the observed effect remain economically meaningful? No.** Under the frozen,
realistic cost model the volatility-conditioned C1 fade is **net-negative on all
three pairs at the primary slippage and worse under stress** — the cost wall that
defeated the unconditional factor still stands once the conditioning is applied
honestly across all sessions. This drives the Phase-1 **cost gate to FAIL on both
primaries** (carried to the Phase-6 decision).

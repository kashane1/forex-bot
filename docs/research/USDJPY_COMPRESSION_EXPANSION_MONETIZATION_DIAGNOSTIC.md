# USD_JPY Compression → Expansion — Monetization Diagnostic

**Sprint:** `usdjpy-volatility-compression-expansion-diagnostic-001` · **Phase 4**
**Tooling:** `scripts/analyze_usdjpy_compression_expansion_monetization.py`
**Output:** `research/usdjpy_vol_compression_expansion/monetization_diagnostic.json`

> **Counterfactual measurement, NOT a strategy, NOT edge, NOT a campaign.** All PnL is
> net of a **deliberately optimistic** 4.4-pip round-trip cost (2× the ~1.7-pip active
> spread + 1 pip slippage). Execution proxy: enter at the first prior-range break level
> in bars `i+1..i+h` after a compressed decision bar, exit at the close of bar `i+h`;
> whipsaw (both sides break) charges an extra round-trip. This proxy is **generous** (a
> real stop-entry slips; a real risk-managed trade can be stopped out intrabar before the
> horizon). Train+validation only; TEST sealed.

---

## Setup

- **Compressed state:** ≥3 of 4 percentile features {range, ATR, bandwidth, realized-vol}
  ≤ 0.20 (the predeclared primary cut).
- **Horizons:** 16 (4h) and 32 (8h) M15 bars — where Phase 3's follow-through signal was
  clearest.
- **Compressed decision bars:** 13,768; trade participation 0.94 (h16) / 0.99 (h32);
  whipsaw rate 0.27 (h16) / 0.43 (h32).

---

## Aggregate monetizations — all fail the both-splits cost bar

Mean pips/trade **net** of the optimistic cost:

| Monetization | h16 train | h16 val | h32 train | h32 val |
|---|---|---|---|---|
| **M2 continuation** (enter break dir) | **−4.87** | −1.52 | **−5.73** | −0.60 |
| **M3 fade** (enter opposite) | −6.40 | −9.58 | −7.02 | −11.75 |
| **M4 continuation, active sessions only** | −4.31 | +0.01 | −4.95 | +0.41 |

- **M1 straddle proxy** ≈ M2 (you hold the triggered side); a true both-legs straddle
  pays ≥2 costs and is strictly worse. Not separately profitable.
- **M2/M3/M4 all lose on train**, and are negative-to-breakeven on validation. None
  clears the precommitted cost bar on **both** splits. The fade (M3) is the worst.
- High whipsaw (0.27–0.43) is a major drag: low-vol prior ranges get pierced on both
  sides within the horizon, charging double costs.

**Verdict on the aggregate thesis: monetization is negative.** Consistent with Phase 3
(compression → *smaller* absolute range, direction null). A broad post-compression
breakout strategy does not survive even optimistic costs.

---

## One honestly-flagged lead: post-compression **London-session** continuation

Breaking M2 continuation down by session surfaces exactly one cell positive on **both
splits at both horizons**:

| session | h16 train | h16 val | h32 train | h32 val | h32 win-rate t/v |
|---|---|---|---|---|---|
| **london** | **+1.04** (n=815) | **+3.04** (n=692) | **+2.21** (n=846) | **+6.12** (n=712) | 0.554 / 0.542 |
| london_ny_overlap | −2.74 | +2.71 | −5.61 | +8.24 | (sign-flips) |
| ny | −6.38 | −1.84 | −5.29 | −1.94 | negative |
| tokyo | −4.64 | −0.16 | −6.94 | −1.68 | negative |
| off_hours | −6.36 | −3.59 | −7.49 | −1.24 | negative |
| rollover | −2.31 | −8.56 | −6.19 | −9.43 | negative |

- **London is the only session positive on all four train/val × horizon cells**, with
  win rates > 0.54 at h32. Every other session is negative or sign-flips across splits.
- **It has a plausible mechanism:** compression (often built during the quiet Tokyo
  session) resolving as European liquidity arrives at the London open — i.e. the
  "Tokyo-range → London expansion" idea (scorecard thesis #1/#B), now with a *direction*
  supplied by the actual break rather than predicted.

### Why this is a LEAD, not an edge (mandatory caveats)

1. **Post-hoc selection.** London was found by slicing 6 sessions × 2 horizons (12
   cells). One cell clearing on both splits is not strong evidence after multiple looks;
   it must be treated as a *hypothesis to precommit*, not a result.
2. **Optimistic costs + execution.** +1 to +6 pips/trade is thin and rests on a 4.4-pip
   cost, level-fill entry (no breakout-stop slippage), and a fixed-horizon exit with **no
   intrabar stop-out**. A realistic stop + slippage model could erase it.
3. **Small magnitude / sample.** n≈700–850/split; a handful of large London trends in
   2024–2025 (a strong USD_JPY uptrend period) could dominate the validation number.
4. **TEST untouched** — so there is no out-of-sample confirmation beyond validation.

---

## Disposition

The **broad** compression→expansion monetization **fails** the precommitted both-splits
cost bar (M2/M3/M4 all negative on train). The **only** survivor is a **post-hoc,
optimistic-cost London-session continuation cell** with a coherent mechanism. Per the
anti-overfit framework, that is a single lead that earns **at most one** precommitted,
overfit-hardened, realistic-cost confirmation — **not** a campaign, **not** C024, **not**
an approval. See `USDJPY_VOLATILITY_COMPRESSION_EXPANSION_READINESS_DECISION.md` (Phase 5).

**M5 no-trade filter:** 32.4% of compressed decision bars fall in cost-hostile sessions
(rollover/off_hours); excluding them is the already-adopted overlay and is reaffirmed.

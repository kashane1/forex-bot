# H03 thin-move fade — precise hypothesis (Phase 1)

**Sprint:** `research-non-time-bar-thin-move-frontgate-001` · Phase 1
**Type:** definition only. No code, no backtests, no PnL, no approval.

> This document pins down every term so the Phase 2–5 measurements have no degrees of
> freedom left to tune. Anything not fixed here is a forking path and is forbidden.

---

## 1. Informal statement

> A non-time-bar move that completes on **unusually low participation** (few ticks /
> low tick-count volume) is **less reliable** than a move that completes on normal or
> high participation, and is therefore **more likely to mean-revert** over the next few
> bars.

## 2. Formal definitions

### 2.1 Bars

- **Vehicle:** 30-pip **range bars** (`forex_bot.data.non_time_bars.build_range_bars`,
  `price_basis="mid"`), on the C029 train window, per pair. Only **completed** bars are
  used (`incomplete=False`); the trailing incomplete bar is dropped.
- Each completed bar `i` has: `close[i]` (mid close), `dir[i]` (+1 if
  `completion_reason="range_up"`, −1 if `"range_down"`), `overshoot_pips[i]`,
  `volume[i]` (sum of constituent M1 tick-count volume), `source_count[i]` (number of
  M1 minutes consumed — bar **duration**), a completion **session** bucket, and a
  **spread at completion** (pips, from the M1 bid/ask at `source_end_time`).

### 2.2 Thin participation

- **Participation** of bar `i` ≡ `volume[i]` (tick-count). Travel per bar is
  ≈ constant (`30 pip + overshoot`), so participation is the only varying quantity that
  distinguishes "how the move was produced".
- **Travel-per-unit-volume** ≡ `travel_pips[i] / volume[i]` where
  `travel_pips[i] = 30 + overshoot_pips[i]`. Reported for completeness; since travel is
  ~fixed, this is a monotone transform of `1/volume`, so we **bucket on volume**.
- **Low tick-count volume:** the bottom of the per-pair volume distribution (see 2.3).

### 2.3 Participation percentile & buckets (pre-declared, per pair, no tuning)

Compute the per-pair empirical distribution of `volume[i]` over all completed bars in
the window.

- **Tertile buckets** by volume:
  - `low` participation = volume ≤ 33.3rd percentile (the **thin** moves);
  - `medium` = 33.3rd–66.7th percentile;
  - `high` = volume > 66.7th percentile.
- **Ultra-thin tail** = volume ≤ **10th percentile** (an explicit, disjoint sharper
  test of "very thin"; the low-side mirror of H16's top-5% overshoot tail).

Tertiles (not quartiles) are chosen to keep each bucket's cell count ample given
~2,000–4,500 bars/pair; the decile tail is the sharp test.

### 2.4 Forward behaviour & the fade convention

For horizon `k ∈ {1, 2, 3}` completed bars:

```
fade_k(i) = −dir[i] × (close[i+k] − close[i]) / pip_size      # pips
```

- `fade_k(i) > 0` ⇒ price moved **against** the bar's completion direction ⇒
  **reversion** (the hypothesised behaviour for thin moves).
- `fade_k(i) < 0` ⇒ price continued in the completion direction ⇒ **continuation**.
- **Reversion rate** = fraction of bars in a bucket with `fade_k > 0`.

This is the **same** convention used by the H16 screen, so the two screens are directly
comparable.

## 3. Candidate buckets summary

| bucket | definition (per-pair, by `volume`) | role |
|---|---|---|
| `low` | ≤ P33.3 | the thin-move test cell (H03's claim) |
| `medium` | P33.3–P66.7 | gradient mid-point |
| `high` | > P66.7 | the "normal/high participation" contrast |
| `ultra_thin` (tail) | ≤ P10 | sharp thin-move test |
| `unconditional` | all bars | null baseline |

## 4. Expected behaviour if H03 is TRUE

1. **Gradient:** `reversion_rate(low) > reversion_rate(high)` and
   `mean_fade(low) > mean_fade(high)`, ideally monotone across low→medium→high.
2. **Sharpness:** the `ultra_thin` tail shows the strongest reversion.
3. **Magnitude:** `mean_fade(low)` and/or `mean_fade(ultra_thin)` is **positive and
   materially larger than round-trip cost** at some tradeable horizon.
4. **Robustness:** the effect holds on **≥ 2 of 3** pairs, is **outside the shuffled
   null**, exceeds the **unconditional** baseline, and is **not** confined to expensive
   sessions.

## 5. Falsification criteria (any ⇒ FAIL)

1. **No gradient** — `mean_fade(low) ≲ mean_fade(high)` (low participation carries no
   extra reversion), or the relationship is flat / non-monotone with low ≈ high.
2. **Wrong sign** — low-participation bars **continue** rather than revert
   (`mean_fade(low) < 0`).
3. **Cost-defeated** — the low / ultra-thin conditional fade never exceeds round-trip
   cost at any horizon (especially if thin bars carry *wider* spreads / fall in
   off-liquidity sessions, making them cost-toxic).
4. **Null-indistinguishable** — the low-participation (or ultra-thin) group mean sits
   **inside** the shuffled-participation null (≤ ~95th percentile) and/or does not beat
   the unconditional baseline.
5. **Single-pair artifact** — any apparent effect appears on only one pair, or only in
   one session.

`INCONCLUSIVE` is reserved for a **weak-but-present, correctly-signed** effect that is
cost-positive and null-beating on exactly one pair with suggestive (not decisive)
evidence on a second — i.e. genuinely "needs more data", not "flat and null".

## 6. Known confounds to measure (Phase 2) and how they bite

| confound | why it matters | check |
|---|---|---|
| **Overshoot vs volume** | if thin bars carry larger overshoot, the "effect" is really H16 (already failed), not participation | report `overshoot` stats by volume bucket |
| **Duration vs volume** | thin bars may simply be slow/quiet drift; duration may carry the info, not volume | report `source_count` (duration) by volume bucket |
| **Spread vs volume** | thin bars may coincide with **wide spreads** (off-hours) → cost-toxic, killing tradeability even if a raw effect exists | report spread by volume bucket (Phase 2 + 4) |
| **Session vs volume** | thin bars may cluster in Tokyo / rollover (thin + expensive) | report volume + bucket counts by session |
| **Bid-ask bounce** | mid-close reversion at h1 can be a microstructure artefact, not tradeable | rely on cost gate + h2/h3 persistence |

## 7. What a TRUE result would (and would not) authorise

A PASS authorises **only** a separate, later **scaffold** sprint to design a properly
pre-committed campaign — it does **not** create a campaign, approve anything, or open a
lockbox here. A FAIL abandons H03 and triggers the Phase-7 lane decision (with H16
already failed, H03 is the last shortlisted candidate).

# C1 High-Volatility Hypothesis — FROZEN PRE-COMMIT (Phase 1)

**Status:** FROZEN PRE-COMMIT — written and committed **before** any
volatility-conditioned number is computed. Nothing below may be changed after
results are viewed. No parameter is optimised. (Front-gate integrity.)
**Date:** 2026-05-29
**Branch:** `research-c1-high-volatility-frontgate-001`

---

## 1. Hypothesis (one sentence)

In a **high-volatility regime**, the `C1_trend_cont_long` reversion (price fades a
full H4+H1+M15 bullish alignment, drifting down over 30–60 min) is **large enough
to clear realistic execution cost and remain statistically distinct from a matched
null**, persistently, on liquid majors.

## 2. Scope (frozen)

- **State:** `C1_trend_cont_long` only — the locked prior definition (H4 `trend_up`
  & H1 `trend_up` & M15 `aligned_up`; EMA 20/50, slope-3; rising-edge + 60-min
  cooldown). Signed forward return; **negative = reversion = favourable to the
  fade.** (The `C1_short` mirror is reported descriptively but is **not** part of
  the gate.)
- **Pairs:**
  - **Primary (gate-bearing):** `EUR_USD`, `USD_JPY`.
  - **Generalisation / quasi-out-of-sample:** `GBP_USD` (was *not* one of the two
    pairs the validation cost cells were read from).
- **Evaluation horizon:** **60 min** primary; 30 min reported secondary.

## 3. Volatility measurement & threshold (frozen)

- **Measure:** the event-bar **H4 ATR(14), in pips** — i.e. the `volatility`
  column already recorded in each C1 event panel (`{pair}_c1_events.csv`).
- **High-volatility regime:** an event qualifies iff its event-bar H4 ATR is
  **≥ the pair-specific 66.667th percentile (top tertile) of H4 ATR computed
  across that pair's `C1_trend_cont_long` events.** (Identical to the validation
  sprint's `volatility.quantile(2/3)` cut — chosen there, frozen here.)
- **Rationale (pre-committed, not post-hoc):** validation Phase 2 showed — on the
  full sample, all 7 pairs, *before* any cost analysis — that the C1 reversion
  grows monotonically with H4-ATR volatility (high-tertile t −3.78). The top
  tertile is the pre-existing, mechanism-motivated cut, not a scanned optimum.

## 4. Inclusion criteria (frozen)

An event enters the screen iff **all**:
1. it is a `C1_trend_cont_long` rising-edge event (60-min cooldown) on a screen
   pair;
2. event-bar H4 ATR ≥ the pair's top-tertile threshold (§3);
3. the evaluated-horizon forward return is non-NaN (no weekend/data-gap drop).

No other filter (no session filter, no extension filter, no time filter) — the
hypothesis is **high-volatility regime only**, as specified.

## 5. Cost model (frozen)

Per pair, **round-trip cost** in pips:

```
cost_rt(pair) = mean_spread_hivol(pair)  +  slippage
```

- `mean_spread_hivol` = mean event-bar spread (ask−bid, pips) of that pair's
  **qualifying high-vol events** (so high-vol spread widening is already included;
  one full spread funds a half-spread entry + half-spread exit).
- `slippage` = **0.5 pip** round-trip (primary). A **stress** value of **1.0 pip**
  is also pre-committed for robustness.

**Captured net reversion** at 60 min:
```
net(pair) = |mean_ret_60(hivol, pair)|  −  cost_rt(pair)
```
The fade is **economically meaningful** on a pair iff `net(pair) ≥ +0.20 pip`
under the primary slippage (0.5).

## 6. Nulls (frozen — Phase 4)

For the high-vol subset, over **200 seeds** each, compare the observed high-vol
mean 60-min return to:
1. **Matched null** — random M1 bars, same session + direction (locked sampler).
2. **Randomised-timestamp null** — random M1 bars, fixed direction.
3. **Unconditional baseline** — the all-events (un-filtered) C1_long mean for the
   same pair (does high-vol conditioning *add value*?).
4. **Volatility-matched null** — random bars drawn **only from high-volatility
   M1 bars** (H4 ATR ≥ the pair's high-vol threshold), same session + direction.
   This is the strict test that the effect is **C1-specific**, not merely "any
   high-vol bar mean-reverts."

`matched_z = (observed − null_mean)/null_std`.

## 7. PASS / FAIL / INCONCLUSIVE — pre-committed decision rule

Let "both primaries" mean EUR_USD **and** USD_JPY.

**`PASS_FRONT_GATE`** requires **all** of:
- **Cost:** `net(pair) ≥ +0.20 pip` (primary slippage) on **both primaries**.
- **Null:** matched-Z ≤ **−2.0** at 60 min on both primaries, **and**
  **volatility-matched-Z ≤ −2.0** on both primaries (effect survives the strict
  C1-specific null).
- **Adds value:** `|mean_ret_60(hivol)| > |mean_ret_60(unconditional)|` on both
  primaries (conditioning helps).
- **Stability:** on each primary, signed 60-min return is negative in **≥4 of 6**
  calendar years **and** in **≥3 of 4** sessions, and **no single year** supplies
  **>60%** of the summed favourable reversion.
- **Generalisation:** GBP_USD shows the **same (negative) sign** at 60 min **and**
  `net(GBP_USD) ≥ 0` (at least break-even at primary slippage).

**`FAIL_FRONT_GATE`** if **any** of:
- `net < 0` after cost on **either** primary (cost wall remains); **or**
- matched-Z **> −2.0** on either primary (null advantage gone); **or**
- volatility-matched-Z **> −2.0** on either primary (effect is generic high-vol
  reversion, not C1-specific); **or**
- gross instability (negative sign in **<3** years **or** **<2** sessions on a
  primary); **or**
- GBP_USD sign **flips positive** at 60 min.

**`INCONCLUSIVE`** otherwise — e.g. the primaries clear cost + matched null but the
**vol-matched** null is marginal, or stability is borderline, or the **1.0-pip
slippage stress** flips a primary net negative, or GBP_USD is cost-defeated though
correctly signed. (Effect plausibly real but the evidence is not strong enough to
justify a scaffold.)

## 8. What each verdict authorises

- `PASS` → recommend (do **not** create) **one** future campaign *scaffold* sprint.
- `INCONCLUSIVE` → no scaffold; document; the candidate rests.
- `FAIL` → the M1/HTF time-bar confluence directional lane is **closed** on this
  corpus (joins the retired non-time-bar lane); reopen only with new data
  (10–15y / genuine non-USD crosses) or a new external thesis, via a fresh screen,
  never a re-tune.

No campaign, no strategy, no approval, no paper/demo/live is created by **any**
of these outcomes.

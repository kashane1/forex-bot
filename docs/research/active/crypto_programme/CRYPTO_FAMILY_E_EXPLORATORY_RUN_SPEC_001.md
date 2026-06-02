# Crypto Family E — Exploratory Run Spec 001 (PRE-REGISTRATION)

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Date:** 2026-06-02
**Status:** **FROZEN — written before any diagnostic is executed.** This document pre-registers every threshold, horizon, quantile, null, cost variant, regime definition, and classification gate. No parameter below may be changed after results are read. Forking-path drift is prevented by this freeze.

This spec implements the pre-registered hypotheses in `CRYPTO_FAMILY_E_DIAGNOSTIC_DESIGN.md`. No new hypotheses are invented here.

---

## 0. Shared data rules

- **Instruments:** `BTC_PERP_USD`, `ETH_PERP_USD` only. No altcoins, no third perp.
- **Venue basis:** Deribit USD inverse perps (canonical for this run). USD-quoted throughout — no USDT confound.
- **Timezone:** UTC only; interval-end timestamps.
- **Funding cadence:** Deribit funding is hourly-realized (`funding_interval_hours = 1`).
- **Funding resampling (8h windows):** an 8h funding value = **sum** of the 8 hourly `funding_rate` (realized interest) over the window `[t, t+8h)`, aligned to settlement boundaries 00:00 / 08:00 / 16:00 UTC. No lookahead across windows.
- **Return basis:**
  - funding diagnostics (1, 2, 6-funding): perp H1 **close-to-close log returns** over the stated forward horizon.
  - basis diagnostics (3, 6-basis): forward perp H1 log return at the basis horizon (convergence is tested as perp reverting; expansion as momentum).
- **Missing data policy:**
  - no interpolation of funding/index/OHLCV gaps;
  - **skip** any signal window or forward-return window that crosses a missing funding / index / OHLCV bar;
  - **count and report** skipped windows per diagnostic/instrument.
- **Eligible sample:** per-instrument set of signal timestamps with complete signal inputs **and** a complete forward-return window at every tested horizon for that diagnostic. Deciles/terciles are computed on the eligible sample only (no lookahead — the decile cut uses the full in-sample distribution, an exploratory non-walk-forward convention stated here and not changed later).

---

## 1. Diagnostic 1 — Funding mean reversion

- **Signal:** 8h-summed funding rate `F_8h` per instrument.
- **Extreme positive:** top decile of `F_8h` (eligible sample). **Extreme negative:** bottom decile.
- **Direction tested:**
  - high positive funding → predicts **negative** forward return (long-crowding unwind) → trade **short**;
  - high negative funding → predicts **positive** forward return → trade **long**.
- **Horizons:** 8h, 24h, 72h (forward, from the funding-window end).
- **Effect statistic:** mean forward return of the decile cohort, and the signed "edge" = (mean conditional return in the predicted direction). Net edge subtracts round-trip cost + realized funding over the hold.
- **Splits:** BTC-only, ETH-only, pooled.
- **Nulls:** shuffled funding→forward-return mapping; matched-random entry at same timestamps; randomized sign.
- **Classification inputs:** decile-cohort net edge vs null band, all-in & 2× stress sign, BTC/ETH agreement.

## 2. Diagnostic 2 — Funding trend continuation

- **Signal:** same-sign persistence of `F_8h` over the last `k` settlements, `k ∈ {3, 6, 9}`.
- **Direction tested:**
  - persistent **positive** funding → test **long continuation** AND the **short-after-cost** alternative;
  - persistent **negative** funding → test **short continuation** AND the **long-after-cost** alternative.
- **Horizons:** 24h, 72h.
- **Monotonicity:** report whether the effect strengthens monotonically across `k = 3 → 6 → 9` (a non-monotone gradient is a fail signal).
- **Splits / nulls:** BTC/ETH/pooled; randomized run-length / shuffled sign sequence; matched-random.
- **Note:** directly competes with Diagnostic 1 — at most one direction (reversion vs continuation) can hold.

## 3. Diagnostic 3 — Basis compression / expansion

- **Signal:** `basis_bps` series (`basis_h1.csv`, perp_close − index_close in bps).
- **Extremes:** top decile / bottom decile of `basis_bps`.
- **Horizons:** 4h, 24h (forward perp log return).
- **Both directions tested:**
  - **convergence/reversion:** stretched basis → perp reverts toward index (high basis → short perp; low/negative basis → long perp);
  - **expansion/momentum:** stretched basis → continues.
- **Splits / nulls:** BTC/ETH/pooled; shuffled basis→return; matched-random; **wrong-pairing null** (BTC basis vs ETH return, ETH basis vs BTC return).
- **Cost note:** basis trades treated as a single perp leg here (perp-vs-index is informational; the executable leg is the perp). Two-leg perp-vs-spot cost is flagged in the doc but the perp-only cost is the conservative reported hurdle.

## 6. Diagnostic 6 — Cross-asset confirmation (BTC ↔ ETH)

- **Agreement (funding):** BTC and ETH `F_8h` **same sign** and both beyond a magnitude threshold = both in their respective top decile (positive agreement) or both bottom decile (negative agreement).
- **Agreement (basis):** BTC and ETH `basis_bps` same sign and both beyond top/bottom decile.
- **Disagreement:** one asset extreme (top/bottom decile) while the other is **neutral** (inner 8 deciles) or **opposite-sign extreme**.
- **Tests:**
  - **directional agreement effect:** does dual-asset agreement strengthen the directional forward move (apply diag-1 reversion direction)?
  - **relative-value disagreement effect:** does disagreement predict relative-value reversion of the extreme asset toward the other?
- **Horizons:** 8h, 24h.
- **Cost:** **paired** — conservative. Directional-agreement on a single traded asset uses single-leg cost; relative-value disagreement uses the **paired two-asset** cost (recall Family B paired hurdle was large). Funding included on each held leg.
- **Nulls:** shuffled cross-asset pairing; randomized agreement flag; matched-random.

## 7. Diagnostic 7 — Regime conditioning (applied to 1–3 only, AFTER base diagnostics)

Regimes are **frozen here, before base results are read.** Only these four regimes are used:

| Regime | Definition |
|--------|------------|
| Volatility tercile | tercile of prior-24h realized volatility (std of prior 24 H1 log returns) |
| Trend regime | sign & magnitude of prior-7d (168h) perp log return; terciles by signed magnitude → {down, flat, up} |
| Absolute funding tercile | tercile of \|`F_8h`\| |
| Basis tercile | tercile of `basis_bps` |

- Apply each regime as a conditioning slice on Diagnostics 1, 2, 3.
- For every regime cell: sample count, gross / spread-only / all-in / 2× stress, null comparison, BTC/ETH/pooled.
- **Highest forking-path risk** — Holm adjustment across all regime cells; a tiny regime slice must not override a base-diagnostic failure.

---

## Multiple-comparisons discipline

- **Holm** step-down adjustment (or documented equivalent) applied across the full family of tests: diagnostics × horizons × assets × regimes.
- Raw p-values **and** Holm-adjusted decisions reported.
- Classification uses the **adjusted / forking-path-aware** interpretation, never the best raw cell.

---

## Null baselines (all diagnostics)

| Null | Definition |
|------|------------|
| matched-random | random entries at the same timestamps/frequency as the signal cohort |
| shuffled-timestamp | permute the signal→forward-return mapping |
| randomized sign/rank | randomize the signal's sign (or rank) before conditioning |
| wrong-pairing | (basis & cross-asset only) BTC signal vs ETH return and vice-versa |

- **Deterministic seeds**, recorded in every artifact. Base seed = `20260602`; per-null seeds derived deterministically (`base + offset`). Default `n_draws = 1000` per null (recorded in manifest).

---

## Cost variants (frozen — `CRYPTO_DERIVATIVES_COST_MODEL_001.md`)

| Variant | Definition |
|---------|------------|
| Gross | mid/mark returns, no costs, no funding |
| Spread-only | deduct `2 × half_spread_bps` (BTC 4 bps RT, ETH 6 bps RT) |
| All-in | `2×half_spread + 2×slippage + taker_rt` **+ realized funding** (BTC 16 bps, ETH 18 bps RT at H1/8h, + funding) |
| 2× stress | double spread, slippage, fee (BTC 32 bps, ETH 36 bps RT); funding **as observed** (not halved) |

**Funding cashflow:** when `funding_rate > 0`, longs pay shorts. Long funding PnL over a hold = `−Σ(interest_1h) × notional`; short = `+Σ(interest_1h) × notional`. Any hold across funding intervals includes this in all-in & 2× variants. **Cost assumptions are not changed after seeing results.**

---

## Classification gates (pre-committed)

Labels: `rejected` · `statistical_only_cost_defeated` · `cost_defeated` · `candidate_for_front_gate` · `blocked_data_quality` · `blocked_low_power_oi`.

**`candidate_for_front_gate` requires ALL of:**
1. effect clears matched-null band after multiple-comparisons (Holm) adjustment;
2. all-in net positive;
3. 2× stress net positive;
4. BTC-only and ETH-only **both** directionally supportive;
5. pooled result supportive;
6. enough observations in the cell;
7. not dependent on one small regime slice;
8. not OI-depth-limited.

**Decision tree otherwise:**
- no effect / within null → `rejected`;
- real vs null (gross), but **not** net-positive all-in → if sub-cost-band reversion/effect: `statistical_only_cost_defeated`; if costs simply exceed a real gross edge: `cost_defeated`;
- missing/corrupt required data → `blocked_data_quality`;
- OI diagnostics (4, 5) → default `blocked_low_power_oi` or `exploratory_low_power_only` unless §candidate gates pass AND the shallow-OI concern is explicitly resolved.

**Even a `candidate_for_front_gate` stops here** — no campaign, strategy, front gate, or approval is created from exploratory results.

---

## No-strategy / no-campaign / no-front-gate / no-approval statement

This is a pre-registration document. It creates no strategy, campaign, front gate, or approval and runs no diagnostic. BTC and ETH only. `approved: []`. Paper/demo/live remain blocked.

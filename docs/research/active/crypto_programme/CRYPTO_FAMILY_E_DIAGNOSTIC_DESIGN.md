# Crypto Family E — Exploratory Diagnostic Design (Design Only, Phase 6)

**Sprint:** `crypto-family-e-derivatives-data-prep-001` · Phase 6
**Date:** 2026-06-02
**Type:** DESIGN ONLY — no diagnostic executed, no factor run, no edge claimed.
**Universe:** BTC and ETH perpetuals/derivatives only.

This pre-registers candidate Family E exploratory diagnostics for a **future** sprint. None are run here. Each is exploratory — a statistically-real effect is **not** a tradable edge (the S4 / Family B / Family C lesson). Every diagnostic must report BTC-only, ETH-only, and pooled, against matched nulls, with conservative costs and funding cashflows.

---

## Shared protocol (applies to every diagnostic below)

- **Splits:** BTC-only, ETH-only, and pooled — report all three; flag single-asset artifacts.
- **Null baselines (mandatory):** matched random entries, shuffled-timestamp signal, randomized sign/rank. Effect must clear the null band, not just be non-zero.
- **Cost & funding treatment:** report gross, spread-only net, all-in net, and 2× stress. Perp cost placeholders (taker fee, perp half-spread, slippage) are pre-registered in a derivatives cost-model freeze **before** any run (separate from the spot `CRYPTO_COST_MODEL_001.md`). Funding cashflows use the frozen sign convention: **long pays short when funding_rate > 0** (`funding_cashflow` helper).
- **Quote-currency hygiene:** USDT-quoted perps (OKX/Binance/Bybit linear) are flagged; basis/return comparisons against USD spot must adjust for USDT or use a USD-quoted reference (Kraken `PF_*` / Deribit).
- **Timeframe alignment:** funding is 8h; align signals to funding settlement boundaries or to the diagnostic's stated bar TF; never look ahead across a settlement.
- **Failure classification (pre-committed):** `rejected` (no effect / within null) · `statistical_only_cost_defeated` (real but sub-cost-band) · `cost_defeated` · `candidate_for_front_gate` (real **and** net-positive after 2× stress, robust across BTC & ETH). Default expectation given C & B history: rejected or statistical-only.

---

## Diagnostic 1 — Funding mean reversion

- **Required data:** funding rates (8h), perp OHLCV (forward returns).
- **Hypothesis:** extreme positive (negative) funding predicts subsequent **negative (positive)** perp/spot returns as crowded carry unwinds.
- **Null baseline:** shuffle the funding→forward-return mapping; matched-random entry at same times.
- **Cost/funding:** holding across ≥1 settlement incurs funding cashflow with the frozen sign; all-in + 2× stress.
- **Timeframe:** entry at funding settlement; forward horizons 8h / 24h / 72h.
- **BTC/ETH split:** required.
- **Failure criteria:** reverts within null band, or net-negative after costs, or BTC-only.
- **Why not a strategy:** one exploratory reversion statistic; no sizing, no execution, no walk-forward.

## Diagnostic 2 — Funding trend continuation

- **Required data:** funding rates, perp OHLCV.
- **Hypothesis:** persistent same-sign funding over k settlements aligns with directional **continuation** (carry regime, not exhaustion).
- **Null baseline:** randomized run-length; shuffled funding sign sequence.
- **Cost/funding:** continuation trades pay funding while held — sign convention central; all-in + 2×.
- **Timeframe:** persistence window k ∈ {3, 6, 9} settlements; forward 24h / 72h.
- **BTC/ETH split:** required.
- **Failure criteria:** no monotone gradient in k; within null; cost-defeated. (Note: directly competes with Diagnostic 1 — at most one direction can hold.)
- **Why not a strategy:** exploratory sign test; no portfolio construction.

## Diagnostic 3 — Basis compression / expansion

- **Required data:** perp mark/close + spot index (USD-quoted reference), to compute `basis_bps`.
- **Hypothesis:** stretched spot-perp basis predicts short-horizon convergence (perp reverts toward spot) or momentum.
- **Null baseline:** shuffled basis→return mapping; matched-random entries; **wrong-pairing** null (BTC basis vs ETH return).
- **Cost/funding:** basis trades are perp-vs-spot; two-leg cost + funding; all-in + 2×.
- **Timeframe:** 1h / 4h basis; forward 4h / 24h.
- **BTC/ETH split:** required.
- **Failure criteria:** convergence inside cost band (the S4 no-arb-band trap), within null, or USDT-confounded.
- **Why not a strategy:** requires a clean USD-quoted basis series not yet backfilled; exploratory only.

## Diagnostic 4 — Open-interest impulse

- **Required data:** open interest (history), perp OHLCV.
- **Hypothesis:** OI expansion + price trend → continuation (new money) **or** exhaustion (crowding); OI contraction + price move → reversal.
- **Null baseline:** shuffled OI-change series; matched-random entries.
- **Cost/funding:** all-in + 2×.
- **Timeframe:** OI change over 8h / 24h; forward 24h / 72h.
- **BTC/ETH split:** required.
- **Data caveat:** **deep free OI history is the binding gap** (source review §3). This diagnostic may be limited to forward-collected OI; document coverage and treat as low-power until depth exists.
- **Failure criteria:** no sign structure, within null, or insufficient OI history to power the test.
- **Why not a strategy:** exploratory; data-limited.

## Diagnostic 5 — Funding / OI interaction (crowding)

- **Required data:** funding rates, open interest, perp OHLCV.
- **Hypothesis:** high positive funding **and** rising OI (crowded longs) precedes negative returns (squeeze); symmetric for crowded shorts.
- **Null baseline:** independently shuffled funding and OI; randomized joint condition.
- **Cost/funding:** all-in + 2×; funding sign convention.
- **Timeframe:** condition over 8h–24h; forward 24h / 72h.
- **BTC/ETH split:** required.
- **Failure criteria:** interaction adds nothing over Diagnostic 1/4 alone; within null; cost-defeated; OI-depth-limited.
- **Why not a strategy:** exploratory conditional study; no execution.

## Diagnostic 6 — Cross-asset confirmation (BTC ↔ ETH)

- **Required data:** funding (and/or basis, OI) for both BTC and ETH.
- **Hypothesis:** BTC/ETH funding (or basis) **agreement** strengthens a signal; **disagreement** predicts relative-value reversion (Family-B-adjacent, derivatives version).
- **Null baseline:** shuffled cross-asset pairing; randomized agreement flag.
- **Cost/funding:** paired two-asset cost (recall Family B paired hurdle was ~260 bps); all-in + 2×.
- **Timeframe:** 8h / 24h.
- **Failure criteria:** paired cost defeats it (expected, per Family B), within null.
- **Why not a strategy:** exploratory; explicitly inherits Family B's cost-band caution.

## Diagnostic 7 — Regime conditioning

- **Required data:** any of the above + a regime variable.
- **Hypothesis:** Family E effects concentrate in specific regimes: volatility terciles, trend vs range, high vs low absolute funding.
- **Null baseline:** regime-shuffled labels; ensure regime isn't just proxying time.
- **Cost/funding:** all-in + 2× within each regime cell.
- **Timeframe:** inherits the conditioned diagnostic's TF.
- **Failure criteria:** apparent effect is a multiple-comparisons artifact across regime cells (apply Holm/forking-path discipline); within null; cost-defeated.
- **Why not a strategy:** conditioning is exploratory slicing, highest forking-path risk — pre-register regime definitions before running.

---

## Data readiness gate (must pass before Family E diagnostics run)

| Requirement | Status after this prep sprint |
|-------------|------------------------------|
| Funding rates (BTC+ETH) | Pilot proven (OKX); full backfill **not yet** run |
| Perp OHLCV | Adapter designed; OKX OHLCV endpoint **not yet** wired/backfilled |
| Mark/index (USD reference) | Designed; **not yet** fetched |
| Open interest history | **Binding gap** — only snapshots free here; forward-collection likely |
| USD-quoted basis series | **Not yet** — needs USD reference venue (Kraken `PF_*`/Deribit) |
| Derivatives cost-model freeze | **Not yet** — must be written + frozen before diagnostics |

Diagnostics 1–2 (funding only) are closest to runnable; 3–7 need more backfill. **No diagnostic runs until the readiness gate and a frozen derivatives cost model exist.**

## No-strategy / no-campaign / no-approval statement

This is a design document. It creates no strategy, campaign, front gate, or approval, and runs no diagnostic. BTC and ETH only. Paper/demo/live remain blocked.

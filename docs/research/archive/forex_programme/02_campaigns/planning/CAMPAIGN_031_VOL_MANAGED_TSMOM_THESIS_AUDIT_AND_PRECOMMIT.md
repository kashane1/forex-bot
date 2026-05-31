# CAMPAIGN_031 — Volatility-Managed Time-Series Momentum: Thesis Audit & Front-Gate Precommit

**Sprint:** `campaign-031-vol-managed-tsmom-front-gate-screen-001`
**Status:** `PRECOMMIT` / `FRONT_GATE_NOT_YET_RUN` / `NOT_RUN_AS_CAMPAIGN` / `NOT_APPROVED`
**Date:** 2026-05-29
**Thesis source:** user-supplied "Thesis & Founders Pack — Volatility-Managed Time-Series Momentum on OANDA Spot FX" (spec-grade).
**Freeze:** intact. This document is written **before** any screen run. It pre-states the
frozen house config and the decision rule the screen will be judged against. It changes no
campaign status, opens no lockbox, and approves nothing. `configs/approved_strategies.yaml`
stays empty.

> Reserved number: **031** (030 left free per the user's instruction; grep confirms neither 030
> nor 031 was previously used — see `CAMPAIGN_NUMBERING_CONVENTION.md`). The front-gate screen
> carries the campaign number the way C028 did; earning the number as a *campaign* is contingent
> on passing this gate.

---

## 1. Thesis in one paragraph

Liquid FX majors are claimed to exhibit **time-series momentum** (the sign/scaled-magnitude of an
instrument's own trailing 1–12-month return predicts its next-period return), strongest when
positions are **scaled by volatility**. The pack's real contribution is not the TSMOM claim — it is
the **combination-space analysis (§3)**: volatility enters the pipeline at up to five distinct points
(A signal transform · B per-instrument 1/σ sizing · C portfolio gross vol-target · D Moreira-Muir
conditional timing · E vol estimator/window), and several "obvious" combinations apply 1/σ twice
(the **1/σ² double-counting trap**). The program is to test whether a vol-managed TSMOM book beats
honest baselines net of OANDA spread + asymmetric financing, and to map *where* volatility belongs.
**H0 = net-of-cost OOS Sharpe ≤ 0, indistinguishable from random-entry of matched turnover.**

## 2. Audit verdict

**Strengths.** Self-deflating (treats published Sharpes as upper bounds; names post-publication
decay; H0 = zero edge). The §3 decomposition and the 1/σ² trap are correct and are exactly the
silent researcher-degree-of-freedom this platform exists to catch. Correctly identifies **financing
as first-order** for a multi-month directional book.

**Weaknesses / honest priors.** (a) The edge itself is the one thing the pack cannot establish a
priori; given this platform's record (C022/C026/C027/C029 all REJECTED, mostly *cost-defeated*) the
prior is heavily negative. (b) Financing over multi-month holds is the highest-probability kill path —
the pack half-knows this. (c) Five unverified citations / regulatory items (§13) — do not block a
backtest. (d) The 864-cell grid is a loaded gun; the "judge the house config first" discipline must
be **machine-enforced**, not promised. (e) The strategy is **Sharpe/portfolio-based**, not
R-multiple/single-pair — the existing gate vocabulary does not map onto it (foundation gap, §3).

**Verdict:** scientifically sound *as a specification*, deserves a cheap hard falsification, does
**not** deserve a presumption of edge.

## 3. Foundation gap inventory (thesis need vs. platform)

| Thesis need | Status | Note |
| --- | --- | --- |
| OANDA v20 daily, BMA, 17:00 NY align | EXISTS | `broker/oanda.py`, `domain/candles.py` defaults `daily_alignment=17`, `America/New_York` |
| Valid daily bars | PARTIAL | Native `D` invalid (C006 rollover blackout). Use `D1AGG` (H4-derived, `backtesting/d1_aggregation.py`) |
| Half-spread bid/ask cost | EXISTS | `backtesting/fills.py`; lab `edge_discovery/costs.py` |
| **Financing / swap model** | **GAP** | Only a conservative bp/day **stress overlay** (`financing.py`, ESTIMATED). No real per-pair long/short rates, no admin-fee asymmetry, no weekend 3×, no in-engine 17:00 charge |
| **Multi-instrument portfolio engine** | **MISSING** | Engine is single-instrument/single-position. No covariance, portfolio vol-target, net-USD cap, or Moreira-Muir overlay. Largest gap |
| Edge-discovery front gate | EXISTS | `research/edge_discovery/` — matched-null, filter-ablation, multiple-comparison, cost-feasibility. **Mandated** before any scaffold |
| **Deflated Sharpe (Bailey-LdP)** | PARTIAL | best-of-N noise exists; DSR formula (haircut, N_eff, skew/kurtosis) does not |
| **PBO / CSCV** | MISSING | thesis §10 requires it |
| **Purged / embargoed CV** | MISSING | overlapping 63/126/252-day lookbacks need it |
| Daily depth (10+ pairs, 10–15y) | **PARTIAL — decisive, see §4** | |
| Portfolio-Sharpe gate set | MISSING | all gates are R-multiple/expectancy/PF |

## 4. Data-availability finding (decisive)

Postgres `market_data.candles` holds **7 instruments, all USD-legged majors**
(AUD_USD, EUR_USD, GBP_USD, NZD_USD, USD_CAD, USD_CHF, USD_JPY). Deepest series is **H4,
2020-01-01 → 2026-05** (~6.4 yr). **No crosses** (no EUR_JPY, EUR_GBP, AUD_JPY). D1AGG daily is
built from H4.

This collides with two load-bearing premises of the thesis:

1. **Breadth is gone.** 7 USD-legged pairs are — by the pack's own Key insight #3 — *secretly one
   leveraged USD bet*. Correlation-aware scaling (C) and the net-USD cap cannot diversify the common
   factor away when there is nothing to diversify into.
2. **History is too short for a slow signal.** A 252-day lookback eats ~1 yr of warmup; a train-only
   window (2020–2022, matching C028 / the lockbox discipline) leaves ~2 yr of daily signal. A
   1–12-month-horizon edge over ~6 calendar years is **~6 independent annual cycles** — too few for a
   credible deflated-Sharpe claim *before costs*.

**Consequence:** the modal screen outcome is `COST/FINANCING_DEFEATED`, `INSUFFICIENT_POWER`, or a
fragile positive that will not survive DSR penalization. A robust positive on *this* data is
unlikely. The screen is still run because it is cheap and the rejection is itself the deliverable.

## 5. FROZEN house config (the exact strategy the screen runs)

Decided **before** any run. No tuning; if it fails, it fails.

- **Universe (E0):** the 7 USD majors above. D1AGG daily mid close, lookahead-free, NY-day aligned.
- **Signal (A):** raw **sign-blend** `S_i = sign( Σ_k sign(M_i^{(k)}) )` over `k ∈ {63,126,252}`
  trading days, `M^{(k)} = ln(P_t/P_{t-k})`. **No** signal-level vol normalization (avoids the 1/σ²
  trap; the first 1/σ lives in sizing).
- **Per-instrument sizing (B):** `w_i ∝ S_i / σ_i`, `σ_i` = EWMA vol, center-of-mass ≈ 60 trading
  days (δ ≈ 0.984), annualized ×√252.
- **Portfolio scaling (C):** scale `w` to **10% annualized** portfolio vol. Two variants reported:
  (i) **naive** `diag(σ²)`, (ii) **full-Σ** using estimated correlation. (With 7 USD-legged pairs
  the two will be close and *both* remain a USD bet — this is reported, not hidden.)
- **Timing overlay (D):** Moreira-Muir `m_t = clamp(σ_target_MM / σ̂_strat,t, 0.25, 1.5)` on the
  book's own trailing 20-day P&L vol. **Tested on AND off** — D must earn its place.
- **Vol estimator (E):** EWMA com≈60d primary (above).
- **Rebalance:** daily at the D1AGG close. **No-trade band:** only adjust a position when the target
  differs from current by > 15% of the position. Turnover priced via the half-spread model.
- **Account:** USD, $25k notional reference, 10% vol target.

## 6. FROZEN screen methodology

Train window **2020-01-01 → 2022-12-31 only**. Validation (2023–2024) and test/lockbox (2025-01 →
2026-05) are **never touched** by this screen. Import-isolated lab code only (no `forex_bot`
strategy/broker/approval imports; data hydrated H4 → D1AGG inside the lab).

Pipeline: build per-pair D1AGG mid series → compute the §5 book daily return series (pre-cost) →
apply **half-spread turnover cost** (lab `costs.cost_fraction`, 1.5 pip spread + 0.2 pip slip) on
rebalancing notional changes → apply **conservative financing stress** (lab
`costs.financing_stress_fraction`, worst-of-long/short bp/day, charged per day held, **per leg**) →
**2× cost+financing stress** variant → metrics.

Gates (lab primitives, descriptive — no significance claims):
1. **Cost/financing feasibility** — does the net book survive real spread + financing, and 2× stress?
2. **Net Sharpe** (annualized) of the house book, pre/post cost, ±D, naive-C vs full-Σ-C.
3. **Random-entry matched-turnover null** (lab `null` / `matched_nulls`) — book must beat the null's
   p95, not merely be positive.
4. **Block-bootstrap CI** on net Sharpe (preserve autocorrelation) — lower bound must exclude 0.
5. **Baselines** (thesis §10): random-entry matched-turnover; equal-weight buy-and-hold basket;
   **naive-self** (raw-sign, fixed-notional, single 126d lookback, no vol management). Vol management
   must beat naive-self.
6. **Multiple-comparison honesty** — count every cell evaluated (house + the few ±D / C-variant /
   baseline cells); report a deflated-improvement style haircut. The house config is judged first;
   nothing here cherry-picks a grid maximum.

## 7. PRE-STATED decision rule

The screen advances the thesis to a **precommit scaffold (CAMPAIGN_031 proper)** only if **all** hold:

- House book **net Sharpe > 0** after real spread + conservative financing, **and** still > 0 under
  **2× stress**; **and**
- net-Sharpe **block-bootstrap lower CI > 0**; **and**
- book **beats the random-entry matched-turnover null** (above p95); **and**
- book **beats naive-self** (vol management adds value); **and**
- the result is **not an isolated spike** (house config sits in a plausible neighborhood, not a lone
  max).

Otherwise:

- **`COST/FINANCING_DEFEATED`** — pre-cost edge exists but net ≤ 0 (the C026/C029 pattern).
- **`WITHIN_NULL` / `NO_PRE_COST_INFO`** — no edge even before costs.
- **`INSUFFICIENT_POWER`** — sample (7 USD pairs, ~6 yr, ~6 annual cycles) cannot support a
  deflated-Sharpe claim; result is INFORMATIVE only and the thesis is **not** advanced on this data.

Any non-advancing verdict → **`DOES_NOT_EARN_A_SCAFFOLD`**, freeze intact, nothing promoted — the
honest, cheap outcome this platform is built to produce (cf. C028).

## 8. Freeze compliance & reusable infra promised

- No strategy approved; `configs/approved_strategies.yaml` stays empty.
- Lockbox (2025-01 → 2026-05) untouched; validation window untouched.
- Lab stays import-isolated (no broker/strategy/approval imports; no verdict words inside lab code).
- Delivered regardless of verdict: a **first portfolio-level (multi-instrument, vol-targeted) screen
  capability** in the lab, an **H4→D1AGG aggregator** usable by any future daily campaign, and tests.

## 9. Open verify-items carried from thesis §13 (do not block the screen; block any live)

OANDA US per-pair long/short financing rates + weekend-rollover weekday + historical retrievability;
US leverage/FIFO/anti-hedging current values; account-ccy = USD; MOP per-position vol-target figure;
Menkhoff and Baltas-Kosowski citation venues. These gate any eventual promotion, not this gate.

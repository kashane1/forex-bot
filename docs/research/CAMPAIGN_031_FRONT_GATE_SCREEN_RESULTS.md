# CAMPAIGN_031 — Front-Gate Screen Results & Decision (Phase 3)

**Status:** `FRONT_GATE_SCREEN_COMPLETE` / `DOES_NOT_EARN_A_SCAFFOLD` / `NOT_RUN_AS_CAMPAIGN` / `NOT_APPROVED`
**Date:** 2026-05-29
**Thesis:** volatility-managed time-series momentum on OANDA spot FX (user founders pack).
**Precommit:** [`CAMPAIGN_031_VOL_MANAGED_TSMOM_THESIS_AUDIT_AND_PRECOMMIT.md`](CAMPAIGN_031_VOL_MANAGED_TSMOM_THESIS_AUDIT_AND_PRECOMMIT.md)
(frozen house config + screen methodology + decision rule, written **before** the run).
**Freeze:** intact. Train window only (2020-01-01 → 2022-12-29 D1AGG). Validation
(2023-2024) and test/lockbox (2025-01 → 2026-05) never queried.
`configs/approved_strategies.yaml` unchanged (empty).

> The decision logic in §7 of the precommit was fixed before the screen ran. This
> document records the outcome against that bar. It changes no campaign status and
> approves nothing.

---

## 1. What was run

- **Code:** [`research/edge_discovery/vol_managed_tsmom.py`](../../research/edge_discovery/vol_managed_tsmom.py)
  (import-isolated), driven by
  [`scripts/run_edge_discovery_vol_managed_tsmom.py`](../../scripts/run_edge_discovery_vol_managed_tsmom.py).
- **Artifacts:** [`research/campaign_031/front_gate/vol_managed_tsmom_screen.json`](../../research/campaign_031/front_gate/vol_managed_tsmom_screen.json) + `.md`.
- **Universe:** the **7 USD-legged majors** in the store (AUD/EUR/GBP/NZD_USD,
  USD_CAD/CHF/JPY). **No crosses available.** D1AGG daily mid closes built from
  17:00-NY H4 (first 5 of 6 H4 bars/day → 13:00-NY close, rollover-safe).
- **Frozen house config:** sign-blend TSMOM (k∈{63,126,252}d, no signal-level vol
  normalization → avoids the 1/σ² trap) · 1/σ sizing (EWMA com≈60d) · full-Σ 10%
  portfolio vol target · Moreira-Muir overlay (clamp 0.25–1.5) · 15% no-trade band ·
  half-spread turnover cost · conservative financing stress per day held.
- **Comparators:** 2× cost/financing stress; MM-off ablation; naive-C (diag) ablation;
  random-entry matched-turnover null (200 seeds); naive-self baseline (raw-sign,
  equal-weight, single 126d lookback, no vol management); block-bootstrap Sharpe CI.

## 2. Result (778 D1AGG days, train only)

| Configuration | Sharpe pre-cost | Sharpe **net** | boot 5–95% (net) |
| --- | --- | --- | --- |
| **House (full-Σ, MM on)** | +0.323 | **−0.067** | −0.85 … +0.88 |
| House under **2× stress** | — | **−0.456** | −1.25 … +0.49 |
| Ablation: **MM off** | +0.399 | **+0.014** | −0.80 … +0.95 |
| Ablation: naive-C (diag) | +0.283 | −0.033 | −0.88 … +0.86 |
| **Naive-self baseline** | — | **+0.423** | — |
| Random-entry matched-turnover null | — | mean −0.53, **p95 +0.43**, max +0.99 | — |

Cost decomposition (house): total turnover cost **0.020**, total financing stress
**0.088** — **financing is ~4× the spread cost** and is what flips the book negative.
Structural concentration: mean **|net-USD exposure| ≈ 0.90** of gross — the "diversified"
7-pair book is, as the thesis's own Key insight #3 warned, **a single leveraged USD bet**.

## 3. Decision against the frozen rule (precommit §7)

All five advance-conditions **fail**:

| Frozen condition | Result |
| --- | --- |
| House net Sharpe > 0 | **FALSE** (−0.067) |
| House net Sharpe > 0 under 2× stress | **FALSE** (−0.456) |
| Net-Sharpe block-bootstrap lower CI > 0 | **FALSE** (−0.85) |
| Beats random-entry matched-turnover null (p95) | **FALSE** (−0.067 vs +0.43; P(obs≤null max)=0.24) |
| Beats naive-self (vol management adds value) | **FALSE** (−0.067 vs +0.42) |

**Verdict: `COST_FINANCING_DEFEATED` compounded by `WITHIN_NULL` → `DOES_NOT_EARN_A_SCAFFOLD`.**
The thesis is **not** advanced to a CAMPAIGN_031 precommit scaffold on this data.

## 4. Why — three structural facts, all in the artifact

1. **Cost/financing-defeated (the C026/C029 pattern).** A faint pre-cost signal exists
   (+0.32 Sharpe) but real spread + conservative financing erase it (net −0.07; −0.46 at
   2×). Financing dominates, exactly as §7 of the pack predicted for a multi-day
   directional book — and it is *worse* here because the vol-managed book runs higher
   gross (mean ≈1.5, ≈2.2 active) than a naive equal-weight book, paying more financing
   per unit signal.
2. **Vol management does not earn its complexity.** The Moreira-Muir overlay (axis D)
   **subtracts** value net (MM-on −0.07 vs MM-off +0.01) — it fails the pack's own
   "D must earn its place out-of-sample" test — and the **naive-self baseline beats the
   full house config** (+0.42 vs −0.07). The pack's §10 demand that vol management beat
   its naive self is violated outright.
3. **No edge even at the top.** Naive-self's +0.42 sits *at* the random-entry null p95
   (+0.43): the apparent winner is itself indistinguishable from matched-turnover noise.
   Nothing in the configuration set clears the null.

These compound a precommitted-and-acknowledged **power** problem: 7 USD-legged pairs over
~3 train years (~3 annual cycles after the 252d warmup) cannot support a deflated-Sharpe
claim regardless of point estimate (CI spans roughly ±0.9 Sharpe).

## 5. What would change the verdict (not scheduled; restart-criteria-bound)

The decisive limiters are **data**, not signal construction: (i) only USD-legged pairs, so
the USD common factor cannot be diversified or capped; (ii) ~6 calendar years total, far
short of the 10–15y a 1–12-month signal needs; (iii) financing is *stressed*, not *real*.
A genuinely new test would require **acquiring 10–15y daily history including crosses**
(EUR_JPY, EUR_GBP, AUD_JPY, …) so axis-C/net-USD diversification is testable, and a
**real OANDA per-pair long/short financing series** rather than the conservative overlay.
Per [`STRATEGY_RESEARCH_RESTART_CRITERIA.md`](STRATEGY_RESEARCH_RESTART_CRITERIA.md) this is
a fresh-precommit-only path; re-running this same train slice with tuned axes would be the
multiple-testing trap the criteria reject. The thesis's own closing line agrees this gate
is the cheap falsification everything waited behind — and it did not pass.

## 6. What this delivered (reusable infrastructure, independent of the verdict)

- **The lab's first portfolio-level capability:** a multi-instrument, vol-targeted book
  screen (`vol_managed_tsmom.py`) — D1AGG aggregation (pure-pandas, no `forex_bot` import),
  EWMA vol, sign-blend TSMOM, 1/σ sizing, naive + full-Σ 10% vol targeting, Moreira-Muir
  overlay, half-spread turnover + financing-stress overlay, random-entry matched-turnover
  null, and block-bootstrap Sharpe CI. Import-isolated; no broker/strategy/approval import.
- **An H4→D1AGG aggregator** usable by any future daily campaign.
- **11 unit tests** (mechanics + lookahead-free signal + cost-only-reduces + boundary).

This is the first time the lab can screen a **portfolio** idea (not just a single-pair or
two-leg spread idea) cheaply, and it can be reused the moment deeper/wider data exists.

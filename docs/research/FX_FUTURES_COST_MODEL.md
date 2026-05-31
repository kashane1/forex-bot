# FX Futures Venue-Cost Model (Phase 3)

**Sprint:** `research-fx-futures-venue-and-diagnostic-001`
**Type:** Documentation only. Research assumptions. **No trading logic, no sizing, no execution.**
**Date:** 2026-05-31
**Purpose:** Construct a defensible, research-only cost model for CME FX futures, so the diagnostic can compute *net-of-cost* survival for the frozen factors and compare it against the retail spot cost wall that defeated the programme.

> All figures are **research design assumptions** for a gross-vs-net survival diagnostic, not quotes and not trading advice. They are deliberately *conservative* (cost-pessimistic) so a "survives" verdict would be credible. Re-confirm tick/commission figures at ingestion.

---

## 1. Cost components in futures vs the spot wall

The spot programme was defeated by a **two-part wall**: (a) a two-sided spread paid every round-trip, and (b) a **nightly financing squeeze ≈ 4× the spread cost** on any held position (measured in C031). Futures decompose differently:

| Component | Retail spot (the wall) | CME FX futures (this model) |
|-----------|------------------------|------------------------------|
| Spread | ~1.4 bp/side majors; up to ~3 bp crosses | ~0.5 bp/side (≈1 tick) for 6E/6J; wider for thinner contracts |
| Commission | Embedded in spread | Explicit, small (~0.2 bp/side incl. exchange+clearing) |
| Slippage | Variable; worse off-hours | ~0.2–0.5 bp/side on liquid fronts; worse near roll/illiquid |
| **Overnight financing** | **Nightly debit ≈ 4× spread (C031)** | **NONE explicit** — cost of carry is in the basis, paid via convergence/roll |
| Roll cost | n/a (no expiry) | ~1 spread crossing × 2 legs per quarter (~4×/yr) |

**Headline:** futures **structurally removes the nightly financing leg** — the exact wall that defeated C031 and made carry untradable — and replaces it with a *quarterly* roll cost embedded in the basis.

---

## 2. Per-component assumptions (conservative, round-turn)

Round-turn = enter + exit (cross the spread twice). Expressed in basis points of notional.

### 2.1 Spread
- **6E (EUR), 6J (JPY):** top-of-book typically 1 tick wide. 1 tick ≈ 0.00005 / 1.08 ≈ **0.46 bp** for 6E. Round-turn spread crossing ≈ **0.9 bp**.
- **6B, 6S, 6A, 6C, 6N:** thinner; assume 1–2 ticks wide → round-turn **0.9–1.8 bp**.
- **Design value:** 0.9 bp (6E/6J), 1.5 bp (others) round-turn.

### 2.2 Commission (incl. exchange + clearing fees)
- Retail futures commission ~$0.50–$2.50/side; exchange+clearing ~$1.20–$1.60/side. Conservative total ~$2.50/side.
- On 6E notional ≈ $135,000: $2.50 / 135,000 ≈ 0.0185 bp/side → round-turn ≈ **0.04 bp**. (Negligible in bp terms on full-size contracts; larger relatively on E-micros — another reason micros were excluded in Phase 1.)
- **Design value:** 0.4 bp round-turn (deliberately padded ~10× over the arithmetic to stay conservative and cover thinner contracts).

### 2.3 Slippage
- Liquid front-month market orders on modest research size: ~0–1 tick beyond spread.
- **Design value:** 0.5 bp/side → **1.0 bp round-turn** (conservative; real liquid-front slippage is usually less).

### 2.4 Roll cost
- 4 quarterly rolls/year; each roll crosses the spread on 2 contracts (close front + open next) ≈ 2 ticks ≈ 0.9 bp per roll → **~3.7 bp/year** of roll-spread drag.
- Amortized to a monthly carry horizon: ~0.3 bp/month.
- **Plus basis convergence:** not a "cost" per se but the mechanism by which the rate differential is realized (see §4).

### 2.5 Financing
- **Explicit overnight financing = 0.** Futures carry is in the price (basis), not a nightly debit.
- This is the single most important difference from spot and the entire reason Option C was chosen.

---

## 3. Composite round-trip cost (design)

| Contract | Spread | Commission | Slippage | **Round-trip (excl. roll)** | + Roll (annualized) | Financing |
|----------|--------|------------|----------|------------------------------|---------------------|-----------|
| 6E / 6J | 0.9 | 0.4 | 1.0 | **~2.3 bp** | +3.7 bp/yr | 0 |
| 6B/6S/6A/6C/6N | 1.5 | 0.4 | 1.0 | **~2.9 bp** | +3.7 bp/yr | 0 |

**Comparison to the spot wall:** spot round-trip was ~3–5 bp **plus** a nightly financing squeeze (≈4× spread) on holds. Futures round-trip is **~2.3–2.9 bp with zero nightly financing** and a modest quarterly roll. So futures is roughly **1.5–2× cheaper per round-trip and removes the holding-cost wall entirely.**

---

## 4. The crucial subtlety: futures does NOT create free carry

Honest accounting that the diagnostic must respect:

- In **spot**, carry's gross premium was **mechanical accrual** — you earned the rate differential nightly, and a broker reclaimed it as financing (net ≈ 0, financing-defeated).
- In **futures**, that same rate differential is **embedded in the basis** (futures price = spot adjusted for cost-of-carry to expiry). You do **not** receive a nightly accrual; instead the basis **converges** to spot by expiry. The differential is therefore **priced in, not handed out.**

**Implication:** the part of spot carry that was "real but mechanical" largely **disappears as free return in futures** — not because of a cost, but because it was never predictive to begin with (the spot-predictive leg was statistically zero). Futures removes the financing *penalty* and simultaneously removes the accrual *benefit*, because they are the same rate differential viewed from two sides.

So the **honest prior for carry-in-futures gross return ≈ the spot-predictive component ≈ zero.** Futures gives carry a *fair* test (no financing penalty) but cannot manufacture predictability. This is exactly the falsification the diagnostic should make explicit.

---

## 5. What the cost model lets the diagnostic compute

For each frozen factor (subject to data feasibility from Phase 2):
- **Gross** factor return on the continuous futures series.
- **Net** = gross − round-trip cost (per turnover) − amortized roll, financing = 0.
- **Survival check:** does net clear zero / a matched null, using the *same* matched-null and multiple-comparison gates already in the lab — **no new thresholds, no optimization.**

The cost model is intentionally **conservative**: if a factor cannot survive *these padded* costs, it certainly won't survive realistic ones, making a "does not survive" verdict robust; and a "survives" verdict would be credible precisely because the costs were stacked against it.

---

## 6. Explicit non-goals

- No position sizing, leverage, or margin modeling (that is trading).
- No order-type or execution logic.
- No latency/queue model — which is *why* S4 (sub-bar, latency-bound) is out of scope (Phase 2).
- No change to any factor definition; cost is applied *around* the frozen factor, never inside it.

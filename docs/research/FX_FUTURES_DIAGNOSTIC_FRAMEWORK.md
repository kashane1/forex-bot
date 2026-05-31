# FX Futures Diagnostic Framework (Phase 4)

**Sprint:** `research-fx-futures-venue-and-diagnostic-001`
**Type:** Documentation only. Defines *how* a future diagnostic would run. **No execution, no optimization, no strategy.**
**Date:** 2026-05-31
**Purpose:** Specify how the frozen factors (C1, S4, carry) would be evaluated under the futures universe (Phase 1), data (Phase 2), and cost model (Phase 3) — **without altering any factor definition** — so the next sprint can execute mechanically.

---

## 1. First principles (binding)

1. **Definitions are frozen.** C1, S4, and carry are evaluated *exactly* as their existing protocols specify. The only permitted transformations are venue mechanics that preserve the economic exposure:
   - quote inversion for 6J/6S/6C (sign-only re-expression),
   - substitution of the futures continuous series for the spot series as the price input.
   Neither changes a factor's logic, parameters, ranking rule, horizon, or thresholds.
2. **No optimization.** No parameter is searched, fit, or tuned. Roll rule and cost figures are fixed *before* any data is read (pre-registration in the next sprint).
3. **No strategy.** No entry/exit rules, sizing, or execution are created. The diagnostic measures *factor return survival*, not a tradable system.
4. **Reuse the existing gates.** The diagnostic runs through the lab's already-built **matched-null**, **multiple-comparison (Holm/Bonferroni)**, and **cost-feasibility** modules — the same bar every prior factor faced. No new bar is invented.
5. **Gross AND net, always reported together**, with financing = 0 and roll cost explicit (Phase 3).

---

## 2. Per-factor evaluation design

### 2.1 Carry — PRIMARY (feasible on free/local EOD; Phase 2)

**Frozen definition (unchanged):** month-end rank of the 8 currencies by short-rate; HML-3 long-top-3 / short-bottom-3, dollar-neutral, monthly rebalance; horizons 1/3/6/12 months; primary cell = currency HML-3 total, 3-month.

**Futures re-expression:**
- Replace each currency's spot-vs-USD return with the corresponding **continuous futures return** (6E, 6B, 6J, 6S, 6A, 6C, 6N), applying quote inversion where needed so the *currency exposure* matches the frozen definition exactly.
- **Carry source in futures = the basis/roll**, not a nightly accrual (Phase 3 §4). The diagnostic measures the *total* futures return (price change incl. basis convergence) — which is the honest futures analogue of the spot "total" leg.
- The **spot-predictive (price-only) leg** is computed identically to the frozen protocol's spot-only decomposition.

**What it tests:** whether carry, given a *fair* venue (no financing penalty), produces any net survival — or whether, as the cost model predicts, the gross premium collapses toward the spot-predictive component (which was statistically zero). Decisive either way.

**Gates:** matched-random rank null, shuffled-timestamp null, unconditional baseline, Holm correction — **identical** to the spot carry validation.

### 2.2 C1 — SECONDARY / STRETCH (needs paid or account-gated intraday; Phase 2)

**Frozen definition (unchanged):** fade H4+H1+M15 bullish alignment on USD majors; ~30–60 min reversion.

**Futures re-expression:**
- Requires M15/H1/H4 futures bars over a multi-year window → **contingent on an intraday source** (IBKR or paid 1-min vendor). On free/local data this is **not runnable without changing the definition** (collapsing to EOD would alter it, which is forbidden) → therefore **deferred unless an intraday feed is secured.**
- If an intraday feed is available: build HTF futures bars from the intraday series (continuous, ratio-adjusted), apply C1 unchanged, fade signal, measure 30–60 min reversion net of the futures cost model.

**What it tests:** whether the genuine-but-cost-defeated USD-major C1 effect survives the cheaper futures round-trip. Note the **cross-replication failure** (C1_ARTIFACT) means *only* the USD-major form is in scope; no breadth claim.

**Gates:** the same matched-null / cost-feasibility used in the C1 validation.

### 2.3 S4 — EXCLUDED (infeasible on free/local; venue does not relax its binding constraint; Phase 2)

**Frozen definition (unchanged):** M5 triangular no-arb residual reversion, ~0.5 bp, ≤1-bar / ≤5-min half-life.

**Why excluded (documented, not a silent drop):**
- Needs **synchronized intraday/tick across all triangular legs + a latency/queue model** → only paid tick/MBP data and a microstructure backtest could supply it (Phase 2).
- Its binding constraint is **staleness/latency (≤1 bar)**, which is **venue-independent**. A tighter futures spread improves the *size* comparison (0.5 bp edge vs ~2.3 bp futures cost is still ~5× inside cost) but does nothing for the *speed* constraint. Sub-bp triangular arbitrage in listed futures is an HFT/colocation domain, outside this programme's research scope.
- **Conclusion:** re-testing S4 in futures on available data would be both infeasible and uninformative; it is excluded with explicit reasoning rather than run in a way that would mislead.

---

## 3. Evaluation matrix

| Factor | Futures feasibility | Data needed | In scope for next diagnostic? | Honest prior |
|--------|---------------------|-------------|-------------------------------|--------------|
| **Carry** | High (free/local EOD) | EOD continuous, decades | **Yes — primary** | Gross collapses toward ~0 (predictive leg was null); fair test, likely null |
| **C1** | Medium (paid/account intraday) | M15/H1/H4 multi-year | **Stretch — only if intraday secured** | Cheaper cost may lift net, but USD-major-only; modest |
| **S4** | Nil on free/local | Synced tick + latency model | **No — excluded with reasons** | Venue-independent staleness binds; not informative |

---

## 4. Outputs the diagnostic would produce (next sprint, not now)

- Per-factor **gross** and **net** survival vs the existing gates.
- A single verdict per factor: `SURVIVES_IN_FUTURES` / `DOES_NOT_SURVIVE`.
- A roll-up venue verdict: `EFFECTS_SURVIVE_IN_FUTURES` → a real lane finally opens; or `COST_WALL_HOLDS_IN_FUTURES` → trigger the pre-committed archive (Option E).
- All numbers on disk; no result presented as an edge — only as a survival diagnostic with caveats.

---

## 5. What this framework deliberately prevents

- It cannot become a strategy: no entry/exit/sizing is defined.
- It cannot overfit: definitions frozen, no parameter search, gates pre-existing.
- It cannot quietly narrow scope: S4's exclusion and C1's data-gating are documented, not hidden.
- It cannot smuggle in lookahead: roll/adjustment lookahead pitfalls are flagged (Phase 1 §6) and the adapter must use the proven lookahead-safe pattern.

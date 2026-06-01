# Crypto Family C Trend Persistence Diagnostics 001 — Synthesis

**Type:** Exploratory diagnostic only

**Classification:** `STATISTICAL_ONLY_COST_DEFEATED`

Some horizons show weak positive autocorrelation or null rejection, but simple momentum/continuation diagnostics do not survive spread+fee hurdles — similar to FX cost-defeat pattern despite slightly stronger ETH short-horizon AC1.

---

## Answers

1. **BTC statistical persistence?** M15 AC1=0.0005; D1 negative AC1; weak vs null.
2. **ETH statistical persistence?** M15 AC1=0.0129; H1 AC1=0.0087; strongest exploratory AC1.
3. **Strongest horizon?** ETH_USD/M15 — no all-in cost survival.
4. **High-vol concentration?** Mixed; see regime report — BTC D1 low-vol AC1 positive, high-vol negative.
5. **Spread-only survival?** False.
6. **All-in survival?** False.
7. **2× stress?** No positive momentum Sharpe at any horizon.
8. **vs FX programme?** Not materially better — 120 bps taker RT dominates short-horizon momentum proxies, as in FX cost-defeat.
9. **Economic vs statistical?** Statistical hints only (ETH M15 AC1); economically defeated after spread+fees.
10. **Proceed to factor validation?** No.
11. **Family A wait?** Yes — defer MTF confluence.
12. **Family B next?** Yes — recommended.
13. **Family D wait?** Yes until standard-bar diagnostics complete.
14. **Next sprint:** `NEXT_PROMPT_*` for `STATISTICAL_ONLY_COST_DEFEATED` (Phase 7).

---

## Headline Sharpe (momentum proxy)

- ETH M15 gross: 1.0012 · all-in: -77.9377
- BTC H1 gross: 0.0921 · all-in: -33.3498

## Safety

- No strategy, campaign, or approval.
- Gaps: no interpolation; exchange-side gaps accepted; ~99.94% M1 coverage.

**ETH drives short horizon:** True

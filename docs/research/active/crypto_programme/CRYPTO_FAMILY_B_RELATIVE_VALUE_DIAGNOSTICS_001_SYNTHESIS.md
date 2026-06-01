# Crypto Family B Relative Value Diagnostics 001 — Synthesis

**Type:** Exploratory diagnostic only

**Classification:** `STATISTICAL_ONLY_COST_DEFEATED`

BTC/ETH relative structure shows lead-lag, momentum, or reversion statistics but paired spread+fee hurdles (similar to FX S4) defeat economic tradability.

---

## Answers

1. **BTC → ETH lead-lag?** See lead-lag report; H1 lag1 gross bps ≈ 0.03.
2. **ETH → BTC lead-lag?** H1 lag1 gross bps ≈ -0.28.
3. **Relative momentum?** Quintile spreads in momentum report.
4. **Divergence/reversion?** Z-band events in divergence report.
5. **Strongest timeframe?** H4
6. **Strongest effect family?** rel_momentum_lb3
7. **Null robustness?** See null columns in JSON artifacts.
8. **Regime stable?** See regime report.
9. **Spread-only paired survives?** False
10. **All-in paired survives?** False
11. **2× stress survives?** No (by construction if all-in fails).
12. **Better than Family C?** True (gross scale only).
13. **Better than FX S4?** Unlikely economically — similar cost-band trap if gross < paired hurdle.
14. **Factor validation?** No.
15. **Family D next?** If weak/null or cost-defeated.
16. **Family E forward?** Only after spot lanes exhausted.
17. **Next sprint:** Phase 8 prompt for `STATISTICAL_ONLY_COST_DEFEATED`.

**Strongest gross bps:** 4.56

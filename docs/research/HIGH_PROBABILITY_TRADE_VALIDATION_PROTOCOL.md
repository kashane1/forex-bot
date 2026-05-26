# High-Probability Trade Validation Protocol

**Date:** 2026-05-26  
**Branch:** `infra-multi-timeframe-confluence-and-cost-atlas-001`  
**Status:** Pre-registration template — **not authorized** until human approval.

> Diagnostics from the cost atlas / confluence prototype **do not** satisfy this protocol. No strategy approval from infrastructure sprints.

---

## 1. What “higher probability” means

Win rate alone is **insufficient**. Required metrics:

| metric | requirement |
|---|---|
| Expectancy (R) | Primary gate — beat deduped null ≥ **0.05 R** |
| Profit factor | Report alongside expectancy |
| Max drawdown | Must not worsen vs baseline at same trade count |
| Trade count | Minimum per fold and aggregate (pre-registered) |
| Fold stability | Positive or neutral on majority of held-out folds |
| Cost sensitivity | Must not collapse under **2× cost** stress |
| Post-financing | Net PnL after financing model (when available) |

---

## 2. Confluence lift test

Compare **same entry rules** with and without confluence gating:

```text
baseline: all signals
treatment A: grade == A only
treatment B: grade in {A, B}
treatment C: diagnostic only (no trade)
```

Rules:

- Same data, same folds, **frozen** confluence rules (no tuning on results).
- Out-of-sample / walk-forward test windows only.
- Minimum trade counts pre-registered per bucket.
- Report expectancy R, PF, drawdown, trade count per bucket.
- Bootstrap or simple nonparametric CI if tooling exists; else document sample size limits.

**Failure:** confluence raises win rate but destroys expectancy or sample size.

---

## 3. Cross-asset filter test

Each feature requires:

1. Pre-registered economic thesis (why it should help).
2. Frozen threshold or rule (no post-hoc shopping).
3. Documented missing-data handling (`unknown` must not silently pass).
4. No lookahead — forward-fill daily/weekly only.

Test: conditional lift vs same signals without filter, same cost model.

---

## 4. Divergence test

Allowed without separate pre-registration **only** as:

- MR quality boost when HTF range confirmed.
- Exit de-risk on open trend trades.

Forbidden: divergence-only entry unless new standalone hypothesis pre-registered.

---

## 5. Exit overlay test

One exit change per experiment unless pre-registered as a bundle:

| exit | test |
|---|---|
| ATR trailing | vs fixed stop baseline |
| Counter-signal | vs time stop only |
| Regime invalidation | vs fixed stop |
| Time stop by setup | vs global max_bars |

Same entry rule frozen. Report exit-reason mix change.

---

## 6. Sizing rules

- **Kelly deferred** until calibrated `P(win | setup, regime, asset, cost)`.
- Fractional sizing capped by `max_risk_per_trade_pct`.
- Grade multipliers (A=1.25×, B=1.0×, C=0.5×) only after confluence lift validated.
- **No sizing change may rescue negative-expectancy signals.**

---

## 7. Promotion blockers

- Diagnostics ≠ validation.
- No `approved_strategies.yaml` edit from agent.
- No paper/demo/live until separate promotion sprint after all gates pass.
- CAMPAIGN numbering requires new pre-commit; never retune C015–C017 without new thesis.

---

## 8. Required artifacts for a validation campaign

1. Pre-commit checklist (committed before run).
2. Frozen config hash.
3. DEDUPED_INPUT attestation.
4. Walk-forward plan.json.
5. Null comparison vs CAMPAIGN_011 deduped null.
6. 2× cost lane.
7. Human decision memo (even on PASS — still no auto-approval).

# Next Data Expansion Decision

**Decision:** **Add non-USD FX crosses** as the next (and only) data
expansion — first wave **EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY**, second
wave NZD_JPY, EUR_AUD, EUR_CHF, GBP_CHF.

**Scope:** this selects *which data to ingest next*. It is a data/infra
decision. It creates **no** campaign, **no** strategy, runs **no**
backtest, and approves nothing. Paper/demo/live remain blocked; the
approved-strategy registry stays empty.

**Date:** 2026-05-29. Grounded in Phases 0–4 of this sprint and the
corpus viability review.

---

## The candidates considered

| Path | Verdict |
|------|---------|
| **Add non-USD FX crosses** | **Chosen** — cheapest, reuses all infra, directly attacks crowding/breadth, exercises the multi-market gate on familiar ground. |
| Add crypto | Deferred — best free-data + edge potential, but needs a 24/7 calendar and a funding-based cost model (new infra); do it *after* the gate is proven on crosses. |
| Add futures | Deferred — best cost-structure fix, but continuous-roll + contract-calendar infra is the heaviest lift; sequence later. |
| Add alternate FX data source | Deferred — valuable for history-extension and cost-model cross-checking, but it is a *realism* upgrade, not a new search space; fold in after crosses. |

## Why non-USD crosses

1. **Lowest implementation risk, highest information per unit effort.**
   Same OANDA model, same H4 bid/ask + M1 pipeline, same cost-model
   shape, same parity/validation harness. The only net-new work is
   per-cross cost calibration — no new calendar, no roll logic, no
   funding model. It is the cheapest genuinely-new data we can add.
2. **It attacks the exact limitations crosses *can* fix.** The viability
   review's two fixable problems were **USD-leg crowding** and
   **breadth-poverty**. Crosses add independent (non-USD) legs, enabling
   the cross-sectional/carry/relative-value families that were
   underpowered (C016/C028/C031) and supplying **independent
   replications** to settle the residual-USD question for genuine factors
   like C1 (via a fresh pre-registered screen, never a re-tune).
3. **It exercises the generalized front gate end-to-end on familiar
   ground.** Proving the multi-market framework on crosses (same asset
   class, known cost shape) de-risks the harder later expansions
   (crypto, futures) before their infra is built.
4. **It is conservative and freeze-safe.** Free/local, read-only, no
   strategy, no campaign — pure capability + data + diagnostics.

## Why NOT the alternatives first

- **Crypto / futures** have higher edge or cost-structure upside but
  require **new infrastructure** (24/7 calendar + funding model; or
  continuous-roll + contract calendar). Building that *before* the
  multi-market gate is validated risks compounding unproven infra with
  unproven markets. Prove the gate on crosses first.
- **Alternate FX feed** is a realism/history upgrade, not a new search
  space; it adds most value *after* there is more than one asset class to
  cross-check.

## What must be true for this to be worthwhile

- Crosses ingested **lookahead-free and parity-checked**, with
  **instrument-specific** spreads/financing (no EUR_USD cost reuse), and
  EUR_CHF windowed around the 2015 SNB break.
- The expansion is treated as **breadth/replication + capability**, not
  as a cost fix — crosses do **not** relieve the two-sided cost squeeze,
  so no directional-edge claim is expected from them alone.
- The full front-gate rigor (matched-null, ablation, MCC,
  cost-feasibility) is preserved per instrument; null/negative results
  reported honestly.
- It stays free/local; any need for paid data or live credentials is a
  documented blocker, not an action.

If these cannot be met, the fallback is infrastructure/doc hardening
(no expansion) until they can.

## What this decision is NOT

- Not a campaign, not a strategy, not a screen of any thesis, not a
  backtest, not an approval, not a loop enablement. The actual front-gate
  *screen* of any factor on crosses is a later, separately-gated sprint.

The concrete implementation prompt for this decision is in
`NEXT_PROMPT_AFTER_MULTI_MARKET_FRONT_GATE.md`.

# Future Mean-Reversion Research Gate

**Diagnostic only** — `strategy_evidence: false`

Requirements for any **future** mean-reversion campaign. Does not authorize work. Broad strategy search remains **paused**.

---

## 1. Campaign identity

- **New campaign ID** required (e.g. CAMPAIGN_0XX) — **not** C008/C009 retune.
- **New strategy version** string — not `0.1.0-c008` or `0.2.0-c009`.
- Document explicit **market-structure thesis** (why range-bound H4 majors, why now).

## 2. Pre-commit before any run

Written and committed **before** first backtest bar:

- Frozen parameters — no post-hoc sweeps.
- Train / validation / test windows declared.
- Pass/fail gates numeric and exhaustive.
- Human-review ceiling stated (mean-reversion tail risk).
- Diff vs C008/C009 enumerated.

## 3. No parameter selection from prior winners

- **Forbidden:** choosing thresholds from C008 validation winners, C009 midline results, or this post-mortem's descriptive buckets.
- **Forbidden:** session/pair filters derived from train-loser vs validation-winner anatomy without pre-registration.

## 4. Cross-asset regime hypothesis

- Pre-register role of FRED features (if any): e.g. "risk-on only" — not discovered post-hoc.
- Full-window normalized features + H4 alignment must be available **before** run.
- COT/gold optional — not required for gate if thesis does not use them.

## 5. Confluence role pre-declared

- State whether ConfluenceScore is **filter**, **tag only**, or **ignored**.
- No "A-grade profitability" claims without separate validation protocol.
- Do not tune grader weights from C008 outcomes.

## 6. Out-of-sample fold plan

- Minimum: train → validation → test lockbox (2025–2026) discipline preserved.
- Walk-forward or purged folds if thesis requires — pre-declared.

## 7. Minimum trade count

- Per pre-commit: validation ≥ 30 trades (C008 bar); higher if thesis is narrower.

## 8. Beat-null requirement

- Must beat CAMPAIGN_011 random-entry anchor (or successor null) on declared splits.
- WITHIN_NULL classification = automatic REJECT.

## 9. Cost stress

- **2× cost stress** on screening window — expectancy ≥ 0 where pre-commit requires.
- Cost atlas hostile cells documented.

## 10. Financing treatment

- If `max_bars_in_trade` or hold time crosses rollover: financing modeled or explicit diagnostic-blocking flag.
- C008/C009 used stress overlay only — insufficient for live promotion.

## 11. Execution parity

- Backtrader/parity plan pre-declared, or explicit flag that parity gap blocks promotion.

## 12. Promotion path

- Clearing numeric gates → **REVISE at best** for mean-reversion family.
- Paper/demo/live requires: separate promotion sprint, empty-registry edit with human review, evidence integrity CLEAN rerun, broad-search re-entry gates if applicable.

## 13. Explicit forbiddens

- No CAMPAIGN_018 broad discovery substitute.
- No `approved_strategies.yaml` edit from backtest results alone.
- No OANDA order API calls during research sprint.

---

## Disclaimer

Gate definition only. Does not authorize a campaign. No strategy approved.

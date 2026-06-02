# Next Prompt — Crypto Programme Pause Synthesis 001

**Type:** Programme-level synthesis + decision sprint. **NOT** a diagnostics, factor,
campaign, strategy, front-gate, tuning, or paper/demo/live sprint.
**Precondition:** Three crypto factor families have now failed to clear the front-gate bar
on the BTC/ETH corpus — Family C (`STATISTICAL_ONLY_COST_DEFEATED`), Family B
(`STATISTICAL_ONLY_COST_DEFEATED`), Family E (**NO CANDIDATE**; diagnostics 1/2/3/6/7
`rejected`, 4/5 `blocked_low_power_oi` — see
`CRYPTO_FAMILY_E_EXPLORATORY_SYNTHESIS_001.md`).

Work directly on `main`. Commit after each meaningful phase.

## Why this sprint (not more diagnostics)

- **Front-gate design** is not justified: no diagnostic reached `candidate_for_front_gate`.
- **OI forward collection** is low-value *alone*: the high-power diagnostics (1/2/3/6) failed on deep, non-OI funding/basis data, so OI depth was not the binding cause of failure.
- **Family D (non-time bars)** is low-information: it mostly re-samples the same spot OHLCV that Families C and B already showed cost-defeated (this is exactly why Family E was chosen over D).
- Therefore the disciplined next step is a **synthesis that decides whether to pause crypto research**, not another exploratory drill.

## Hard rules

- Do not create a campaign, strategy, or front gate. Do not approve anything; do not edit `configs/approved_strategies.yaml` except to verify it stays empty.
- Do not enable paper/demo/live. No trading/order/account/private APIs; no API keys.
- BTC and ETH only. No altcoins, no universe expansion.
- Do not re-run or re-tune Family C / B / E. Do not invent new factor hypotheses.
- Do not adjust any frozen cost model.
- This is a docs-only synthesis (ZERO new diagnostic code expected).

## What to do

1. **Classify every crypto effort honestly** (data design → ingestion → C → B → E derivatives prep/backfill → E diagnostics). For each: what was tested, the verdict, and whether failure was idea-quality, cost, data-depth, or efficiency.
2. **Diagnose the dominant failure mode** across C/B/E on the BTC/ETH corpus — is it cost, crowding/efficiency, idea quality, or data limits? Be specific and evidence-cited.
3. **Evaluate the one carried-forward thread:** downtrend-conditioned funding mean reversion (Family E diagnostic 7 — BTC+ETH 2×-stress-positive but a single regime slice on a rejected base, full-family-Holm borderline). Decide whether it is worth a future *fresh-pre-registered, walk-forward, full-family-MC, BTC+ETH-robust* re-test, or whether it is most likely a forking-path/overfit artifact. **Do not run it here.**
4. **Evaluate forward-OI collection** strictly as an enabler of diagnostics 4/5 — is the expected information worth the effort given 1/2/3/6 already failed?
5. **Decide the programme disposition:** PAUSE (recommended default) vs. one narrowly-scoped further step. If PAUSE, write explicit restart criteria (new data depth, new external thesis, a genuinely new mechanism) — mirror the FX programme's restart-criteria discipline.
6. Write `CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md` (decision + restart criteria) and update the roadmap/README accordingly.

## Expected outcome

Given three families missed the bar, the honest prior is **PAUSE crypto research** with
documented restart criteria, preserving the one regime-conditional thread and forward-OI as
*conditional* reopen paths under fresh pre-registration. A pause is a legitimate, disciplined
outcome — not a failure to be papered over with another low-information drill.

## Safety

`configs/approved_strategies.yaml` remains empty. Paper/demo/live remain blocked. FX remains
archived. BTC/ETH only. Frozen cost models unchanged.

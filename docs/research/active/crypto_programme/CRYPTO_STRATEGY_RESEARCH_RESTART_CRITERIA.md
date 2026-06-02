# Crypto Strategy-Research Restart Criteria

**Sprint:** `crypto-programme-pause-synthesis-001` · **governance document**
**Status:** Standing decision is `PAUSE_CRYPTO_RESEARCH` (see `CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md`).
This defines the **strict bar** for restarting crypto factor/strategy research. No verdict
change, no approval, no campaign.

> Restarting crypto research is a deliberate, gated action — never a default, and never
> justified by "the last result was almost positive" or "let me condition on one more regime."

---

## 0. Scope guardrails (unchanged on any restart)

- **Universe stays BTC/USD + ETH/USD only.** No altcoins, no basket expansion, as a *rescue*.
- Paper/demo/live remain blocked until a future strategy passes the full gate chain **and** explicit human approval.
- `configs/approved_strategies.yaml` is never a research output.

## 1. A restart requires AT LEAST ONE of the following (necessary triggers)

1. **A genuinely external thesis with a documented mechanism and objective rules**, written
   *before* coding: the economic / market-structure reason it should work in crypto, and an
   unambiguous, codable entry/exit/risk spec. Internal indicator permutations do not qualify.
2. **A new external data source** that materially changes what is testable, e.g.:
   - **deep per-instrument open interest** (multi-year, not 180d aggregate) — the binding gap for diagnostics 4/5;
   - **order-flow / liquidations / taker-buy-sell** or a credible proxy;
   - **options / implied-volatility** surface data;
   - **on-chain** flows (exchange in/out, stablecoin supply) as a non-price source;
   - a **second venue's funding** at a different cadence enabling cross-venue structure (with USD/USDT hygiene).
3. **A public/academic specification structurally different** from every tested family
   (trend persistence / relative value / funding / basis / OI / cross-asset / regime). A
   different *decision variable*, not different thresholds or a timeframe swap.
4. **A known slow, non-latency mechanism** this project can actually capture (no speed
   competition with market makers / arbitrageurs).
5. **A process change that demonstrably reduces multiple-testing / forking-path risk**,
   *paired with* one of triggers 1–4 — a process change alone does not create an edge.

A restart proposal must name which trigger(s) it satisfies and cite the evidence.

## 2. A restart additionally requires (gating conditions, ALL)

- a **pre-committed hypothesis + cost/stop/multiple-testing model** (locked-definition doc written before any run);
- the **standard falsification panel**: matched nulls + conservative all-in cost (incl. funding for perps) + 2× stress + **full-family** multiple-comparisons haircut + BTC-and-ETH robustness + (for context/regime features) not-a-single-slice and not-circular checks;
- **walk-forward / out-of-sample** support, with any TEST split opened only once for a fully pre-committed campaign;
- **structural distinctness** from the closed families (C/B/E);
- explicit separation of **"effect exists" vs "tradable edge exists."**

## 3. What is INSUFFICIENT to restart (explicitly rejected)

- ❌ Re-running the downtrend-conditioned funding-reversion cell as-is, or any re-slice of this sprint's regime cells (forking-path by another name).
- ❌ "Try a different decile / tercile cut." (threshold mining)
- ❌ "Use 4h instead of 24h." (timeframe swap without a new mechanism)
- ❌ "Add one more regime filter."
- ❌ "Condition on one more market state until something is positive."
- ❌ "The last result was almost positive / 2×-positive in one slice." (a single sub-bar slice is not edge)
- ❌ "Add an altcoin to get breadth." (universe expansion as a rescue)
- ❌ "Re-tune the cost model so it passes." (cost models are frozen bright lines)
- ❌ "Re-run a rejected diagnostic with relaxed gates." (gates are bright lines)

## 4. Conditional reopen threads (recorded, NOT yet triggered)

These are the only two threads the programme leaves open — each still requires §1 + §2:

1. **Downtrend-conditioned funding mean reversion** — economically plausible, BTC/ETH-robust,
   2×-positive in one regime slice, but fails full-family Holm and is a single slice on a
   rejected base. Revisit ONLY as a *fresh, independently pre-registered* hypothesis with
   walk-forward and full-family MC. Not a re-tune.
2. **Deep / forward-collected per-instrument OI** — would re-enable diagnostics 4/5 (currently
   `blocked_low_power_oi`). A new-data trigger (§1.2), not a reason to re-drill 1/2/3/6.

## 5. Relationship to campaign-numbering / approval gates

- A restart does **not** create a campaign by itself. It first produces a pre-committed design
  (separate sprint), which only then — if it passes the falsification panel on train/validation
  — earns a single sealed-TEST confirmation.
- No `CAMPAIGN_032` (or any crypto campaign number) is created until a restart trigger is met
  **and** a pre-committed design exists.
- Approval remains a deliberate, reviewed human action requiring the full existing gate chain;
  it is never a research output.

## 6. Default until a trigger is met

`PAUSE_CRYPTO_RESEARCH`. Infrastructure is preserved (ingestion, materialization, validation,
the Family E harness, frozen cost models). Until a valid trigger arrives, the only sanctioned
work is non-strategy: external-data acquisition, external-thesis sourcing, or engineering —
none of which is factor mining on the current corpus.

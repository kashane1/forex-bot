# Next Prompt — After Financing / Rate-Data Ingestion

The financing/rate-data ingestion sprint is complete. A **validated, macro-faithful
carry-differential dataset** (8 currencies, 15 instruments, harmonized FRED 3-month
interbank rates; internally consistent to machine precision; lookahead-safe) now
exists. Readiness verdict: **`READY_WITH_LIMITATIONS`** — sufficient for a **gross,
existence-level** carry factor-validation, **not** for a tradability/front-gate
conclusion (which is gated on a separate real-OANDA-financing ingest), with a
**monthly-cadence + ~5y-spot-window power limit**.

## Sequencing decision

Run the **gross existence study first** (cheap, in-repo, no new credentialed ingest):
it is **decision-forcing** — if carry does not clear the nulls even *gross* on this
window, the mechanism is closed and the (effortful, credentialed) OANDA-financing
ingest is **avoided**; if it *does* clear gross, the *next* sprint ingests real
financing for the decisive net-of-cost gate. This respects the programme's lesson
that cost is the wall, while not paying the financing-ingest cost until a gross
signal justifies it.

## Recommended next sprint — carry gross existence factor-validation (Stage 1–2)

> Branch: `research-carry-factor-validation-001`
>
> **A pre-registered, gross, existence-level carry factor-validation** using the
> committed carry dataset. Build no strategy, no signal, no entry/exit, no campaign;
> approve nothing. **Explicitly gross-only and un-tradable pending real financing** —
> carry is never presented as an edge.
>
> Read first:
> - `CARRY_FACTOR_VALIDATION_DESIGN.md` — the drafted hypotheses, nulls, horizons,
>   failure modes, and verdict map (freeze it into the protocol).
> - `CARRY_RESEARCH_READINESS_VERDICT.md` — the `READY_WITH_LIMITATIONS` scope and
>   the power/financing caveats that bound the study.
> - `CARRY_DATASET_*` (construction/validation/plausibility) — the data asset.
> - `PROGRAMME_LESSONS_LEARNED.md` — C1/S2/S4 lessons (existence ≠ predictive ≠
>   tradable; one frozen spec; matched-null + multiple-comparison mandatory).
>
> The sprint MUST:
> 1. **Pre-register before touching forward spot returns:** the carry construction
>    (monthly differential, lookahead-safe ≥1-month implementation lag), the
>    cross-sectional ranking, **monthly** holding horizons (1/3/6/12m — NOT
>    intraday), the four nulls, and the multiple-comparison rule — one frozen spec,
>    no best-of-N.
> 2. **Measure the GROSS carry-sorted forward return vs matched nulls** — does
>    higher carry predict higher spot-adjusted forward return beyond chance? Report
>    breadth across the cross-section (guard the S2 "exists ≠ predicts" and C016/C031
>    "collapses to a USD bet" traps).
> 3. **Emit a Stage-1/2 verdict** strictly labeled **gross**: `CARRY_REJECTED` /
>    `CARRY_REAL_BUT_WEAK` / `CARRY_GROSS_SIGNAL_PRESENT` (the last earning only the
>    right to a *future* net-of-financing gate). **No tradability claim, no
>    `FINANCING_DEFEATED`/front-gate verdict** — that needs the financing ingest.
> 4. **Stop at the gross verdict.** No campaign, no approval, no paper/demo/live.
>
> Deliverable: precommit + result + verdict docs; new code limited to a carry-
> ranking + forward-return-vs-null study reusing the committed dataset. **NO**
> signal/entry-exit/campaign code.

## The sprint after that (context only — do not start)

- **If `CARRY_GROSS_SIGNAL_PRESENT`:** a **real-OANDA-financing ingest** sprint
  (separate, **explicitly user-authorized**, credentialed — mirroring the cross-
  population sprint), then a net-of-financing carry front-gate. **Not** a campaign.
- **If `CARRY_REJECTED` / `CARRY_REAL_BUT_WEAK`:** the **last in-repo mechanism is
  closed**, which — per the programme synthesis — justifies a deliberate **archive
  (Option D)** or a **venue/market pivot (Option B/C)** decision sprint.

## Guardrails carried into the next sprint

- **No campaign of any number**; the carry work is a factor-validation, not a
  campaign.
- **Carry is never presented as an edge before validation**; any positive result is
  **gross-only** and explicitly un-tradable pending real financing.
- **No OANDA real-financing ingest** in the existence study (separate, later,
  user-authorized); **no broker/order APIs.**
- No strategy approved; `approved: []`; paper/demo/live blocked; `forex_bot.approval`
  fails closed.
- Read-only research-DB + public FRED data only; pre-registration precedes any
  conditioned number; matched-null + multiple-comparison mandatory; one frozen spec.
- Freeze stays intact; evidence + a gross verdict, nothing order-capable.

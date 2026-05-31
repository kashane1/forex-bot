# Next Major Direction — Decision

**Sprint:** `research-cross-factor-programme-synthesis-001` · Phase 5
**Type:** single-direction decision. Docs-only. No factor, screen, campaign, or
strategy. This chooses *what to do next*, nothing more.
**Date:** 2026-05-30.

---

## Decision

# Chosen direction: **Option A — Financing-data ingestion, enabling carry research**

The next major direction is to **ingest real OANDA financing/swap-rate data** as a
first-class data object, so that **carry — the one genuinely untested mechanism —
can later be evaluated on real rates and real carry crosses** (AUD_JPY, NZD_JPY,
EUR_JPY). The **immediate next sprint is a data-ingestion / research-preparation
sprint**, *not* a carry factor screen, *not* a campaign.

> This is a direction + a data prerequisite, not a factor and not a screen. Phase 6
> writes the exact next prompt (a data sprint).

---

## Evidence-based justification

1. **It is the only genuinely-new mechanism left, and it is nearly testable
   in-repo.** Phase 1 shows every effort to date is a **spread-capture or reversion**
   mechanism — all rejected, cost-defeated, or real-but-sub-cost-band. **Carry is a
   different return source** (interest-rate differential), was **data-blocked for the
   entire programme**, and only became testable when the cross expansion added real
   carry pairs (Phase 3 §1). Testing it is **not** re-mining the exhausted family
   space — it closes a real gap.

2. **Highest information gain per unit cost (Phase 4: composite ~4.4, the clear
   leader).** It reuses the existing OANDA vendor, ingest/materialization pipeline,
   candle store, cost models, and front-gate lab (repo compatibility 5) for a modest
   data-ingestion lift (implementation cost 4). Every other option is a large
   venue/market lift (B, C) or learns nothing (D).

3. **It resolves the programme's open question either way — and is decision-forcing.**
   - If carry **survives** real-financing cost → the programme finally has a genuine,
     differently-sourced factor worth a *future, separate* front-gate screen (a real
     first).
   - If carry is **financing-defeated** (the honest base rate, given C031's financing
     ≈4× spread and carry-crash risk) → the **last in-repo mechanism is closed with
     real evidence**, which *cleanly justifies* either archiving (Option D) or a
     deliberate venue/market pivot (Option B/C) — decisions that are **premature
     today** precisely because carry is untested.

4. **The financing-data asset is valuable regardless of the carry verdict.** Real
   swap rates sharpen every overnight-cost estimate, replace the registry's
   *estimate* rates (removing a standing data-integrity caveat), and are a permanent
   platform improvement — so the sprint has positive value even if carry later fails.

5. **It respects every standing constraint and the freeze.** It introduces **no new
   venue, no new market, no paid data, no trading**; it is the lowest-repeat-risk way
   to make genuinely new progress. It also honors the corpus-review rule
   (CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS): **carry is a new mechanism with a
   decades-deep external evidence base**, not a re-tune.

## Why not the others (now)

- **B (lower-cost venue / tick):** highest ceiling — S4 proved real RV structure
  exists sub-retail-cost — but a large paid-data + execution-realism lift,
  overfit-prone, and premature before the cheap in-repo mechanism (carry) is
  resolved. **Sequenced after A** (and most compelling if carry is also
  cost/financing-defeated).
- **C (new market: futures/metals/crypto):** best edge diversity and the best
  structural cost fix (futures), but the largest infrastructure lift (roll/calendar/
  cost models). The corpus review already deferred it; it remains the pivot if the
  spot-FX venue is fully closed. **Sequenced after A.**
- **D (stop/archive):** **premature.** Archiving before testing the one cheap,
  untested mechanism would leave the programme's evidence incomplete. D becomes the
  *right* call **after** carry — if carry is financing-defeated and there is no
  appetite for B/C.

## Explicit scope guard for the chosen direction

- The immediate sprint is **data ingestion + research preparation only** — ingest
  real financing/swap rates, validate them, document the carry *design* — and
  **stops there**.
- It does **NOT** run a carry factor-validation, build a carry signal, screen,
  campaign, or approve anything. Carry-the-factor is a **separate, later**
  pre-registered factor-validation sprint, gated on this data existing.
- **Carry must never be evaluated on estimate rates** — doing so would repeat C031's
  financing-defeat on guessed costs (a Phase-2 lesson).

## Pre-stated success criteria for the eventual carry work (recorded now)

So the future carry sprint cannot drift: carry "exists" only if a pre-registered,
real-financing, matched-null carry construction on the cross carry pairs clears the
nulls **net of real financing** at a cost-stress multiple, stable across years and
the risk-off regime — exactly the bar every prior factor faced. A positive gross /
negative net result is `FINANCING_DEFEATED`, not a factor.

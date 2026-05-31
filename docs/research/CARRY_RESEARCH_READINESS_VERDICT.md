# Carry Research — Readiness Verdict (Phase 6)

**Sprint:** `research-financing-rate-data-ingestion-001` · Phase 6
**Type:** readiness verdict on the carry **data asset**. Docs-only. No factor study,
no edge claim.
**Date:** 2026-05-31.

---

## Verdict

# `READY_WITH_LIMITATIONS`

The carry-differential **data asset is research-grade and sufficient to justify a
future GROSS, existence-level carry factor-validation (Stage 1–2)** — but it is
**NOT** sufficient for any **tradability / front-gate** conclusion, which is gated on
a separate real-OANDA-financing ingest, and the **monthly cadence + ~5-year spot
window** materially limit statistical power. Carry is **ready to be studied for
existence, with explicit limitations — not ready for a tradability verdict.**

---

## Why READY (the data asset is sound)

1. **Complete & gap-free** over the corpus window — all 8 currencies / 15
   instruments, 60 monthly points each, no mid-window gaps (Phase 3 §1–§2).
2. **Internally consistent** — triangular rate residual = 1.78e-15; cross carry =
   sum of USD-leg carries exactly (Phase 3 §3).
3. **Lookahead-safe at monthly cadence** — strictly-prior forward-fill; the only
   imputation is the documented 1–4-month publication-lag tail (Phase 2 §2).
4. **Macro-faithful** — reproduces ZIRP/negative rates, the 2022–23 hiking peak, the
   2024–26 easing, the BoJ exit, the ECB/SNB lag, and the signature 2022–24
   USD_JPY/AUD_JPY carry-trade episode (Phase 4). Funding pair (JPY/CHF) persistently
   lowest; high-yield side (NZD/USD/AUD) sensible; genuine time-varying
   cross-sectional dispersion.
5. **Reproducible & provenanced** — public FRED source, committed series ids + fetch
   metadata, gitignored cache, no key committed.

→ A **gross, existence-level** study ("does carry-sorted forward spot return clear
matched nulls?") is fully feasible on this asset.

## Why WITH LIMITATIONS (what it cannot yet support)

1. **Interbank ≠ broker financing (the binding gate is missing).** This dataset is
   the carry **signal**, not the carry **cost**. Any tradability claim requires
   **real OANDA broker financing** (interbank + markup — the C031 ≈4× reality), which
   is **not yet ingested**. Without it, a front-gate / `FINANCING_DEFEATED` verdict
   **cannot** be reached. (Deliberately deferred to a separate user-authorized step.)
2. **Monthly cadence + ~5y spot window = low power for a slow signal.** ~60 monthly
   points / ~5 years of overlapping holding periods give **few independent
   observations** of a premium that academically needs decades to separate from
   carry-crash noise. Forking-path risk is high if horizons/rebalances are mined; the
   ~5y window is also **regime-narrow** (one hike-cut cycle, no major carry crash like
   2008/2020).
3. **Deep rate history but shallow spot history.** The rate series go back to ~2002,
   but the **spot** corpus is ~5y — so the test window is bounded by spot, not rates,
   unless longer spot data is added.
4. **Carry-crash regime largely absent** from the window — the property most likely
   to defeat carry (risk-off unwind) is under-sampled.

## Why not NOT_READY

The data is genuinely complete, consistent, lookahead-safe, and macro-faithful — a
*gross existence* study is feasible and worthwhile. Declaring NOT_READY would
understate a sound, validated asset.

## Why not (unqualified) READY_FOR_FACTOR_VALIDATION

The **decisive tradability gate — real broker financing — is missing**, and the
~5y/monthly power limit is real. Calling it unqualified-ready would risk a future
study over-claiming carry as an edge on the interbank signal alone (the exact
"no-edge-before-validation" failure the hard rules forbid). The honest status is
**ready *with* these limitations**.

## Conditions to upgrade to READY_FOR_FACTOR_VALIDATION

1. **Ingest real OANDA broker financing** (separate, user-authorized) → enables the
   net-of-cost gate.
2. (Optional, strengthens power) **Extend spot history** toward the available ~20y+
   rate history, or accept the existence-only scope with pre-registered,
   power-limited horizons.

## Practical implication

The **next sprint** can proceed as a **gross, existence-level carry factor-validation
(Stage 1–2)** using this asset — pre-registered, matched-null, **explicitly labeling
any positive result as gross-only and un-tradable pending real financing** — OR
first run the OANDA-financing ingest to enable a full net-of-cost study. Either way:
**no campaign, no approval, carry never presented as an edge before validation.**
Phase 7 drafts the prompt.

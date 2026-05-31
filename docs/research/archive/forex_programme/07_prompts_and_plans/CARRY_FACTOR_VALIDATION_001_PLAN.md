# Carry Factor-Validation 001 — Plan (Phase 0)

**Sprint:** `research-carry-factor-validation-001` · Phase 0
**Type:** factor-validation study **only** — gross, existence-level. **NOT** a
campaign, strategy, front gate, tradability study, or financing-cost study. No
trades, no entry/exit, no approval, no broker, no OANDA financing.
**Date:** 2026-05-31.

---

## 0. What this sprint is (and is not)

This sprint answers **one** question:

> Does carry exhibit **statistically meaningful gross predictive power** in the
> research FX universe — before any effort is spent on broker-financing realism?

It is the **execution** of the future-study design drafted at the end of the
financing-rate-data-ingestion sprint
([CARRY_FACTOR_VALIDATION_DESIGN.md](CARRY_FACTOR_VALIDATION_DESIGN.md)), tightened
into a frozen protocol and run against the now-available carry data asset.

Hard scope rules (verbatim from the sprint prompt, restated as binding constraints):

- Do **not** create CAMPAIGN_032 or any campaign.
- Do **not** create entry/exit logic, trading rules, or a front gate.
- Do **not** approve any strategy; do **not** enable paper/demo/live.
- Do **not** call broker APIs; do **not** use OANDA financing data.
- Do **not** alter definitions after data review.
- Carry is evaluated **gross only**.

## 1. Baseline audit — what already exists

Reviewed before writing this plan:

| Artifact | What it establishes |
|---|---|
| [FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_SUMMARY.md](FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_SUMMARY.md) | the prior sprint's scope & outcome |
| [CARRY_DATASET_CONSTRUCTION.md](CARRY_DATASET_CONSTRUCTION.md) | how the carry signal was built (FRED OECD 3M interbank, `IR3TIB01<CC>M156N`) |
| [CARRY_DATASET_VALIDATION.md](CARRY_DATASET_VALIDATION.md) + [CARRY_DATASET_PLAUSIBILITY_REVIEW.md](CARRY_DATASET_PLAUSIBILITY_REVIEW.md) | the signal is complete, internally consistent (tri-residual 1.78e-15), macro-faithful |
| [CARRY_RESEARCH_READINESS_VERDICT.md](CARRY_RESEARCH_READINESS_VERDICT.md) | verdict `READY_WITH_LIMITATIONS` — good for a **gross existence** study, **not** tradability |
| [CARRY_FACTOR_VALIDATION_DESIGN.md](CARRY_FACTOR_VALIDATION_DESIGN.md) | the draft study design this sprint freezes & executes |
| `research/carry/carry_rates.py` | the construction code (rate panel → monthly matrix → carry differentials) |
| `docs/research/carry_rates/*.csv` | the committed data asset (rate series + 15-instrument carry differentials) |

**Programme context** (from prior synthesis): every in-repo factor family has been
rejected, failed replication, or proved real-but-sub-cost; the dominant failure mode
is **cost**, not idea quality. Carry was identified as the *only* genuinely-new,
nearly-testable-in-repo mechanism. This sprint resolves whether the carry *signal*
even has gross predictive power — the cheapest decisive question before any
financing-realism work.

## 2. Data available (audited this sprint)

- **Carry signal:** `docs/research/carry_rates/` — monthly per-currency interbank
  rates (8 currencies, 1995→2026) and per-instrument carry differentials (15
  instruments). Real FRED data, lookahead-safe at monthly cadence.
- **Spot returns:** the canonical local research store `data/campaign_002.sqlite3`
  holds **real** H1/H4/D bars for the **7 USD majors** (EUR_USD, GBP_USD, USD_JPY,
  AUD_USD, NZD_USD, USD_CAD, USD_CHF), 2020-01 → 2026-05. Spot-checked against the
  real 2021→2026 carry-trade era (USD_JPY 109.5 → 159.0, EUR_USD 1.223 → 1.160) —
  these are genuine market levels, **not** the obfuscated copy in `campaign.sqlite3`.

### 2.1 Resolving the "8 crosses have no spot bars" concern

The 8 cross instruments (EUR_JPY, AUD_JPY, …) were ingested only on an **unmerged**
branch; their bars are **not** in merged `main`, and re-ingesting requires a broker
API (forbidden this sprint). This would appear to block the JPY-cross carry pairs —
the genuinely high-yield-vs-funding instruments.

**It does not**, for a *gross* study, because of no-arbitrage:

1. The 7 USD majors give every one of the **8 currencies'** log-return vs USD
   (USD is the numeraire; the other 7 come directly from the major pairs). This makes
   the **full 8-currency cross-sectional carry** portfolio fully computable.
2. Any cross's gross **mid** log-return equals the sum of its two USD-leg log-returns
   (`r(AUD_JPY) = r(AUD_USD) + r(USD_JPY)`), an identity the carry differentials
   already satisfy to machine precision. So all **15 instruments'** gross spot returns
   are derivable exactly from the majors.

The only thing genuinely unavailable is each cross's **own bid/ask spread and
financing** — which is a *cost*, irrelevant to a **gross** study and explicitly
deferred to the future financing-aware gate. Documented as a limitation, not a
blocker.

## 3. Hypotheses (to be frozen verbatim in the Phase-1 protocol)

- **H1 — UIP-failure / spot predictability:** currencies (instruments) with higher
  carry differential earn higher *spot* forward returns than lower-carry ones — i.e.
  the carry is **not** fully offset by spot depreciation.
- **H2 — cross-sectional carry premium:** ranking the 8 currencies (and, secondarily,
  the 15 instruments) by carry and going long top / short bottom earns a positive
  **gross** total return (spot + accrued interbank carry) beyond a matched null.
- **H3 — carry-crash asymmetry (descriptive):** carry returns are negatively skewed /
  weakest in risk-off months — a *risk property to characterize*, never an edge.
- **Direction is an empirical output**, never assumed. "Carry pays" must be measured.

## 4. Success criteria (what would make carry a `FACTOR_FRONT_GATE_CANDIDATE`)

A gross carry premium that **simultaneously**:

1. is correctly signed and material (HML mean clearly > 0 on the primary metric);
2. **clears every null** (randomized ranks, shuffled-timestamp, matched, unconditional)
   at a multiple-comparison-aware threshold across the pre-registered horizon grid;
3. is **broad** — coherent across currencies, instruments, years, and regimes, not
   carried by one currency/pair/episode (the C1 lesson);
4. is **robust** to nearby definitions / rankings / windows / lags (Phase 6).

Such a result would *merit future financing-aware evaluation* — it would **not** be an
edge, a strategy, or an approval.

## 5. Failure criteria (what rejects carry)

- HML return within the null band (does not clear matched/shuffled nulls) — `FACTOR_REJECTED`.
- Sign-incoherent / carried by a single currency, pair, or one carry-trade episode.
- Collapses to a structural USD or risk-on bet (the C016/C031 collinearity failure).
- Unstable across nearby specs (a forking-path artifact).

A genuine, null-separated, broad gross premium that is nonetheless **small / fragile /
regime-narrow** → `FACTOR_REAL_BUT_WEAK` (survives validation & nulls, insufficient
magnitude for a standalone edge).

## 6. Gross-only scope (explicit)

- Returns are **spot mid** + **accrued interbank carry** (the economic signal).
- **No** transaction cost, **no** broker spread, **no** OANDA financing markup is
  charged or modelled. A positive gross result is therefore **un-tradable on its own**
  and is reported as such — the net-of-financing gate is a *separate, later,
  user-authorized* sprint, not this one.
- The ~59-month spot window at monthly cadence is **low-powered** for a slow signal;
  this is pre-registered as a limitation, and multiple-comparison control is mandatory.

## 7. Phase plan & artifacts

| Phase | Output |
|---|---|
| 0 | this plan |
| 1 | `CARRY_FACTOR_PROTOCOL.md` — frozen universe, definitions, nulls, stats |
| 2 | `CARRY_FACTOR_CONSTRUCTION.md` — factor *exposures* (no returns) |
| 3 | `CARRY_FACTOR_RESPONSE_STUDY.md` — forward-return response |
| 4 | `CARRY_FACTOR_CROSS_SECTIONAL_VALIDATION.md` — currency/pair/regime/year consistency |
| 5 | `CARRY_FACTOR_NULL_COMPARISON.md` — vs randomized / shuffled / matched / unconditional |
| 6 | `CARRY_FACTOR_ROBUSTNESS.md` — nearby specs (robustness, not optimization) |
| 7 | `CARRY_FACTOR_VERDICT.md` — exactly one of REJECTED / REAL_BUT_WEAK / FRONT_GATE_CANDIDATE |
| 8 | `NEXT_PROMPT_AFTER_CARRY_FACTOR_VALIDATION.md` — implications + next prompt |
| 9 | `CARRY_FACTOR_VALIDATION_001_SUMMARY.md` + gate runs |

Research code: `research/carry/carry_factor.py` (import-isolated; no broker / loops /
approval deps) + runner `scripts/run_carry_factor_validation.py` writing artifacts
under `research/carry/factor_validation/`. Tests under `tests/research/carry/`.

Freeze remains intact throughout: `approved:[]`, paper/demo/live blocked.

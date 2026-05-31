# Implications & Next Prompt — after Carry Factor-Validation 001 (Phase 8)

**Sprint:** `research-carry-factor-validation-001` · Phase 8
**Verdict carried in:** `FACTOR_REAL_BUT_WEAK` ([CARRY_FACTOR_VERDICT.md](CARRY_FACTOR_VERDICT.md)).
**Date:** 2026-05-31.

---

## 1. Implications of `FACTOR_REAL_BUT_WEAK`

1. **Carry is a real gross premium but not an edge.** A correctly-signed, broad-ish,
   spec-robust gross cross-sectional carry premium exists (+0.74%/quarter). But it is
   **mechanical accrual with no spot-predictive content**, **marginally significant**
   (3m t=1.68), **single-name dependent** (drop-JPY → +0.0003), and **untimed** (fails the
   timing null; momentum spec flips negative). It is a static risk-premium tilt, not an
   alpha signal.
2. **The last genuinely-new in-repo mechanism is now resolved.** The programme synthesis
   identified carry as *the only genuinely-new, nearly-testable-in-repo mechanism left*.
   It has now been tested and lands where every prior family did — real-but-weak /
   structurally cost-exposed. **The in-repo factor-discovery search is effectively
   exhausted**; the corpus's `CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS` status stands,
   reinforced.
3. **The premium *is* the financing charge.** The positive part (accrual of the rate gap)
   is exactly what a retail broker reclaims as financing; the prior C031 result put OANDA
   financing at ≈4× spread. There is no spot-predictive residual to survive that charge.

## 2. Is financing ingestion worthwhile? — **No (not for a strategy).**

The Phase-1 plan framed this sprint as the cheap gate to run **before** spending effort on
broker-financing realism. That gate has now returned a clear answer:

- **Information value of a financing-aware carry study is low.** Its outcome is near-
  predetermined: gross premium ≈ the accrual; financing reclaims most of that accrual plus
  spread; spot-predictive residual = 0 → the overwhelmingly likely verdict is
  **`FINANCING_DEFEATED`** (the pre-registered failure label, and the C031/S4 pattern).
- **Cost is high and gated.** Ingesting real OANDA financing requires a **broker API and
  explicit user authorization** (out of scope here by hard rule). Spending that to confirm
  a near-certain negative is poor value.
- **Therefore:** do **not** open a financing-ingestion sprint *for the purpose of building
  a tradable carry strategy.* The gross study already shows there is no edge underneath
  the financing line.

**Where carry still has value (non-strategy):** as a **risk / context factor** — a
descriptive regime indicator (funding-currency stress, carry-unwind risk) layered on
*existing* analysis, never as a standalone signal. And the carry dataset remains a sound,
reusable data asset.

## 3. Recommended next step

**Programme-level decision sprint — not another factor study.** Carry was the last
in-repo mechanism; with it resolved, the honest next move is to *decide the programme's
direction*, not to mine further. Recommended: **archive the in-repo factor-discovery
search as exhausted**, record carry's real-but-weak / financing-defeated-by-construction
finding in the programme synthesis, and (optionally) reposition carry as a context factor.
Only pursue financing realism if the user explicitly wants *closure confirmation* that
carry is financing-defeated (a single, cheap, pre-registered net study) — and even that
needs broker-financing data and user authorization.

---

## 4. Next prompt (copy-paste)

> **Programme-direction decision after carry resolution (docs-only synthesis sprint).**
>
> Branch: `research-programme-direction-after-carry-001`. Start from clean origin/main.
>
> Context: the carry factor — the last genuinely-new, in-repo-testable mechanism — has
> been validated gross and returned `FACTOR_REAL_BUT_WEAK`: a real but mechanical,
> predictive-null, single-name (JPY), untimed static premium whose positive part is the
> very accrual a broker reclaims as financing (expected `FINANCING_DEFEATED`). Every prior
> family was rejected / failed-replication / real-but-sub-cost / cost-defeated. The corpus
> remains `CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS`.
>
> This sprint is **docs-only**. No code, no data ingest, no campaign, no strategy, no
> approval, no broker API, no OANDA financing. Freeze stays intact.
>
> Do:
> 1. Update the programme synthesis to classify carry (real-but-weak gross /
>    financing-defeated-by-construction) and mark the **in-repo factor-discovery search
>    exhausted**.
> 2. Lay out, score, and recommend the programme's go-forward options:
>    (A) **archive** the in-repo search as exhausted and stop mining;
>    (B) reposition carry as a **risk/context factor** (non-strategy use), specifying how;
>    (C) define what a genuinely **new external thesis or dataset** (longer/cheaper venue,
>        true tick/L2, non-USD-cross spot bars, real financing) would have to provide to
>        reopen the search — as a *spec*, not an ingest;
>    (D) a single cheap **financing-defeat confirmation** for carry — only if the user
>        wants closure, and only with explicit authorization for broker-financing data.
> 3. Recommend one, with the decision criteria made explicit. Decision-forcing, honest
>    about the cost wall; do not weaken the freeze.
>
> Deliver a synthesis doc + a recommended-direction doc + a memory update. Nothing
> approved; paper/demo/live stay blocked.

# Next Prompt — After Currency-Strength Factor Validation

The S2 cross-implied currency-strength factor-validation study is complete.
Verdict: **`FACTOR_REJECTED`** — the strength vector is a **real, breadth-diverse
descriptor** (breadth hypothesis H2 *passed*: PC1 is a haven-vs-risk axis, not a
USD axis) but carries **no forward-predictive information**: 0/80 null cells clear
|z| ≥ 2 (global max 1.65), means ≈1–2% of path noise, sign-incoherent across every
currency/year/session/lookback/aggregation. Strength **persists** but does not
**predict**.

## Decisive implication for the shortlist

- **S3 (currency cross-sectional momentum) is now pre-falsified — do NOT run it.**
  S3 *is* "rank currencies by strength, trade winners vs losers." This sprint
  showed the strength ranking has **no forward-return information** at 5–240 min,
  so S3 would inherit the same nullity by construction. Running it would be
  variant-hunting against a freeze. **S3 is closed by this result** (absent new
  data or a fundamentally different ranking signal).
- **S5 (regime gate) is moot** — it is an overlay needing a surviving generator;
  S1 (C1) and S2/S3 have all failed, so there is nothing to gate.

## Recommended next sprint — S4 cross relative-value / cointegration (Stage 1–2)

> Branch: `research-cross-relative-value-factor-validation-001`
>
> **A pre-registered Stage-1/2 factor-validation study of economically-motivated,
> half-life-matched mean-reversion in cross spreads** on the already-populated
> universe. This is the **one remaining shortlist family that tests a
> fundamentally different mechanism** — *reversion of a stationary spread*, not
> *directional/cross-sectional prediction* — so it is **not** pre-falsified by the
> three directional nulls (C1 cost-defeat, C1 cross-replication failure, currency
> strength rejection). Build no strategy, create no campaign, approve nothing.
>
> Read first:
> - `CROSS_UNIVERSE_FACTOR_SHORTLIST.md` (S4) — thesis, the two C028 failure modes
>   it must fix, gate reqs.
> - `CURRENCY_STRENGTH_FACTOR_VERDICT.md` — why directional/cross-sectional breadth
>   is now closed on this corpus (and why S3 is pre-falsified).
> - `DO_NOT_REPEAT_LIST.md` §1/§4 — the C028 selection-noise + two-leg-cost fences;
>   RV reopens ONLY with economically-motivated, pre-named spreads + half-life ≤
>   hold (NOT best-of-N spread mining).
> - `relative_value_spread.py` (existing C028 lab module) — reuse, do not refit.
>
> The sprint MUST:
> 1. **Pre-register before touching data:** the small set of **economically-named**
>    cross spreads (e.g. JPY-cross complex EUR_JPY/GBP_JPY/AUD_JPY/NZD_JPY sharing
>    the JPY leg; EUR_GBP vs the EUR_USD/GBP_USD triangle), the cointegration test,
>    the **half-life ≤ intended-hold precondition**, the response/null methodology,
>    and the multiple-comparison correction over the *pre-named* set only.
> 2. **Test existence, not tradability** — does a pre-named spread mean-revert
>    beyond a matched null on a gross/descriptive basis? Cost is recorded
>    descriptively only.
> 3. **Emit one Stage-2 verdict** (`FACTOR_REJECTED` / `REAL_BUT_WEAK` /
>    `FRONT_GATE_CANDIDATE`). No campaign, no approval, no front gate built.
>
> Deliverable: precommit + result + verdict docs. New code limited to reusing the
> cointegration utility; NO strategy/signal/entry-exit/campaign code.

## If S4 also fails (state the stop-criterion now)

If S4 is `FACTOR_REJECTED`, then **all five planning-sprint shortlist families
(S1–S5) will have failed or been pre-falsified** on this corpus, and the
no-new-data factor search is **exhausted**. The only remaining genuinely-different
return source is **carry (interest-rate differential)** — which rests on a
**different mechanism than every family tested so far** but is **prerequisite-
blocked on real financing/swap-rate data**. At that point the recommended move is
a **data sprint** — `research-financing-data-ingest-001` (ingest real OANDA
financing/swap rates for the carry crosses AUD_JPY/NZD_JPY/EUR_JPY) — **not**
another factor screen on the same M5 mids. Carry cannot be honestly validated on
the registry's *estimate* rates (that repeats C031's financing-defeated failure on
estimated costs).

## Guardrails carried into the next sprint

- **No campaign of any number**; S4 is a factor-validation study.
- **Do not run S3** (pre-falsified) and **do not revive** C1 or the naive C028 RV.
- **Carry stays prerequisite-blocked** on a separate financing-data ingest sprint.
- No strategy approved; `approved: []` stays empty; paper/demo/live blocked;
  `forex_bot.approval` fails closed.
- Read-only research-DB access is acceptable (no trading APIs, no broker creds,
  no orders).
- Pre-registration precedes any conditioned number; matched-null +
  multiple-comparison mandatory (Stage-2 bar).
- Freeze stays intact; evidence + a verdict, nothing order-capable.

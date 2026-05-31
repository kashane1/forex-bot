# Next Prompt — After C1 Cross-Replication

The C1 cross-replication screen is complete. Verdict: **`REPLICATION_FAILED`** —
the C1 factor's significant magnitude (EUR_USD/USD_JPY) **does not replicate** on
the 8 non-USD crosses (sign-inconsistent, indistinguishable from the
session-matched null on the required set, unstable across years/sessions/vol/spec;
the lone null-clearing pair GBP_CHF is a period-/off-hours-concentrated optional
single-pair noise hit). This lands on the planning sprint's pre-stated
**`C1_ARTIFACT`** branch.

Per the realized verdict and the Phase-6 implications, the next discovery
direction is **S2 — the cross-implied currency-strength index** (the highest-
ranked *new*, breadth-pure family; needs no new data; removes the USD-collinearity
that C016, C031, and now C1 all reveal as a confound).

> The next sprint **may open a factor-validation discovery sprint** for S2. It is
> **not** a campaign, **not** a strategy, **not** a trading front-gate, **not** a
> train/validation/test exercise. It produces descriptive factor evidence + a
> verdict, exactly as the C1 validation and this replication screen did.

---

## Recommended next sprint — S2 currency-strength factor validation (Stage 1–2)

> Branch: `research-currency-strength-factor-validation-001`
>
> **A pre-registered Stage-1/Stage-2 factor-validation study of a cross-implied
> currency-strength construction**, on the already-populated 15-instrument
> universe (7 majors + 8 crosses). Build no strategy, create no campaign, approve
> nothing, enable no paper/demo/live. Descriptive factor evidence + a
> `GENUINE_FACTOR` / `WITHIN_NULL` / `SELECTION_NOISE` verdict only.
>
> Read first:
> - `CROSS_UNIVERSE_FACTOR_SHORTLIST.md` (S2) — thesis, failure modes, gate reqs.
> - `C1_CROSS_REPLICATION_IMPLICATIONS.md` — why S2 is preferred now.
> - `DO_NOT_REPEAT_LIST.md` — the collinearity-masquerading-as-breadth trap (§4)
>   and the C016-with-crosses hidden-re-tune fence (§3).
> - `EXPANDED_FX_SEARCH_SPACE_MAP.md` (Category E) — what strength/dispersion
>   newly enables.
> - `MULTI_MARKET_FRONT_GATE_FRAMEWORK.md` — Stage-1/Stage-2 evidence bar.
>
> The sprint MUST:
> 1. **Pre-register before touching data.** Freeze, in a committed precommit doc:
>    the **decomposition method** (e.g. average-of-pairs log-return per currency,
>    or a least-squares decomposition of the 15-instrument return matrix — choose
>    ONE), the lookback, the response horizon, the rebalance/measurement cadence,
>    the matched-null design, and the multiple-comparison correction. No best-of-N
>    over methods/lookbacks.
> 2. **Decompose to currencies, not pairs.** Explicitly avoid the Phase-3 trap:
>    EUR loads on 5 instruments — a proper per-currency strength vector, with a
>    reported **variance-explained-per-currency** collinearity diagnostic, not a
>    naive pile of correlated pairs (that would be C016 with leakage).
> 3. **Test the factor, not a strategy.** Measure whether currency-strength
>    divergence/extremity predicts subsequent pair moves on a **gross,
>    descriptive** basis vs a matched null — Stage 2 asks *"is the effect real?"*,
>    not *"is it tradable?"*. Cost is recorded descriptively only.
> 4. **Read every number from committed artifacts** (artifact-first; verify
>    CSV-on-disk before quoting — the standing integrity rule).
> 5. **Emit one Stage-2 verdict.** If `GENUINE_FACTOR`, recommend a *separate,
>    later* pre-registered Stage-3 cost/front-gate screen (never an automatic
>    campaign). If `WITHIN_NULL`/`SELECTION_NOISE`, recommend the next shortlist
>    item (S3 cross-sectional momentum, built on S2's vector) or the financing-data
>    prerequisite for the carry family.
>
> Deliverable: precommit + result + verdict docs under `docs/research/`. New code
> limited to a currency-strength decomposition utility + matched-null reuse; NO
> strategy, signal, entry/exit, or campaign code.

---

## Guardrails carried into the next sprint

- **No campaign of any number** (no CAMPAIGN_032; S2 is a factor-validation
  study, not a campaign).
- **Do not revive C1.** C1 is retired as a research target (kept as a control);
  no C1 re-tune, no "C1 on crosses with a new filter."
- **Do not naively add crosses to C016** (hidden re-tune; decompose to currencies).
- **Carry stays prerequisite-blocked** on real swap-rate ingest — not opened here.
- No strategy approved; `approved: []` stays empty; paper/demo/live blocked;
  `forex_bot.approval` fails closed.
- Local research-DB read is acceptable (read-only data analysis, no trading APIs,
  no broker credentials, no orders) — confirm scope with the user if uncertain.
- Pre-registration precedes any conditioned number; matched-null +
  multiple-comparison are mandatory (Stage-2 bar).
- Freeze stays intact; the sprint produces evidence and a verdict, nothing
  order-capable.

---

## Alternative (only if carry is prioritized over breadth)

If the next priority is the **carry** family instead of S2, the prerequisite is a
**data sprint** — ingest real OANDA financing/swap rates for the carry crosses
(AUD_JPY, NZD_JPY, EUR_JPY) — **not** a factor screen. Carry cannot be honestly
validated on the registry's *estimate* rates (that repeats C031's
financing-defeated failure on estimated costs). This remains a separate, later,
explicitly-scoped data sprint; S2 is the recommended default next step.

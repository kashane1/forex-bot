# Next Prompt — After Programme Synthesis

The cross-factor programme synthesis is complete. The S1–S5 shortlist is exhausted;
every effort to date is rejected, a failed replication, cost-defeated,
financing-defeated, or real-but-sub-cost-band (S4 cross RV — the one genuine
factor). The chosen next major direction is **Option A — financing/rate-data
ingestion enabling carry research**: carry (interest-rate differential) is the one
**genuinely new, untested mechanism**, data-blocked for the entire programme and now
nearly testable in-repo.

> The next sprint is a **data-ingestion / research-preparation sprint** — it builds
> the real rate/financing data layer and *designs* (does not run) the carry factor
> study. It is **NOT** a carry factor screen, **NOT** a factor validation, **NOT** a
> campaign, **NOT** a strategy.

---

## Recommended next sprint — financing/rate-data ingestion + carry research design

> Branch: `research-financing-rate-data-ingestion-001`
>
> **Build the real interest-rate / financing data layer for carry, validate it, and
> write the carry factor-validation design — then stop.** Run no carry screen, build
> no signal, fit no model, create no campaign, approve nothing.
>
> Read first:
> - `NEXT_MAJOR_DIRECTION_DECISION.md` — the decision + scope guard + pre-stated
>   carry success criteria.
> - `REMAINING_UNTESTED_MECHANISMS.md` §1–§2 — why carry/financing is the frontier.
> - `PROGRAMME_LESSONS_LEARNED.md` §4 — the financing wall (C031 ≈4× spread) and the
>   "never test carry on estimate rates" rule.
> - `src/forex_bot/research/cost_models/carry.py` — the existing two-legged carry
>   **estimate** model this sprint replaces with real rates.
> - `scripts/fetch_cross_asset_fred_features.py` + `CROSS_ASSET_FRED_INGEST_RUNBOOK.md`
>   — the **already-wired FRED ingest** path (credential-free, public data).
>
> The sprint MUST:
> 1. **Ingest real per-currency short-term interest rates (FRED, credential-free)**
>    for the 8 programme currencies (USD, EUR, GBP, JPY, AUD, NZD, CAD, CHF) over the
>    corpus window — policy / short-rate proxies sufficient to compute the
>    **interbank carry differential** for each cross. Reuse the FRED pipeline; do not
>    call any trading API.
> 2. **Construct and validate the real carry differential per cross** (base-leg rate
>    − quote-leg rate) as a new, lookahead-safe data object aligned to the existing
>    bars — replacing the registry's qualitative `conservative_bp_per_day`
>    *estimates*. Validate coverage, alignment, and sanity (sign, magnitude vs known
>    rate regimes). **Descriptive only — no signal.**
> 3. **Document the OANDA-financing follow-on as a SEPARATE, later, explicitly
>    user-authorized step.** Real *tradable* carry cost = OANDA's broker financing
>    (interbank + markup; the C031 ≈4× reality). That ingest needs credentials and is
>    a deliberate authorized action (mirroring the cross-population sprint) — flag it
>    as the **cost-gate prerequisite**, do not perform it here unless the user
>    explicitly authorizes.
> 4. **Write the carry factor-validation DESIGN** (a pre-registration *draft*, not a
>    frozen protocol to be executed): candidate carry construction on the cross carry
>    pairs (AUD_JPY, NZD_JPY, EUR_JPY; long high-yield vs low-yield), response/holding
>    framing, the matched-null design, and the **net-of-real-financing** cost gate
>    with the carry-crash (risk-off) stress slice. Mark it explicitly as *for a future
>    sprint*.
> 5. **Stop at data + design.** No carry response study, no null run, no verdict, no
>    campaign, no approval.
>
> Deliverable: ingested+validated rate/carry-differential data, a data-validation
> doc, and a carry-research design doc. New code limited to FRED ingest + a carry-
> differential builder + validation; **NO** carry signal, factor screen, entry/exit,
> or campaign code.

---

## Guardrails carried into the next sprint

- **No campaign of any number** (no CAMPAIGN_032); the carry work is a *future*
  factor-validation, not a campaign.
- **Data + design only** — no carry factor screen, no null run, no verdict, no
  train/validation/test.
- **Never evaluate carry on estimate rates** — real rate differential (FRED) is the
  economic signal; OANDA real financing (later, authorized) is the cost gate.
- **Credential-free for the FRED ingest**; the OANDA-financing ingest is a separate,
  explicitly user-authorized step (not performed without authorization).
- No strategy approved; `approved: []`; paper/demo/live blocked; `forex_bot.approval`
  fails closed.
- Freeze stays intact; the sprint produces data + a design, nothing order-capable.

## After that (context only — do not start)

The sprint *after* the data layer exists is the **carry factor-validation** (a
pre-registered Stage-1/2 study, verdict-producing, no campaign). Its three outcomes
were pre-stated in `NEXT_MAJOR_DIRECTION_DECISION.md`: a genuine net-of-financing
carry factor (a real first), or `FINANCING_DEFEATED` (closing the last in-repo
mechanism and justifying a deliberate Option-D archive or Option-B/C venue/market
pivot). Either way: a fresh sprint, fresh pre-registration, no campaign.

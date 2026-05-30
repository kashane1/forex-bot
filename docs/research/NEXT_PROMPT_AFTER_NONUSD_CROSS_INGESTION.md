# Next Prompt — After Non-USD Cross Ingestion Infrastructure

This sprint (`research-nonusd-cross-ingestion-and-cost-models-001`) added
the *capability* to ingest, validate, materialize, and cost-model non-USD
FX crosses. **No cross data has been ingested**, and no factor discovery,
front-gate screen, campaign, or strategy was created.

There are two candidate next sprints. **Pick the data sprint first** if no
cross M1 has been fetched (it is the hard prerequisite for everything
real); otherwise proceed to discovery planning.

---

## Option A (prerequisite) — credentialed cross M1 ingestion run

> Branch: `research-nonusd-cross-data-acquisition-001`
>
> Using the capability built in `...ingestion-and-cost-models-001`, perform
> the **practice-only, read-only** M1 ingestion of the four primary wave-1
> crosses (EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY), then materialize and
> validate them to the major-pair standard.
>
> - Use `scripts/ingest_oanda_m1_candles.py --crosses --execute-readonly-ingestion`
>   (practice creds only; live host refused; candle endpoint only).
> - Materialize with `scripts/materialize_m1_derived_timeframes.py --all-crosses`.
> - Validate with `scripts/validate_nonusd_cross_data.py --scope primary`
>   and record measured spread/coverage/session diagnostics.
> - Confirm provenance (fetch_batch_id/data_hash), missing-bar bounds, and
>   H4-derived-vs-native parity where native H4 exists.
>
> Hard rules: no strategy, no campaign, no front-gate screen, no approval;
> paper/demo/live stay blocked; do not touch the majors' data.

---

## Option B (recommended once data exists) — cross factor-discovery PLANNING

> Branch: `research-nonusd-cross-factor-discovery-planning-001`
>
> **Planning only — pre-campaign, pre-strategy, pre-screen.** Produce a
> design document that scopes (does NOT run) factor discovery on the
> ingested non-USD crosses, using the generalized multi-market front-gate
> framework (`MULTI_MARKET_FRONT_GATE_FRAMEWORK.md`).
>
> The plan must:
>
> 1. **Restate the standing constraints** — crosses add breadth, not cost
>    relief or history; broad undirected mining stays closed; revival needs
>    a genuine cost-aware external thesis, never a re-tune of a rejected
>    idea.
> 2. **Prioritize the two intended uses** the reviews named:
>    - **Independent replication** of the one genuine factor on this corpus
>      (C1: fade H4+H1+M15 bullish alignment → reverts down) on
>      non-collinear cross data via a *fresh pre-registered screen* to
>      settle the residual-USD question. This is replication, NOT a re-tune
>      of C1's cost-defeated USD-major result.
>    - **Breadth families** that were data-blocked on USD-only majors
>      (cross-sectional, carry, relative-value), framed cost-first.
>    - Do-not-revive list: every REJECTED campaign/lane (C022 pullback,
>      C025/026 Donchian ladder, C027 z-score, C028 RV spread, C029 range
>      bars, C031 TSMOM, H03/H16 non-time-bar, M1/HTF directional lane).
> 3. **Specify the cost-realism gate up front** — every candidate must pass
>    `cost_models` round-trip spread + two-legged carry net-of-cost before
>    it earns a single front-gate screen, exactly as the majors did.
> 4. **Define stop criteria** — what result would close the cross lane (as
>    the majors' lane closed on cost), so the sprint cannot drift into
>    open-ended mining.
>
> Deliverable: one planning document. **Do not** create a hypothesis,
> run a screen, build entry/exit logic, create a campaign, or approve
> anything. Freeze stays intact.

---

## Guardrails carried into either sprint

- Do not create any CAMPAIGN_03x or any campaign.
- Do not implement any strategy or entry/exit logic.
- Do not run train/validation/test evidence.
- Do not approve any strategy; paper/demo/live stay blocked.
- Do not revive a rejected idea as anything but a *fresh, independent,
  pre-registered* replication on genuinely new (cross) data.
- Use only existing read-only research patterns and practice credentials.

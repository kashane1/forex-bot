# Non-USD Cross Research Readiness

**Sprint:** `research-nonusd-cross-ingestion-and-cost-models-001` (Phase 6)
**Status:** infrastructure readiness assessment. No factor discovery, no
hypothesis, no front-gate screen, no campaign, no approval. Freeze intact.

## Summary

The infrastructure to **ingest, validate, materialize, and cost-model**
non-USD FX crosses to the same standard as the seven USD majors is now in
place and tested. **No cross data has been ingested yet** — that requires
a separate, explicitly-scoped credentialed M1 fetch. Future factor
discovery on crosses is *infrastructurally* possible but **not started and
not authorized** by this sprint.

## Which crosses are fully supported (capability)

All eight registered crosses are supported by every layer
(registry → ingestion allow-list → materialization → cost models →
validation/diagnostics):

| Cross | Tier | Quote | Pip | Registry | Ingest | Materialize | Cost model | Diagnostics |
|-------|------|-------|-----|:--------:|:------:|:-----------:|:----------:|:-----------:|
| EUR_GBP | primary | GBP | 0.0001 | ✅ | ✅ | ✅ | ✅ | ✅ |
| EUR_JPY | primary | JPY | 0.01 | ✅ | ✅ | ✅ | ✅ | ✅ |
| GBP_JPY | primary | JPY | 0.01 | ✅ | ✅ | ✅ | ✅ | ✅ |
| AUD_JPY | primary | JPY | 0.01 | ✅ | ✅ | ✅ | ✅ | ✅ |
| NZD_JPY | extended | JPY | 0.01 | ✅ | ✅ | ✅ | ✅ | ✅ |
| EUR_CHF | extended | CHF | 0.0001 | ✅ | ✅ | ✅ | ✅ | ✅ |
| GBP_CHF | extended | CHF | 0.0001 | ✅ | ✅ | ✅ | ✅ | ✅ |
| EUR_AUD | extended | AUD | 0.0001 | ✅ | ✅ | ✅ | ✅ | ✅ |

"Supported" = code path + tests exist. It does **not** mean data is
present (see below).

## Which remain blocked (and why)

Nothing is blocked at the *capability* level. The gating dependency is
**data + a go-ahead**, not code:

1. **No ingested data.** Live diagnostics confirm all eight crosses are
   `NOT_INGESTED` (0 rows). Until a credentialed practice-only M1 fetch is
   run, no measured spread/coverage/aggregation diagnostics exist — only
   registry-estimate cost profiles.
2. **No credentials in this environment.** The artifact secret scan and
   ingestion path both report no real OANDA credentials present, so this
   sprint deliberately added the *capability* without fetching.
3. **Live promotion remains hard-blocked** independent of crosses: no
   strategy is approved; paper/demo/live stay blocked; the financing
   live-blocker is permanent until a real (MODELED) financing series
   exists, which OANDA does not expose for crosses any more than majors.

## Known data-quality concerns (to confirm post-ingestion)

- **EUR_CHF 2015-01-15 SNB break** — a hard price discontinuity; the
  registry flags it and `cross_cost_profile` surfaces it. Any future study
  must window around it.
- **Same vendor / same ~6.4y window** — crosses add breadth, **not
  history**. Slow/regime/macro families stay underpowered.
- **Thin crosses (NZD_JPY, GBP_CHF)** — expect wider, less stable spreads
  and more missing minutes; the missing-bar + spread-percentile
  diagnostics will quantify this once data lands.
- **Volume is a tick-count proxy** — crosses do not unlock a true
  tick/L2 microstructure lane.

## Known cost concerns

- **Crosses are wider than the majors**, not cheaper. The feasibility
  review's verdict stands: crosses are a **breadth/replication** expansion,
  **not** a cost fix. The cost models encode this honestly — spread bands
  are near-major→wide, and `spread_cost_r` is round-trip by default.
- **Carry is two-legged.** `CrossCarryModel` uses explicit per-cross
  conservative bp/day (not the majors' fallback) and works in R so the
  quote currency cancels; carry crosses (AUD_JPY, NZD_JPY, EUR_JPY,
  GBP_JPY) have financing as a first-order driver.
- **Quote≠USD.** Converting any cross debit/risk to USD needs a separate
  quote/USD rate; the models refuse to fabricate one.

## Is future factor discovery now possible?

**Infrastructurally, yes — once data is ingested.** The lab can ingest,
validate, materialize, and cost-model crosses on the same standard as the
majors, which is exactly what the multi-market front-gate framework
requires before a market may take the gate. The intended first research
uses (per the viability/feasibility reviews) are:

- **Independent replication** of genuine factors (e.g. C1) on
  non-collinear data via a *fresh pre-registered screen* (NOT a re-tune).
- **Breadth families** (cross-sectional, carry, relative-value) that were
  data-blocked on the USD-only majors.

**This sprint does none of that.** It creates no hypothesis, no factor, no
front-gate screen, and no campaign. Discovery is the *next* sprint's
pre-work, and only after a credentialed ingestion run.

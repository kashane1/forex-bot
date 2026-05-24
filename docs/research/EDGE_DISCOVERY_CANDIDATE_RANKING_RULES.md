# Edge Discovery — Candidate Ranking Rules

**Sprint:** `research-edge-discovery-lab-001` · Phase 4
**Date:** 2026-05-24
**Status:** Decision rules for what a lab finding has to look like
before a human should consider drafting a formal campaign pre-commit
for it. **The lab itself never graduates anything.** A human reads
this file, looks at the lab's evidence packet, and decides.

These rules operationalize the ten reusable lessons in
`FAILED_CAMPAIGN_META_ANALYSIS_001.md`. They are deliberately
conservative — the cheapest mistake a campaign can make is to be
spawned for a candidate that the lab already knew was thin.

---

## 1. Minimum exploratory evidence before campaign promotion

A lab finding may be **proposed** for promotion to a formal pre-commit
only if every one of these is true. Missing items kill the proposal,
not raise a yellow flag.

1. **Repeatability.** Two independent re-runs of the same lab script
   against the same input bytes produce byte-identical (or numerical-
   noise-only) summary JSON. The lab's SHA-256 provenance fields are
   the proof; both runs are linked in the proposal.

2. **Post-cost positive in a non-trivial slice.** Some slice (pair,
   event class, session, regime bin) shows a post-cost mean log-return
   > 0 with **n ≥ 30** observations in that slice. *Aggregate* post-
   cost positivity is not enough — Lesson 3.

3. **Materially above the random-entry null.** On that same slice, the
   post-cost mean exceeds the sample-matched random-entry null mean by
   at least `+1.0` null stds (the lab's `slightly_above_null` band) —
   and preferably `+2.0` stds (`materially_above_null`). Below 1.0
   null stds is `within_null` and disqualifies the proposal. Lesson 1.

4. **Per-trade pre-cost edge clears cost-per-trade with margin.** The
   slice's pre-cost mean log-return per trade is greater than the
   cost-per-trade by a factor of at least 2.0. (E.g. on EUR_USD where
   cost-per-trade ≈ `+0.000173` log-units, the slice's pre-cost mean
   must be ≥ `+0.00035` per trade.) Lesson 2 — the turnover-sensitivity
   matrix is the artifact.

5. **Not single-pair-concentrated unless declared.** Either the slice's
   effect spans ≥ 2 pairs with consistent sign, or the proposal is
   explicitly written as a *single-pair* candidate (one strategy
   version, one pair, ≤ 50% of the universe's risk budget). Lesson 3.

6. **Not validation-only.** If the effect is constructed from a
   validation-style window, an independent second window (or a hold-
   out the lab did not touch) must show the same sign at the same
   slice; otherwise the proposal is parked as "validation-only —
   needs second-window check before promotion." Lesson 4.

7. **Honest infra classification.** If any slice has *zero matched
   trades* because the session / data filter blocked the trigger bar,
   the proposal lists it explicitly (Lesson 5 / 6). A zero-trade slice
   is **not** a "no signal" finding — it's a "did not test."

## 2. Red flags that stop an idea early

A single red flag from this list ends the proposal at the lab; the
human writes a brief note ("killed by red flag X") and moves on.

- **R-1 — Cost-dominated.** Post-cost mean / pre-cost mean < 0.20.
  More trades make this strictly worse (Lesson 2).
- **R-2 — Inside the null band.** `band == within_null` on the lab's
  null comparison. Lesson 1.
- **R-3 — Single-pair effect dressed up as a universe effect.** Top
  pair explains > 70% of the aggregate effect and the proposal
  doesn't acknowledge it. Lesson 3.
- **R-4 — Validation-only with no second-window check.** Lesson 4.
- **R-5 — Dominant event class with opposite-sign minority.** One
  event class explains > 60% of trades AND has opposite sign to
  another class with material n ≥ 30. Lesson 6.
- **R-6 — Zero-trade slice on the dominant filter.** The proposal's
  filter blocks the most important event class entirely (the
  CAMPAIGN_014 FOMC pattern from the brief). Lesson 6.
- **R-7 — One-rule rescue of an artifact-rejected family.** The
  proposal is a single-rule tweak on top of an already-rejected
  CAMPAIGN_001–009 family AND the rule has no independent positive
  evidence elsewhere in the lab. Lesson 7.
- **R-8 — Looks like a regime drift, not an edge.** The candidate's
  best slice's leading pair matches the leading pair on the random-
  entry baseline for the same window — that's pair-drift overlap, not
  a strategy effect. Lesson 3 + Lesson 10.

## 3. Comparing against the CAMPAIGN_011 / CAMPAIGN_005 null

The sprint brief mentions CAMPAIGN_011 as the random-entry / null
baseline. The artifact-backed equivalent on this branch is
**CAMPAIGN_005, Benchmark 3** — random-entry, matched frequency, 20
seeds, 30-bar hold, real spreads. Per-pair values (mean expectancy R):

| pair | random R |
|---|---:|
| EUR_USD | −0.183 |
| GBP_USD | −0.107 |
| USD_JPY | −0.122 |
| AUD_USD | −0.147 |
| USD_CAD | −0.008 |
| USD_CHF | −0.004 |
| **universe mean** | **−0.095** |

A lab study comparing to the null **must**:

- compute its own sample-matched random null on the actual frame and
  window it used (via `research.edge_discovery.null.random_null_baseline`);
  the universe-mean `−0.095 R` is the *cite*, the per-study null is
  the *test*;
- report the gap in null stds (the descriptive band), not a p-value;
- when CAMPAIGN_010 / 011 actually land as committed artifacts on
  this branch, re-anchor the cite to those campaigns and re-validate
  this section.

If a study's per-study null is collapsed (one seed, or all seeds
produce identical means), the lab reports `band: null_collapsed` and
the proposal is parked until the study is rerun with a non-degenerate
seed set.

## 4. How to penalize turnover amplification

Concretely, every proposal must include the turnover sensitivity
table from `study_turnover_cost.py` (or its equivalent), with the
candidate's measured per-trade pre-cost edge plotted on it. If the
candidate's per-trade pre-cost edge sits in a row where the post-cost
cumulative is negative *at the candidate's expected trade count*, the
proposal is downgraded:

- `pre-cost edge per trade < cost-per-trade`: **R-1 cost-dominated**
  (stop).
- `cost-per-trade ≤ pre-cost edge < 2.0 × cost-per-trade`:
  proposal is parked as "cost-marginal — needs a 2× cost-stress
  rerun before promotion."
- `pre-cost edge ≥ 2.0 × cost-per-trade`: passes the turnover gate;
  proposal continues.

The cost-stress factor of 2.0 mirrors the cost regimes already used
in CAMPAIGN_002–009 (`base`, `stress_15x`, `stress_2x`) — a candidate
that survives the lab's 2× turnover gate has at least the same
safety margin those campaigns required of themselves.

## 5. "Interesting but not tradable yet" handling

Some lab findings are real and worth recording but cannot be
graduated. The lab's standard disposition for these is to write a
short summary into `docs/research/FUTURE_RESEARCH_BACKLOG.md` as a
new dated entry, with:

- the lab evidence packet (JSON + MD links),
- which graduation rule fails (e.g. "passes 1, 2, 3, 4, 5; fails 6 —
  validation-only, no second window available yet"),
- what would unblock it (e.g. "rerun against 2024–2026 hydrated H4
  store with the same script, no parameter change").

The candidate is then **not** scheduled for a campaign and is not
listed under `STRATEGY_STATUS.md`. It stays in the backlog until a
human revisits.

## 6. Recommended next 3–5 lab studies (ranked)

These are *lab studies*, not campaigns. None of them is authorized
to produce a strategy verdict. Ranking is rough priority: do 1 before
2 before 3, because each later study consumes / verifies the previous.

1. **Real-event-window study (NFP / FOMC / CPI 2020–2026, six majors).**
   *Hypothesis:* the brief's CAMPAIGN_014 narrative (NFP dominates and
   loses; FOMC has zero trades because the session filter blocks the
   trigger bar) reproduces on the real fixture. *Pass condition:* the
   study output shows the dominance, the zero-trade-class, and a per-
   class null gap on each of the six majors; the lab's MD note records
   the result without proposing a strategy. *Why first:* it's the
   most directly informed by the meta-analysis and the cheapest to
   run once an event fixture exists.

2. **Real-data turnover-cost validation on each rejected campaign's
   per-trade edge.** *Hypothesis:* the post-cost matrix correctly
   re-explains why CAMPAIGN_002 / 003 / 004 failed by per-trade
   pre-cost edge and trade-count alone. *Pass condition:* the
   per-trade pre-cost edge implied by each campaign's summary cleanly
   places that campaign in the "cost-dominated" or "cost-marginal"
   row of the turnover matrix at its actual trade count. *Why
   second:* it grounds the lab's cost arithmetic in artifact-backed
   evidence so the cost-stress gate (§4) is trusted.

3. **Pair-level, regime-conditioned forward-return profile, six
   majors.** *Hypothesis:* some (pair, regime) cell is materially
   above the random-entry null on a non-trivial n. *Pass condition:*
   at least one (pair, regime) cell satisfies §1.2–§1.5; one cell
   parked as "validation-only" is fine. *Why third:* it produces the
   broadest descriptive map the lab can offer for proposing real
   candidates — without itself being one.

4. **(Optional) Day-of-week × time-of-day cross study.** *Hypothesis:*
   per-(weekday, hour) bins show diurnal+weekly structure beyond what
   the random null produces. *Why optional:* low expected value
   relative to 1–3; mostly insurance against missing a regime effect.

5. **(Optional) Bias-of-fixtures audit.** *Hypothesis:* the
   committed synthetic fixtures don't accidentally bias any future
   study (a sanity rerun of 1–4 on the synthetic fixture should land
   in `within_null` on every slice). *Why optional but recommended:*
   keeps the lab from drifting onto its own fixture characteristics.

Items 1–3 are the package the sprint summary highlights for the next
sprint. They graduate one lab finding only if all six §1 gates and
zero §2 red flags hold; otherwise they sharpen the lab itself.

# Next Research Lane — After USD_JPY Microstructure Closeout

**Date:** 2026-05-28 · **Type:** options analysis + recommendation. Approves nothing,
executes nothing, creates no campaign, implements no strategy, claims no edge.

> The full C022/C023/USD_JPY microstructure thread is closed at both the entry and
> management layers (see
> [`C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md`](C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md)).
> This doc compares **genuinely new** next lanes. **None is a C022-style entry variant**,
> and none reopens the closed family. Nothing here is precommitted; the chosen lane is a
> direction only and must be independently pre-committed before any execution.

## What "genuinely new" must mean here

Across C010/C015–C017/C020–C022 plus the USD_JPY microstructure entry + management
diagnostics, internally-invented indicator/confluence/reclaim/stop combinations have
**repeatedly** failed, and post-entry descriptive signals proved non-actionable. The
recurring lesson: the edge problem is not solved by another internally-designed
technical combination. A new lane must therefore either (a) bring an **external** source
of edge, (b) **map** behavior rather than assert a strategy, or (c) change the **horizon
/ mechanism** entirely (macro/carry) — not re-mine price-pattern entries.

## Scoring key (1–5; 5 = best)

- **Distinct** — structural distinctness from everything already tried.
- **Evidence** — support from current repo evidence (not threshold-mined).
- **Data** — availability of required data locally / read-only.
- **Sample** — expected usable sample size.
- **Simplicity** — implementation simplicity (5 = simplest).
- **Overfit-resist** — resistance to overfitting (5 = most resistant).
- **P(actionable)** — probability of producing an *actionable* future precommit.
- **Demo-help** — whether it moves eventual demo readiness forward (honestly).

---

## Lane 1 — Stop strategy research temporarily (infra / evaluation / process)

Pause strategy search; invest in infrastructure, evaluation rigor, and process quality.

- **Reason.** Many failed strategies and no edge; the process, not the next indicator, may
  be the highest-value investment.
- **Risk.** No new edge discovery; can become indefinite deferral.
- **Distinct 5 · Evidence 5 · Data 5 · Sample n/a · Simplicity 4 · Overfit-resist 5 · P(actionable) 2 · Demo-help 3**
- **Priority:** medium. The honest null; always defensible under the freeze, but does not
  itself search for the new edge the thread closeout says is required.

## Lane 2 — External thesis sourcing sprint

Research public / institutional / academic FX edges **before** coding anything.

- **Reason.** Avoid inventing yet another internal indicator combination; import a
  hypothesis with outside priors. Directly answers the thread's core lesson.
- **Risk.** Quality/credibility of sources; many public "edges" are stale or unrobust.
- **Distinct 5 · Evidence 4 · Data 4 (literature/notes, user-provided) · Sample n/a · Simplicity 4 · Overfit-resist 4 · P(actionable) 4 · Demo-help 3**
- **Priority:** **high.** It is the cheapest way to change the *source* of edge rather
  than re-mining price. Pairs naturally with Lane 4 (map the repo's own behavior to
  pre-screen any sourced thesis).

## Lane 3 — Macro / calendar / event-driven USD_JPY lane

BOJ / FOMC / CPI / NFP / rate-decision / event windows.

- **Reason.** Structurally different from technical microstructure; a real exogenous
  driver (especially for USD_JPY, a rates/intervention-sensitive pair).
- **Risk.** Sample size (few high-impact events), event-fixture quality (the repo's
  CAMPAIGN_014 calendar lane has known caveats), look-ahead hazards around releases.
- **Distinct 4 · Evidence 2 · Data 2 (needs reliable calendar) · Sample 2 · Simplicity 2 · Overfit-resist 2 · P(actionable) 3 · Demo-help 2**
- **Priority:** medium-low. Genuinely different but gated on calendar-data quality and
  small event samples; better attempted *after* sourcing (Lane 2) sharpens the hypothesis.

## Lane 4 — Session / time-of-day statistical atlas (map, not strategy)

Map USD_JPY (and optionally all pairs) by session, spread, volatility, drift, reversal,
trend persistence — a descriptive atlas, not a strategy.

- **Reason.** Context features (hour/volatility/cost) showed the only weak separation in
  C022; a rigorous atlas turns vague context into a documented prior and a screening tool
  for any future thesis.
- **Risk.** May be descriptive only (no tradable edge) — but that is acceptable as a
  *map*, not a strategy, provided it is not retro-fit into one.
- **Distinct 4 · Evidence 4 · Data 5 (M1/M15/H1 local) · Sample 5 · Simplicity 4 · Overfit-resist 4 · P(actionable) 3 · Demo-help 4**
- **Priority:** **high (as a companion to Lane 2).** Cheap, fully-resourced, read-only,
  and it builds reusable infrastructure (a behavior map) that pre-screens externally
  sourced theses before any coding.

## Lane 5 — Carry / rates / financing-aware research

Structurally different, slower horizon (overnight financing, rate differentials).

- **Reason.** A real, economically-grounded driver distinct from intraday price patterns;
  the repo already has a financing/overlay toolchain.
- **Risk.** Data/model complexity; slow horizon means small independent-sample counts;
  prior financing work was diagnostic, not edge-finding.
- **Distinct 5 · Evidence 3 · Data 3 · Sample 2 · Simplicity 2 · Overfit-resist 3 · P(actionable) 3 · Demo-help 2**
- **Priority:** medium. Genuinely new mechanism but heavier; better motivated by a
  sourced thesis (Lane 2) than pursued cold.

## Lane 6 — Market-regime labeling / supervised diagnostics

Build labels for trend / chop / volatility / session / macro conditions (not a strategy
yet).

- **Reason.** Reusable regime labels could condition any future thesis and explain past
  failures.
- **Risk.** Easy to overfit if labels are tuned to outcomes or used carelessly as
  features; can drift into the same null with more degrees of freedom.
- **Distinct 3 · Evidence 3 · Data 5 · Sample 5 · Simplicity 3 · Overfit-resist 2 · P(actionable) 3 · Demo-help 3**
- **Priority:** medium. Useful infrastructure but the highest overfit hazard of the
  "mapping" lanes; fold the safe parts into Lane 4 rather than running standalone.

---

## Summary scoring table

| Lane | Distinct | Evidence | Data | Sample | Simplicity | Overfit-resist | P(actionable) | Demo-help | Priority |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| 1 · Pause / infra | 5 | 5 | 5 | — | 4 | 5 | 2 | 3 | med (null) |
| **2 · External thesis sourcing** | **5** | **4** | **4** | — | **4** | **4** | **4** | **3** | **high** |
| 3 · Macro / calendar / event | 4 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | med-low |
| **4 · Session/time-of-day atlas** | **4** | **4** | **5** | **5** | **4** | **4** | **3** | **4** | **high (companion)** |
| 5 · Carry / rates / financing | 5 | 3 | 3 | 2 | 2 | 3 | 3 | 2 | med |
| 6 · Regime labeling | 3 | 3 | 5 | 5 | 3 | 2 | 3 | 3 | med |

## Recommendation

**Recommended next lane: `external-thesis-sourcing-and-session-atlas-001` (Lane 2 + Lane 4 combined).**

- **Do not code another entry strategy yet.** Every internally-invented technical entry
  in this repo has failed; the thread closeout's central lesson is that a *new source* of
  edge is required, not another combination.
- **Lane 2 (external thesis sourcing)** changes the *source* of hypotheses — survey
  public / institutional / academic FX edges (and any user-provided notes) and shortlist
  candidates with outside priors.
- **Lane 4 (session/time-of-day atlas)** is the cheap, fully-resourced, read-only
  companion that *maps* USD_JPY (and optionally all pairs) behavior so each sourced thesis
  can be pre-screened against the repo's own data before any coding.
- Together they are diagnostic/research-only, low overfit risk, fully data-available, and
  the most likely to produce a *genuinely new, pre-committable* hypothesis — without
  re-mining the closed family.

**Acceptable alternative:** Lane 1 (pause strategy research, invest in infra/process) if
the preference is to stop hypothesis search entirely for now. Lanes 3/5/6 should follow a
sourced thesis, not precede it.

## Hard rules upheld

No C022/C023/USD_JPY microstructure mining; no CAMPAIGN_024; no C023 execution; no
strategy implementation; no campaign; no approval; no paper/demo/live. The selected lane
is a research direction only and must be independently pre-committed before any execution.

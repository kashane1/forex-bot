# Edge Discovery Lab — Sprint 001 Results

**Sprint id:** `research-edge-discovery-lab-001` · Phase 4
**Date:** 2026-05-24
**Status:** Exploratory results — **no strategy approved, no campaign
verdict changed.** This is process output, not edge evidence.

---

## 1. What the lab now has

The sprint built and exercised a four-component exploratory rig:

- `research/edge_discovery/loaders.py` — CSV loaders with SHA-256
  provenance for candles and event fixtures.
- `research/edge_discovery/windows.py` — fixed-window signed
  forward-return computation with explicit no-look-ahead semantics.
- `research/edge_discovery/costs.py` — round-trip spread + slip cost
  overlay and financing stress (sourced from
  `forex_bot.financing.CONSERVATIVE_BP_PER_DAY`), all subtractive.
- `research/edge_discovery/null.py` — seeded random-entry null with
  descriptive band comparison (`within_null`, `slightly_above_null`,
  `materially_above_null`, …). Not a significance test.
- `research/edge_discovery/report.py` — JSON + Markdown reporter with
  a verdict-word ban: the writer refuses to emit a body containing
  `APPROVE`, `GO`, `PROMOTE`.

Four illustrative studies ship as runnable scripts plus committed
JSON + Markdown outputs:

| study | input | output | exercises |
|---|---|---|---|
| `study_event_window.py` | committed synthetic NFP/FOMC/CPI fixture + H4 candle fixture | `studies/outputs/study_event_window.{json,md}` | event-class breakdown, dominance share, zero-trade-class flag, null comparison — the CAMPAIGN_014 narrative pattern |
| `study_turnover_cost.py` | analytical sweep (no candle input) | `studies/outputs/study_turnover_cost.{json,md}` | post-cost matrix over (pre-cost edge × trade count); cost-share-of-mean — the CAMPAIGN_012/013 narrative pattern |
| `study_pair_baseline.py` | committed CAMPAIGN_002/003/004/005/007/008/009 per-pair numbers | `studies/outputs/study_pair_baseline.{json,md}` | per-pair lift over the artifact-backed random-entry null; test-window vs validation-only above-null split |
| `study_session.py` | committed H4 candle fixture | `studies/outputs/study_session.{json,md}` | per-UTC-hour forward-return breakdown — capability check for time-of-day studies |

All four artifacts are deliberately committed so a reviewer can read
the lab output without running anything; re-running each script
overwrites with byte-identical content (modulo fixture-hash drift).

## 2. What the studies say (descriptive only)

### Event-window study (synthetic)

Run against the 6-event synthetic fixture (NFP / FOMC / CPI, two each),
the post-cost LONG mean over a 6-bar forward window is `−0.000198`
log-units, within the null's noise band (gap `−0.10` null stds). The
per-class breakdown shows the trivial example of class concentration
(33% each) and a per-class sign split that exists only because the
fixture is small. **No edge conclusion is possible from this run.**
The point is to demonstrate that the lab correctly produces:

- per-class `n` (the dominance-share denominator),
- per-class pre-cost and post-cost mean,
- a zero-trade-classes list (empty here because the synthetic events
  all hit live bars — but the field is populated when a real
  session/data filter blocks a class, e.g. the CAMPAIGN_014 FOMC
  behavior),
- a descriptive null-band on the aggregate, and
- an inputs block with SHA-256s so a re-run is reproducible.

A real-fixture run (real NFP / FOMC dates + a hydrated H4 store)
plugs into the same script with two CLI-style path overrides; no
other code changes.

### Turnover-cost sensitivity (analytical)

The committed cost-per-trade for an EUR_USD-shaped midprice with
spread 1.5 pip + 2 × 0.2 pip slip is `+0.000173` log-units round-trip.
Reading the matrix:

- For a **−0.0001 per-trade pre-cost edge** (roughly the order of
  magnitude many CAMPAIGN_002/003/004 H4 backtests showed on a per-
  trade basis), the cumulative post-cost return at n=500 trades is
  `−0.136` log-units, dominated by the `+0.086` cost burden. More
  trades make this strictly worse.
- For a **0 per-trade pre-cost edge**, the post-cost return at any
  positive n is purely the negative of the cost burden — by n=2500
  that is `−0.432` log-units. Cost-share of pre-cost cumulative is
  undefined (`—`), which the lab marks as `+inf` / `—` in the matrix
  — that label is itself the alarm.
- For a **+0.00025 per-trade pre-cost edge** (well above the cost-per-
  trade), the post-cost return scales linearly with `n` and cost
  share is `~0.69`. This is the only column where increasing turnover
  improves the post-cost outcome.

That single matrix is sufficient to encode Lesson 2 of the meta-
analysis: turnover only helps a candidate whose **per-trade pre-cost
edge clearly exceeds the cost-per-trade**.

### Pair-level baseline (artifact-backed)

Reading the per-pair table:

| pair | random R | best test-window gap | best campaign | n test-above-null | n val-only-above-null |
|---|---:|---:|---|---:|---:|
| EUR_USD | −0.183 | +0.440 (CAMPAIGN_002 / 003 +0.257) | breakout/trend H4 | 2 | 2 |
| GBP_USD | −0.107 | +0.079 (CAMPAIGN_002 / 003 −0.028) | breakout/trend H4 | 2 | 2 |
| USD_JPY | −0.122 | +0.122 (CAMPAIGN_004 −0.000) | volatility_breakout | 3 | 3 |
| AUD_USD | −0.147 | +0.110 (CAMPAIGN_002 / 003 −0.037) | breakout/trend H4 | 2 | 2 |
| USD_CAD | −0.008 | (no test-window cell ≥ +0.05) | — | 0 | 1 |
| USD_CHF | −0.004 | (no test-window cell ≥ +0.05) | — | 0 | 2 |

Honest readings:

- **EUR_USD** is the only pair with a clearly large test-window gap
  (+0.440 R) — but that gap comes from a campaign that was
  **rejected overall**: CAMPAIGN_002 / 003 still failed their pre-
  committed gates despite EUR_USD's per-pair lift. This is the "pair
  concentration" pattern of Lesson 3 — celebrate carefully.
- **USD_JPY**'s "n test-above-null = 3" is real but tiny in size
  (~+0.12 R gap). Each cell hovers near zero (−0.002, −0.000, +0.000
  expectancy) which is barely above the random-entry −0.122 R floor;
  this is *less-bad*, not *good*. A candidate that proposes a JPY-
  pair edge needs explicit fresh evidence; this table is not a
  green-light.
- **USD_CAD** and **USD_CHF** have effectively zero random-entry
  baseline already (very small `random R`), so they are also the
  pairs where small cost shifts move them into negative territory
  most easily. Their "test-above-null" count is 0; their "val-only-
  above-null" count is non-zero only because of CAMPAIGN_008 / 009 —
  i.e. the validation-only pattern, which the meta-analysis Lesson
  4 says is the highest-overfit-risk signal in the archive.

The lab does **not** translate any of these readings into a strategy.
They are inputs to a human deciding *where to point the next lab
study*, not where to point a new campaign.

### Session / time-of-day (synthetic)

Per-UTC-hour post-cost means cluster between `−0.00018` and
`−0.00039`, all within ~0.02 null stds of the aggregate null. The
synthetic fixture's hour bins are nearly identical because the data
is geometric Brownian motion with no diurnal pattern — exactly what
the synthetic *should* show, and a useful "this study did not invent
an effect" sanity test for the rig itself. A real-data rerun against
the hydrated H4 store would surface any actual session character.

## 3. What this sprint did **not** prove

A non-exhaustive list, to keep the lab honest:

- It did not measure any real NFP / FOMC / CPI behavior. The repo
  has no committed event fixture; the synthetic events are
  illustrative.
- It did not load or analyze a hydrated H4 OANDA store. The
  committed candle fixture is 480 synthetic H4 bars.
- It did not change a single campaign verdict. CAMPAIGN_002–009
  remain at their existing verdicts; the approved-strategy registry
  is still empty; the freeze gate still passes.
- It did not approve, promote, or recommend any strategy. No
  pre-commit was drafted; no campaign was scaffolded.
- It did not find an edge. Finding an edge is not the lab's job —
  the lab's job is to make it cheap to look.

## 4. What the sprint **did** prove

A small list, equally honest:

- A lab study can be written, run, and reported (JSON + MD) in
  ~50–150 lines of Python on top of the new utility module — far
  below the cost of scaffolding a full strategy + pre-commit +
  walk-forward campaign.
- The reporter's verdict-word ban actually fires (see
  `tests/research/edge_discovery/test_report.py::test_write_study_report_rejects_verdict_words`),
  which means an accidental "this PASSes the gate" sentence in a
  lab output is blocked at write time rather than at review time.
- The import-isolation rails actually fire too (see
  `tests/research/edge_discovery/test_isolation.py`), so the lab
  cannot silently drift into the broker or loop modules.
- The same script that runs on synthetic fixtures runs unchanged
  against real CSV inputs — this is the property the sprint brief
  was asking for ("test many signal ideas cheaply before turning any
  one idea into a full formal campaign").

## 5. Next-3 lab studies to run when real data lands

Recorded here for the next researcher, not authorized for this
sprint:

1. **Event-window with real NFP / FOMC / CPI 2018–2026** on each of
   the six majors. Reports per-class dominance, zero-trade-class
   slices, and per-class null gap. **Direct test of the
   CAMPAIGN_014 narrative.** No new pre-commit until the lab output
   shows a per-class slice that is materially above the null on n ≥
   30 events and not driven by one class.

2. **Session-of-day on the hydrated H4 store** for each pair. With
   ~9.9k H4 bars per pair, per-hour `n` is ~1.7k — enough for
   meaningful per-session bands. Surfaces any session character that
   the synthetic could not.

3. **Pair-level forward-return profile, regime-conditioned.** Take
   the same null baseline computation, but condition entries on a
   coarse regime label (efficiency ratio quartile, ADX quartile).
   This is the "richer regime diagnostic" of
   `FUTURE_RESEARCH_BACKLOG.md` item 4, but pre-stage only — no
   strategy attached, just a regime-by-pair effect map for human
   review.

If item 1 produces a per-event-class slice that materially clears
the null **and** survives a turnover/cost sensitivity check
(Lesson 2) **and** is not pair-concentrated (Lesson 3), it would be
the first candidate the lab could honestly hand to the formal
campaign machinery. The ranking rules in
`EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md` make this graduation
test explicit.

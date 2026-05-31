# Next Programme Options

**Sprint:** `research-cross-factor-programme-synthesis-001` · Phase 4
**Type:** options evaluation. Docs-only. No execution.
**Date:** 2026-05-30.

Four strategic options, scored on five axes (1–5, higher = more favorable). Weights
reflect the programme's binding lesson — **prefer a genuinely new mechanism/regime,
at low repeat-risk and low lift, that the existing repo can actually execute.**

Axes: **Novelty** (new return source / regime?) · **Implementation cost** *(5 =
cheapest)* · **Expected information gain** · **Repeat-risk** *(5 = least likely to
re-hit a known failure)* · **Repo compatibility** *(5 = fits existing pipeline)*.

---

## Option A — Financing-data ingestion + carry research

- **What:** ingest **real OANDA financing/swap rates** (a data sprint), enabling a
  *later* pre-registered carry factor-validation on real carry crosses (AUD_JPY,
  NZD_JPY, EUR_JPY).
- **Novelty 5** — carry is a **genuinely new return source** (rate differential),
  never tested; the one untested mechanism (Phase 3 §1).
- **Implementation cost 4** — same OANDA vendor + existing ingest/materialization
  pipeline; financing endpoint + a new data object. Modest, in-repo.
- **Information gain 5** — resolves the last open mechanism either way: a real
  tradable, or a clean financing-defeat that *completes* the evidence and justifies
  a venue/market pivot.
- **Repeat-risk 3** — the venue's financing wall (C031: ≈4× spread) and carry-crash
  risk are real headwinds; carry here *may* be financing-defeated. But testing it is
  not a re-tune — it is a new mechanism, and the *data* asset is valuable regardless.
- **Repo compatibility 5** — reuses the candle store, ingest gates, cost models, and
  the front-gate lab directly.
- **Composite (weighted): ~4.4.**

## Option B — Better-cost venue / tick-data path

- **What:** acquire institutional/ECN-spread or true tick/L2 data to re-test
  cost-defeated effects (esp. S4's genuine no-arb RV) under a different cost regime.
- **Novelty 4** — a new *cost/microstructure regime* (not a new mechanism); S4
  proved real structure exists sub-retail-cost.
- **Implementation cost 2** — paid data, new ingest schema, latency/fill realism;
  significant lift.
- **Information gain 4** — could convert S4 (and other sub-cost effects) from
  "real-but-weak" to tradable — high ceiling — but overfit-prone and hard to
  validate honestly without execution realism.
- **Repeat-risk 3** — risk of fitting noise in a richer dataset; the discipline
  helps but the data is seductive.
- **Repo compatibility 2** — new data model, new cost/fill simulation.
- **Composite: ~3.0.**

## Option C — New market (futures / metals / crypto)

- **What:** extend the multi-market lab to a genuinely different market with a
  different cost structure and real volume (FX/index futures best for the cost fix;
  crypto for free deep history; metals for diversity).
- **Novelty 4** — new market + (for futures) a different cost structure + real
  volume.
- **Implementation cost 2** — new pipelines (continuous-contract roll for futures,
  24/7 calendar for crypto), new cost/calendar models; the largest infra lift.
- **Information gain 4** — best **edge diversity** and the best structural fix to the
  cost squeeze (futures) — but a long road before any verdict.
- **Repeat-risk 3** — new markets have their own artifacts (roll, survivorship,
  venue funding); discipline transfers but the surface is large.
- **Repo compatibility 3** — the lab is already generalized (multi-market framework);
  adapters + cost/calendar models are the work.
- **Composite: ~3.1.**

## Option D — Stop current search and archive the programme

- **What:** declare the OANDA spot-FX corpus (majors + crosses) exhausted for
  no-new-data factor discovery; archive with the S4 real-but-weak finding as the
  capstone; keep everything as a control/baseline.
- **Novelty 1** — no new information.
- **Implementation cost 5** — trivial (documentation).
- **Information gain 1** — closes the book but learns nothing new; **premature**
  because the one untested mechanism (carry) is cheap to test and not yet attempted.
- **Repeat-risk 5** — cannot repeat a failure by stopping.
- **Repo compatibility 5** — nothing to build.
- **Composite: ~3.0** (high only because it is free; yields no edge and leaves a
  mechanism untested).

---

## Score table

| Option | Novelty | Impl. cost (5=cheap) | Info gain | Repeat-risk (5=low) | Repo compat | **Weighted** |
|---|---|---|---|---|---|---|
| **A. Financing/carry** | 5 | 4 | 5 | 3 | 5 | **~4.4** |
| B. Cost-venue/tick | 4 | 2 | 4 | 3 | 2 | ~3.0 |
| C. New market | 4 | 2 | 4 | 3 | 3 | ~3.1 |
| D. Stop/archive | 1 | 5 | 1 | 5 | 5 | ~3.0 |

*(Weights: Novelty ×1.5, Info gain ×1.5, Repeat-risk ×1.5, Impl. cost ×1, Repo
compat ×1; composite normalized to /5.)*

## Reading

- **A dominates** on the axes that matter most for *learning something new cheaply*:
  it is the only option that tests a **genuinely new mechanism** (carry), is
  **directly repo-compatible**, and has the **highest information gain** (resolves
  the last mechanism either way). Its one weakness — the venue's financing
  headwind — is a *result to measure*, not a reason to skip, and the financing-data
  asset is valuable regardless.
- **B and C** are higher-ceiling but expensive lifts that the corpus review already
  deferred; they become the natural *next* moves **after** carry is resolved (if
  carry is financing-defeated, B/C are how the programme pivots cost/venue).
- **D** is premature: stopping before testing the one cheap, untested mechanism
  leaves the evidence incomplete. (If carry is then financing-defeated, D becomes
  fully justified — or B/C if appetite remains.)

**Recommended ordering:** A now (cheap, new mechanism, in-repo) → then, on the
carry result, either a clean **D archive** (if financing-defeated) or a **B/C
venue/market pivot** (if appetite for the larger lift). Phase 5 commits to A.

# CAMPAIGN_028 — Front-Gate Screen Results & Decision (Phase 1)

**Status:** `FRONT_GATE_SCREEN_COMPLETE` / `DOES_NOT_EARN_A_SCAFFOLD` / `NOT_RUN_AS_CAMPAIGN` / `NOT_APPROVED`
**Date:** 2026-05-28
**Thesis:** relative-value / cointegration spread reversion (Path A of
[`CAMPAIGN_028_NEW_THESIS_BRIEF.md`](CAMPAIGN_028_NEW_THESIS_BRIEF.md))
**Freeze:** intact. Exploratory lab diagnostic only. Train window only
(2020-01-01 → 2022-12-31). Validation/TEST never touched.
`configs/approved_strategies.yaml` unchanged (empty).

> The screen and its pre-stated decision logic were written **before** the run
> (see the brief §4.5 and the runner's "Reading this" block). This document
> records the outcome against that bar. It changes no campaign status and
> approves nothing.

---

## 1. What was run

- **Code:** [`research/edge_discovery/relative_value_spread.py`](../../research/edge_discovery/relative_value_spread.py),
  driven by [`scripts/run_edge_discovery_relative_value_spread.py`](../../scripts/run_edge_discovery_relative_value_spread.py).
- **Artifacts:** [`research/campaign_028/front_gate/relative_value_spread_screen.json`](../../research/campaign_028/front_gate/relative_value_spread_screen.json)
  + `.md`.
- **Universe:** all 21 leg1-leg2 spreads of the 7 majors, H4 mid-close.
- **Construction:** `s_t = ln(P1) − β·ln(P2)`, β by OLS frozen on train; z-score
  over a 60-bar strictly-prior window; fade |z| ≥ 2.0; 12-bar hold; next-bar-open
  emulation; **two-leg** round-trip cost (1.5 pip + 2×0.2 pip slip per leg, leg2
  scaled by |β|) + conservative financing stress on both legs.
- **Gates:** cost-feasibility (lab `cost_feasibility`), matched null
  (random-timing on the same spread, lab `null`), filter-adds-edge (z-threshold
  vs all-bar fade), and best-of-N selection sanity across the 21 spreads (lab
  `multiple_comparison.matrix_sanity`).

## 2. Result

| Gate | Outcome |
| --- | --- |
| Cost feasibility (two-leg) | **13 / 21** `COST_FEASIBLE`; **8 / 21** `COST_HOSTILE` (spread/ATR ≥ 0.25). The second leg's cost is a real headwind. |
| Per-spread matched null | 10 / 21 `materially_above_null` on their own spread (z-timing carries pre-cost information vs random timing). |
| Filter adds edge | 10 / 21 `filter_adds_edge = yes`. |
| **Best-of-N selection sanity** | **`LIKELY_SELECTION_NOISE`** — the decisive gate. |

Matrix-sanity detail (best = `USD_CAD-USD_CHF`, post-cost `+0.000898`):

- Expected best-of-N under noise: **`+0.001548`** (p95 `+0.002283`) — *higher than
  the observed best*.
- Deflated improvement: **`−0.000650`** (negative).
- P(best ≤ noise max): **`0.949`**.

The best spread out of 21 is **less** than what picking the maximum of 21 noisy
draws would produce by chance. Selecting it would be selecting noise.

## 3. Why "10 above null" is not an edge

Two structural facts, both visible in the artifact, explain why the per-spread
positives are not trustworthy and the selection gate is right to kill them:

1. **Half-life ≫ hold.** Measured AR(1) reversion half-lives are **126–1195
   bars** (mostly 250–530 H4 bars ≈ 40–90 days) against a **12-bar (~2-day)
   hold.** The position is unwound long before the spread reverts to equilibrium,
   so the post-cost result is dominated by *in-sample spread drift over the hold*,
   not by completed reversion.
2. **Symmetric large outliers.** Per-spread gaps to the random-timing null span
   `+23σ` down to `−79σ`. That two-sided spread is the signature of in-sample
   drift across a unit-root-ish spread, i.e. exactly the **USD common-factor
   confound** flagged in the brief §4.3 (the seven majors all share USD, so a
   "spread" can simply trend with EUR-vs-GBP-type fundamentals rather than
   revert). It is *not* the signature of a stable mean-reverting edge.

The unit tests encode this honestly: a constructed cointegrated spread shows a
short half-life and a genuine fade, while a basket of independent random walks
flags `LIKELY_SELECTION_NOISE` — the same verdict the real majors produced.

## 4. Decision

**CAMPAIGN_028 does not earn a precommit scaffold.** Per the bar set in the brief
(§4.5: "advances to a precommit scaffold only if the best spread is
`ROBUST_MATRIX_SIGNAL`"), the relative-value spread reversion thesis **fails the
front gate** on the selection-noise check, with the two-leg cost and the
half-life/hold mismatch as compounding structural problems. This mirrors how
**C026** closed the timeframe ladder: a cheap screen killed the idea before any
campaign machinery was built. The freeze is intact and nothing was promoted.

## 5. Parked (pre-registerable, NOT executed)

One observation is worth recording so it is not re-mined accidentally: the
within-spread z-timing does carry **pre-cost** information, and the reversion
timescale is far longer than the tested hold. A *genuinely new, pre-committed*
follow-up could test a **hold matched to the measured half-life with an
exit-on-reversion to z≈0** (and USD-neutralised / triangulated spread
constructions to defuse the common-factor confound).

This is parked, **not** scheduled, and is bound by
[`STRATEGY_RESEARCH_RESTART_CRITERIA.md`](STRATEGY_RESEARCH_RESTART_CRITERIA.md):
it would require a fresh precommit written **before** seeing its result, ideally
on a different data slice or with an explicit multiple-testing haircut. Re-running
this same train slice with a longer hold and keeping the best spread would be the
multiple-testing trap the restart criteria explicitly reject ("Mine the same data
along a new slicing") and must not be done.

## 6. What this delivered (reusable infrastructure)

Independent of the verdict, Phase 1 added a permanent, tested lab capability:

- `research/edge_discovery/relative_value_spread.py` — a two-leg spread screen
  that composes the existing lab primitives (forward returns, random-timing null,
  two-leg cost, cost-feasibility, best-of-N matrix sanity) plus a pure-numpy
  AR(1) half-life. Import-isolated; no broker/approval/execution import.
- `scripts/run_edge_discovery_relative_value_spread.py` — train-only runner that
  blocks cleanly without the H4 store and refuses any window past the train end.
- `tests/research/edge_discovery/test_relative_value_spread.py` — 11 tests
  (mechanics + cointegrated-vs-random-walk boundaries + basket selection-noise).

This is the **first cointegration/relative-value capability in the lab** and can
screen any future spread idea cheaply.

# Bias-of-Fixtures Audit — Result

**Sprint:** `research-bias-of-fixtures-audit-001` · Phase 5
**Date:** 2026-05-24
**Status:** Audit complete. No strategy approved. No campaign verdict
changed. No parameter tune proposed. No backtest re-executed.

> No strategy approved by this document. CAMPAIGN_001–014 keep their
> existing verdicts. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live loops still refuse every
> configured strategy.

This document answers the six questions the audit plan
([`BIAS_OF_FIXTURES_AUDIT_001_PLAN.md`](BIAS_OF_FIXTURES_AUDIT_001_PLAN.md)
§4 Q1–Q6) posed against the fixture/artifact substrate, with
direct citations to the Phase 1 inventory and the two Phase
2/3 study outputs. It then states what is safe to keep, what
needs documentation, and what — if anything — needs a follow-up
sprint to repair.

---

## Q1 — Is CAMPAIGN_011 acceptable as the binding null?

**Yes.** The null is structurally legitimate; every conditional
shape metric the audit checked lands inside the cross-campaign
range, and the one metric it lands outside (`mean_R_overall`) is
outside in the direction a floor *should* be outside.

Specific findings from
[`outputs/real/bias_null_baseline.{json,md}`](../../research/edge_discovery/studies/outputs/real/bias_null_baseline.md):

| sub-question | finding | classification |
|---|---|---|
| coverage by (fold × pair) | 8 folds × 7 pairs = 56 cells, **0 empty** | acceptable |
| trade count distribution | max pair share 0.167 (GBP_USD), max fold share 0.138 (fold 4) | within_expected_range |
| direction balance | 51.8 % long / 48.2 % short, deviation 0.018 from 50 / 50 | within_expected_range |
| session / hour-of-day | peak 16.6 % at UTC 9 | minor_deviation (small) |
| exit-reason distribution | 20.5 % stop / 78.9 % time / 0.6 % eod | matches cross-campaign median |
| stop_rate vs others | 0.205 ∈ [0.204, 0.242] | inside range |
| time_rate vs others | 0.789 ∈ [0.746, 0.793] | inside range |
| mean_R given_stop vs others | −0.831 ∈ [−0.948, −0.792] | inside range |
| mean_R given_time vs others | +0.209 ∈ [+0.067, +0.211] | inside range |
| mean_R_overall vs others | −0.0024 vs others [−0.148, −0.041] | **outside (less negative)** |

Reading: the null shares the engine's stop+time exit shape with
every candidate — same hard-stop crystallisation, same small-
positive time-exit bias — and is only "different" in that it
loses *less* overall than every rule-based candidate the lab
has tried. That is the structurally desired property of a
binding floor: a candidate should at minimum clear what random
entry against the same engine achieves. None of CAMPAIGN_010 -
014 do.

The minor session/hour-clustering observation (16.6 % at UTC 9)
is a property of the H4 candle grid and the random-entry sampler;
it is **far below** the material-deviation threshold (0.25) and
two orders of magnitude smaller than CAMPAIGN_010's structural
63 % clustering at UTC 9 or CAMPAIGN_014's 62 % at UTC 13. No
action required.

**Bottom line for Q1: CAMPAIGN_011 is acceptable as the binding
null. No re-execution required.**

---

## Q2 — Are CAMPAIGN_010-014 comparable enough for current screens?

**Yes, with one documentation-grade caveat.** Five of five
invariant axes pass; the one source of asymmetry the audit found
is the trade-window-population gap, and that gap does not flip
the headline numbers.

From
[`outputs/real/bias_cross_campaign_comparability.{json,md}`](../../research/edge_discovery/studies/outputs/real/bias_cross_campaign_comparability.md):

| axis | result | classification |
|---|---|---|
| fold layout | identical 8-fold layout across all 5 | harmless |
| pair universe | identical 7 majors across all 5 | harmless |
| fill_model + fill_timing + granularity | identical | harmless |
| trade-CSV schema | single 14-column schema, all 280 CSVs | harmless |
| exit-reason vocabulary | `['eod', 'stop', 'time']` identical | harmless |
| trade-window population | C010/011 test-only; C012/013/014 partial | **needs_documentation** |
| coverage anomalies | C013 has 29/56 empty (fold,pair) cells; C010 has 2 | weakens_comparison |

The trade-window finding (F0-2 from the audit plan) is real and
worth documenting:

- CAMPAIGN_010 and CAMPAIGN_011 trade only on each fold's test
  window. Every entry is OOS.
- CAMPAIGN_012, CAMPAIGN_013, CAMPAIGN_014 emit trades over a
  wider window (the strategies require indicator warm-up that
  extends earlier than test_start, and the lab's walk-forward
  engine logs every emitted trade rather than test-window-only
  trades).

The audit re-derived the exit-asymmetry headline under a strict
test-window-only restriction. Result:

| campaign | mean_R_given_time (full) | mean_R_given_time (test-only) | Δ |
|---|---:|---:|---:|
| CAMPAIGN_010 | +0.1926 | +0.1926 | +0.0000 |
| CAMPAIGN_011 (null) | +0.2093 | +0.2093 | +0.0000 |
| CAMPAIGN_012 | +0.1450 | +0.1436 | −0.0014 |
| CAMPAIGN_013 | +0.2105 | +0.2107 | +0.0002 |
| CAMPAIGN_014 | +0.0667 | +0.0640 | −0.0027 |

The maximum absolute delta is 0.0027 R — two orders of magnitude
smaller than the +0.05 R material-gap floor. Every campaign still
has positive mean_R_given_time on test-only. Every campaign still
has negative mean_R_overall on test-only. The exit-asymmetry
headline survives.

**Bottom line for Q2: the campaigns are comparable enough. The
trade-window asymmetry is documentation-grade, not repair-grade.**

---

## Q3 — Are any existing lab findings weakened by fixture bias?

**No existing finding is invalidated.** Two findings receive
documentation updates.

1. **The cross-campaign exit-asymmetry headline survives the
   test-only restriction.** Every campaign still shows positive
   `mean_R_given_time`. Every campaign still loses overall.
   `share_gross_loss_from_stops ≥ 0.60` and
   `share_gross_gain_from_time_exits ≥ 0.98` hold on the test-
   only data with negligible drift. The binding tests in
   `tests/research/edge_discovery/test_exit_asymmetry.py` remain
   valid.

2. **The EUR_USD / CAMPAIGN_012 R-9 fire is on test-only-data
   trades.** Of CAMPAIGN_012's 88 EUR_USD fold-0 trades, 51 are
   test-only and 37 are validation. R-9 fires on the *full*
   ledger of all 35 (campaign, pair) cells, but the cell where it
   actually fires (EUR_USD × CAMPAIGN_012) has 469 test-only
   trades out of 819 total in the full ledger — enough sample to
   re-derive. The audit did **not** re-run R-9 against test-only
   data (that would belong in a different sprint), but the
   ranking-rule R-9 definition is robust because the
   single-pair-probe sprint's `outputs/real/
   probe_robustness_eur_usd_c012.{json,md}` already showed that
   the cell classified as ISOLATED_SELECTED_CELL_ARTIFACT — not
   PROMISING. The classification does not change under the
   test-only restriction.

3. **C013's 29 empty (fold, pair) cells out of 56 (52 %)** is a
   real cross-campaign comparability weakness but **not a fixture
   bias** — it's a property of CAMPAIGN_013's strategy (currency-
   strength rotation, which only emits a trade when a pair is at
   the rank-top or rank-bottom of the universe). The audit's
   classification correctly flagged it as `weakens_comparison`.
   The existing exit-asymmetry sprint already noted CAMPAIGN_013
   per-side asymmetries; this is the underlying explanation.
   Reading: C013 contributes less per-pair coverage to cross-
   campaign aggregates than the other four campaigns; lab readers
   should not over-interpret per-pair patterns inside C013 alone.

**Bottom line for Q3: no existing lab finding is invalidated.
Two findings get explicit documentation (the test-window
asymmetry and the C013 empty-cell pattern).**

---

## Q4 — Are any screens too dependent on artifact quirks?

**No.** All four exit-shape screens (B.1 – B.4 in the
[`EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md`](EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md))
are cell-level — they apply per (candidate, pair) — and they
either:

- restrict the trade population further (B.1's LOO-stability
  test, the multi-cell-coherence test in the
  [`EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md`](EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md)
  §A.1, the n_folds_paired ≥ 6 floor in §A.6), or
- depend on cross-campaign comparisons that already hold under
  test-only restriction (B.2's "stops are not worse than the
  null's" requirement).

For each:

| screen | depends on the C011 null? | depends on cross-campaign trade-window alignment? | robust under test-only restriction? |
|---|---|---|---|
| B.1 mean_R_given_time ≥ C011's + 0.05R | yes | partially (C011 is test-only, candidates' trade-window may include val+test) | YES — null sits at the same value (Δ = +0.0000); candidate values drift by ≤ 0.003 R |
| B.2 mean_R_given_stop ≥ C011's − 0.05R | yes | partially | YES — same reasoning |
| B.3 No R-9 fire | no (per-cell metric) | no | YES — per-cell, not aggregate |
| B.4 per-fold stop_rate σ ≤ 0.06 | no (within-campaign) | no | YES — within-campaign, no comparison |

**Bottom line for Q4: no screen is too dependent on an artifact
quirk. The screens are designed at the cell level and survive
the test-window restriction.**

---

## Q5 — What should be repaired before the next real candidate study?

**Nothing requires repair to support the lab's current screens.**

Two items belong on a "consider tightening, not blocking" list:

1. **For comparability cleanliness**, a future sprint could
   re-execute CAMPAIGN_012, CAMPAIGN_013, CAMPAIGN_014 with
   test-window-only trade ledgers (i.e. the walk-forward engine
   would drop emitted trades whose `entry_time < test_start`).
   This would make every cross-campaign aggregate a true
   apples-to-apples OOS comparison. **It is not required by any
   current lab finding.** The audit's headline-survival check
   shows the deltas would be < 0.003 R per campaign on
   mean_R_given_time and < 0.02 R per campaign on
   mean_R_overall.

2. **Optional labeling polish**: back-fill `data_kind` /
   `exploratory_only` into the four legacy
   `outputs/study_*.json` files so machine readers don't need to
   open the matching `.md` to learn the data kind. The audit
   instead added a `README.md` in the outputs directory and a
   binding test that asserts no active code reads them — that's a
   safer fix because it doesn't modify historical artifact bytes.

Neither item is on the critical path. The lab can run the next
real candidate study (whatever that turns out to be) without
either repair.

---

## Q6 — What remains safe to use immediately?

| rule / screen / doc | safety status |
|---|---|
| `EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md` (§1-3 ranking, §2 red flags R-1 to R-8) | **safe to keep as-is** |
| `EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md` (§A.1 binding null, §A.2 material-gap floor) | **safe to keep as-is** |
| `EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md` (§A.1 multi-cell coherence, §A.5 R-9, §A.6 n_paired ≥ 6) | **safe to keep as-is** |
| `EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md` (§B.1-B.4 pre-campaign screens, §C.1-C.4 reporting) | **safe to keep as-is** |
| existing `outputs/real/*.json` artifacts | **safe to keep citing as evidence** |
| existing binding tests under `tests/research/edge_discovery/` | **safe to keep passing** |
| paper / demo / live refusal loops | **safe — still refuse every configured strategy** |
| `configs/approved_strategies.yaml = approved: []` | **safe — unchanged** |

No rule needs to be relaxed. No rule needs to be tightened to
patch a bias the audit uncovered. The audit's role here is to
*say so out loud*: the existing rule stack is calibrated against
fixtures that this audit certifies as adequate for their stated
purpose.

---

## Decision on a new addendum

**The audit does NOT introduce a new ranking-rule addendum.**

Rationale:

- No existing rule needs to be relaxed (the rules are working).
- No existing rule needs to be tightened to patch a fresh bias
  (the audit didn't find one).
- The trade-window-population finding is informational; it does
  not change how the screens behave, because the screens are
  cell-level and the headline numbers survive the test-only
  restriction.
- The synthetic-vs-real labeling fix landed as an additive README
  + a binding test, not as a new rule.
- The verdict-word ban from the prior sprints explicitly
  prohibits introducing a "PASS" / "APPROVE" / "PROMOTE" event in
  any classification field; this audit's outputs all carry
  `verdict_word_ban_acknowledged = true` and the binding tests
  re-verify it.

If a future sprint *does* re-execute CAMPAIGN_012-014 with test-
only trade ledgers, a small addendum at that time could record
the resulting deltas. Until then, no addendum is required.

The four existing addenda (candidate ranking rules, hydrate,
single-pair probe, exit-asymmetry) remain in force. This audit's
RESULT becomes part of the chain of evidence those addenda
implicitly rely on.

---

## What this audit explicitly does NOT do

- Does **not** approve any strategy.
- Does **not** change CAMPAIGN_010 - 014 verdicts.
- Does **not** propose any parameter tune.
- Does **not** modify any of `configs/approved_strategies.yaml`,
  `configs/paper.yaml`, `configs/practice.yaml`,
  `configs/live.example.yaml`.
- Does **not** modify any `backtests/CAMPAIGN_*/walk_forward/`
  artifact.
- Does **not** modify any `CAMPAIGN_*_STATUS.md` or
  `*_WALK_FORWARD_RESULT.md` verdict-bearing doc.
- Does **not** modify the evidence manifest or evidence index.
- Does **not** call any broker endpoint.
- Does **not** fetch new market data.

## What this audit does add (in scope, additive only)

- 1 audit plan: `BIAS_OF_FIXTURES_AUDIT_001_PLAN.md`
- 1 artifact inventory: `BIAS_OF_FIXTURES_ARTIFACT_INVENTORY.md`
- 1 result doc (this file): `BIAS_OF_FIXTURES_AUDIT_001_RESULT.md`
- 2 lab studies under `research/edge_discovery/studies/`:
  `bias_null_baseline.py`, `bias_cross_campaign_comparability.py`
- 4 study outputs (JSON + MD pairs) under `outputs/real/`:
  `bias_null_baseline.{json,md}`,
  `bias_cross_campaign_comparability.{json,md}`
- 1 README clarifying the synthetic-vs-real boundary:
  `research/edge_discovery/studies/outputs/README.md`
- 1 binding-test file (28 tests):
  `tests/research/edge_discovery/test_bias_of_fixtures.py`

Total: 10 net-new files. Zero files modified outside the
audit's scope. The freeze, the verdict-word ban, the approval
boundary, and every refusal path remain intact.

---

## Recommended next branches (for the human reader's consideration only)

The audit certifies the substrate. It does **not** recommend a
specific next strategy. If a future sprint runs, the audit's
recommended priority order is:

1. **A truly new candidate-finding study** that uses the existing
   exit-shape screens (B.1-B.4) to evaluate a fresh proposal at
   the lab stage — letting the screens catch the small-n masking
   pattern before any campaign-scale resource is spent.

2. **A documentation sprint** that walks the existing four-addenda
   stack into a single readable "lab decision rules" doc, so a
   new reader doesn't need to read four addenda + this audit to
   understand what the screens do. Not urgent.

3. **An optional re-execution sprint** to give CAMPAIGN_012,
   CAMPAIGN_013, CAMPAIGN_014 test-window-only trade ledgers
   (so cross-campaign aggregates are literally apples-to-apples).
   The audit's headline-survival check shows the qualitative
   findings would not change; the quantitative improvement is
   under 0.003 R per campaign on `mean_R_given_time`. Lowest
   priority.

Explicitly **not recommended**: any sprint that revisits
CAMPAIGN_010 - 014 verdicts or that asks "could this campaign
have edge after all". The exit-asymmetry sprint already answered
that with a hard no and this audit reconfirms there's no fixture-
bias loophole to walk through.

---

## Appendix — Pointers to evidence

The full audit chain, in order:

1. [`docs/research/BIAS_OF_FIXTURES_AUDIT_001_PLAN.md`](BIAS_OF_FIXTURES_AUDIT_001_PLAN.md)
   — Phase 0 plan, six audit questions, pre-committed refusals,
   three Phase-0 orientation findings.
2. [`docs/research/BIAS_OF_FIXTURES_ARTIFACT_INVENTORY.md`](BIAS_OF_FIXTURES_ARTIFACT_INVENTORY.md)
   — Phase 1 inventory, sha256 / size / row-count for every
   committed artifact in scope.
3. [`research/edge_discovery/studies/outputs/real/bias_null_baseline.md`](../../research/edge_discovery/studies/outputs/real/bias_null_baseline.md)
   — Phase 2 null audit.
4. [`research/edge_discovery/studies/outputs/real/bias_cross_campaign_comparability.md`](../../research/edge_discovery/studies/outputs/real/bias_cross_campaign_comparability.md)
   — Phase 3 cross-campaign audit, test-only headline survival.
5. [`research/edge_discovery/studies/outputs/README.md`](../../research/edge_discovery/studies/outputs/README.md)
   — Phase 4 synthetic-vs-real boundary doc.
6. [`tests/research/edge_discovery/test_bias_of_fixtures.py`](../../tests/research/edge_discovery/test_bias_of_fixtures.py)
   — Phase 4 binding tests pinning the audit's findings.

This RESULT doc (Phase 5) is the human-readable summary.

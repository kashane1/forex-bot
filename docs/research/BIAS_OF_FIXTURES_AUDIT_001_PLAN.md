# Bias-of-Fixtures Audit — Plan

**Sprint:** `research-bias-of-fixtures-audit-001` · Phase 0
**Date:** 2026-05-24
**Status:** research-infrastructure audit only — descriptive plan,
no strategy approval, no campaign verdict change.

> This sprint does **not** approve any strategy, does **not** change
> any CAMPAIGN_001–014 verdict, does **not** tune parameters, does
> **not** create a new campaign, and does **not** use broker
> endpoints. It audits the **fixtures and artifacts** the lab already
> consumes. `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live loops still refuse every configured strategy.

---

## 1. What "fixture bias" means in this repo

A **fixture** here is any artifact the edge-discovery lab consumes
to produce a quantitative claim. Concretely:

- per-campaign trade ledgers (`backtests/CAMPAIGN_*/folds/fold_NN/
  fold_NN_<PAIR>_trades.csv`)
- per-campaign per-fold per-pair backtest summaries
  (`*_summary.json`)
- per-campaign walk-forward roll-ups
  (`backtests/CAMPAIGN_*/walk_forward/{plan,results}.json`)
- the CAMPAIGN_014 event fixture
  (`research/calendar/fixtures/campaign_014_events.json`)
- the gitignored H4 SQLite candle store
  (`data/campaign_002.sqlite3`)
- the Lean-parity H4 provenance JSONs
  (`research/lean_parity/exports/campaign_002_h4/*.provenance.json`)
- the synthetic test fixtures
  (`research/edge_discovery/sample_fixtures/synthetic_*`)
- the walk-forward fold plans (`backtests/CAMPAIGN_*/walk_forward/
  plan.json::folds[]`)

**Fixture bias** is any property of these artifacts that — without
changing any strategy code — **systematically tilts** a comparison
the lab performs. The categories that matter to this audit:

| category | example |
|---|---|
| coverage bias | one campaign's trade ledger spans a wider date window than another's, so per-fold aggregates use uneven n |
| population bias | one campaign trades on test-only, another on val+test, so a "fold-level" expectancy doesn't compare like-for-like |
| schema bias | one campaign's trade CSV uses different columns / different exit-reason vocabulary |
| selection bias | the lab's screening accidentally always lands on the same outlier pair/fold |
| synthetic-vs-real bias | a finding that arose against synthetic fixtures is treated as if it came from real data |
| provenance bias | an artifact's `data_request_hash` / `config_hash` / `data_sha256` is missing or inconsistent, masking which inputs were used |

A bias is **not** the same as a difference. Two campaigns are
*allowed* to differ — different entry rules, different trade
counts, different per-pair fingerprints. What this audit checks is
whether the **lab's downstream comparisons** silently rely on
properties the artifacts don't actually share.

## 2. Why this audit now

Recent lab outputs (this branch and the three preceding ones)
treat CAMPAIGN_011 as the binding random-entry null and compute
cross-campaign exit-shape, mean-R, and stop-rate metrics over the
union of CAMPAIGN_010-014 trade ledgers. The next family of
candidate-evaluation rules (the new pre-campaign exit-shape
screen B.1-B.4) **depends on the CAMPAIGN_011 null shape itself**.
If the fixtures underneath are biased — for instance, if C011's
trade population is on a different window than C012-014's — then
the new screens may be calibrated against an unintended baseline.

The preceding sprint (`research-exit-asymmetry-cross-campaign-001`)
flagged this explicitly in its §G "future evolution" block:
*"This addendum may be tightened further by lowering the 0.05 R
material-gap floor if a future bias-of-fixtures audit shows the
null itself is biased toward positive R."* This audit answers that
prerequisite.

## 3. In-scope artifacts

Same five-campaign universe and the same supporting fixtures the
hydrate sprint inventoried in
[`EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md`](EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md):

- **CAMPAIGN_011 null artifacts** — the binding random-entry
  baseline (1,177 trade rows across 8 folds × 7 pairs).
- **CAMPAIGN_010, 012, 013, 014** — the four candidate campaigns
  compared against the null.
- **CAMPAIGN_010-014 walk-forward plans** — the fold definitions
  every cross-campaign comparison relies on.
- **CAMPAIGN_014 event fixture** — the only event-class artifact
  the lab consumes.
- **H4 SQLite candle store** (gitignored) — the underlying price
  data every walk-forward depends on.
- **Lean-parity H4 provenance JSONs** — committed proxies for the
  gitignored CSV exports.
- **Synthetic fixtures** — used by tests; need to verify they're
  not silently used as evidence.
- **The four ranking-rule documents** that depend on the above:
  `EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`,
  `EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md`,
  `EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md`,
  `EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md`.

Out of scope: CAMPAIGN_001-009 inputs (already retired as primary
baselines), the broker module, the loops module, anything in
`configs/`. This audit does not run any backtest.

## 4. Audit questions

The audit must produce a defensible answer to each of these. "I
don't know" is an allowed answer; fabrication is not.

### Q1 — Is CAMPAIGN_011 acceptable as the binding null?

Sub-questions:
- Does the null cover all 8 folds × 7 pairs the way it claims?
- Is its per-pair / per-fold trade count distribution defensible
  (no pair / fold ≫ dominating the aggregate)?
- Is its direction balance (long vs short) consistent with random
  entry?
- Is its session / hour-of-day distribution consistent with random
  entry (i.e., no degenerate clustering)?
- Is its exit-reason mix structurally different from the rest of
  the lab's campaigns in any way that would make it accidentally
  *easier* (positive-R-prone) or *harder* (positive-R-resistant)
  than future candidates?

### Q2 — Are CAMPAIGN_010-014 comparable enough for current screens?

Sub-questions:
- Same fold windows? (preliminary check: yes, all five share the
  same 8-fold layout and universe 2020-01-01 → 2026-05-20.)
- Same pair universe? (preliminary: yes, all 7 majors.)
- Same fill model / fill timing / cost assumptions?
- Same trade-window population? **(preliminary check: NO — see §6
  "What this audit already found in orientation")**
- Same schema across trade-CSV columns?
- Any campaign with an artifact-only advantage or disadvantage?

### Q3 — Are existing lab findings weakened by fixture bias?

Sub-questions:
- Does the cross-campaign exit-asymmetry headline (every campaign's
  `mean_R_given_time` positive, including the null at +0.2093 R)
  survive when restricted to **test-window trades only**?
- Does the EUR_USD / CAMPAIGN_012 R-9 fire survive that
  restriction?
- Does CAMPAIGN_011's "+0 R aggregate" survive that restriction
  (it should — C011 already trades on test-only).

### Q4 — Are any screens too dependent on artifact quirks?

Sub-questions:
- Is the +0.05 R material-gap floor calibrated against a clean
  null shape, or against a shape contaminated by mixed-window
  bias?
- Is the 0.06 stop_rate dispersion ceiling robust to including
  only test-window trades?
- Would dropping the val+test concatenation change the LOO and
  t-stat screens enough to flip any cell's classification?

### Q5 — What should be repaired before the next real candidate?

If any of Q1-Q4 expose a hard problem, recommend a follow-up
sprint to repair it. Repair means re-execute the affected walk-
forward with a **test-window-only** trade ledger and re-derive the
cross-campaign aggregates. **This sprint does not perform that
repair.** It only diagnoses and recommends.

### Q6 — What remains safe to use immediately?

For every screen / rule the lab currently runs, the audit must
state explicitly: "safe to keep as-is", "safe with documentation",
or "park pending repair." No silent passes.

## 5. Methodology and outputs

This audit is **read-only descriptive**. It runs zero backtests,
zero broker calls, zero strategy code. It uses pandas / numpy on
the committed artifacts, plus the already-shipped lab helpers
(`research/edge_discovery/real_data.py`).

Outputs by phase:

| phase | docs | code | data |
|---|---|---|---|
| 0 | `BIAS_OF_FIXTURES_AUDIT_001_PLAN.md` (this) | — | — |
| 1 | `BIAS_OF_FIXTURES_ARTIFACT_INVENTORY.md` | — | — |
| 2 | — | `research/edge_discovery/studies/bias_null_baseline.py` | `outputs/real/bias_null_baseline.{json,md}` |
| 3 | — | `research/edge_discovery/studies/bias_cross_campaign_comparability.py` | `outputs/real/bias_cross_campaign_comparability.{json,md}` |
| 4 | (doc updates if needed) | — | — |
| 5 | `BIAS_OF_FIXTURES_AUDIT_001_RESULT.md` (+ optional addendum) | — | — |
| 6 | `BIAS_OF_FIXTURES_AUDIT_001_SUMMARY.md` | binding tests in `tests/research/edge_discovery/test_bias_of_fixtures.py` | — |

Each `.json` output carries the standard provenance block
(`data_kind == "real"`, `exploratory_only == True`, full
`inputs[]` with sha256, `verdict_word_ban_acknowledged == True`,
`refusals` block with `approves_strategy == False`,
`changes_campaign_verdict == False`, `proposes_parameter_tune ==
False`, `writes_to_approved_strategies_yaml == False`).

## 6. What this audit already found in orientation (Phase 0)

Three preliminary findings, written down here so the later phases
can confirm or refute them rather than rediscovering them:

### F0-1 — Fold windows, pair universe, fill model are aligned

All five campaigns share the same 8-fold walk-forward plan
(universe 2020-01-01 → 2026-05-20, fold 0 train = 2020-01-01 →
2021-06-23, validation = 2021-06-24 → 2021-12-20, test =
2021-12-21 → 2022-06-18, etc.), the same 7-pair universe
(AUD_USD, EUR_USD, GBP_USD, NZD_USD, USD_CAD, USD_CHF, USD_JPY),
the same H4 granularity, and the same fill model
(`fixed_slippage_pips=0.2`, `spread_slippage_multiplier=0.5`,
fill_timing `signal_bar_close`). On these axes the campaigns
are aligned by construction.

### F0-2 — Trade-window populations are NOT aligned

The five campaigns differ on **which sub-windows of the fold
their trade ledgers cover**:

| campaign | fold-0 total trades | inside test only | inside validation only | inside train only |
|---|---:|---:|---:|---:|
| CAMPAIGN_010 session_breakout | 367 | 367 (100 %) | 0 | 0 |
| CAMPAIGN_011 random_entry_anchor (null) | 143 | 143 (100 %) | 0 | 0 |
| CAMPAIGN_012 regime_switcher_atr_percentile | 678 | 465 (69 %) | 213 (31 %) | 0 |
| CAMPAIGN_013 cross_pair_currency_strength_rotation | 794 | 287 (36 %) | ~360 (45 %) | ~150 (19 %) |
| CAMPAIGN_014 calendar_event_window_anomaly | 93 | 43 (46 %) | 50 (54 %) | 0 |

The data_request_hash differs in lockstep:
{C010, C011} = `46318435eea4…`, {C012, C013} = `7639b8cef0c5…`,
C014 = `6c4f9a8fd52f…`. The configured H4 from-time differs
correspondingly — the strategies requiring longer indicator
warm-ups got more pre-test data, **and the engine logged every
trade emitted in that wider window**.

This means the cross-campaign exit-asymmetry headline numbers
(every campaign's `mean_R_given_time > 0`, including the null at
+0.2093 R) were computed over **non-comparable trade
populations**: C010/C011 on test-window only, C012/C013/C014 on
validation + test (and C013 on some training data too).

**Implication for the audit:** Phase 3 must re-derive the headline
metrics restricted to test-window trades only and report the
delta. If the asymmetry survives the restriction, the prior
finding survives. If it doesn't, the addendum needs documentation
work (not a new addendum, since the screens themselves remain
correct — they're cell-level and the test-only restriction tightens
not loosens them).

### F0-3 — Synthetic fixtures are present but small

`research/edge_discovery/sample_fixtures/` holds
`synthetic_EUR_USD_H4.csv` (480 bars), `synthetic_events.csv`
(6 events × 3 classes), and a generator script. These are clearly
labelled as synthetic. Phase 4 must verify no real-data study
silently consumes them and no ranking rule was derived from them.

## 7. Things that would invalidate or weaken CAMPAIGN_011 as the null

| condition | severity | what the audit would do |
|---|---|---|
| C011 missing folds or pairs the others have | **invalidates** | recommend C011 re-execution |
| C011 trade direction grossly imbalanced (e.g. 80 % long) | **weakens** | document, add reporting requirement |
| C011 session/hour-of-day grossly clustered | **weakens** | document, add reporting requirement |
| C011's trade-window narrower than test window | **invalidates** | recommend C011 re-execution |
| C011's exit-reason mix has a class missing entirely | **weakens** | document |
| C011's per-pair / per-fold trade count → one cell explains > 50 % | **weakens** | flag for ranking-rule update |
| C011 vs C012-014 trade-window asymmetry (F0-2) | **weakens cross-campaign comparison, NOT the null itself** | recommend test-only re-aggregation in screens |

## 8. Things that would require a follow-up data/fixture repair sprint

- Any campaign with missing per-fold artifacts that the lab
  currently treats as present.
- Any campaign with a trade-CSV schema change the lab's loaders
  silently accommodate but the metric definitions implicitly
  depend on.
- Any pair-universe difference between two campaigns that the lab
  has been concatenating.
- Any case where the underlying H4 candle bytes (`data_sha256`)
  differ between campaigns that claim to share the same data
  window.
- Any case where a "real" study output was actually produced from
  a synthetic-fallback path without `data_kind` reflecting that.

The repair sprint, if needed, would NOT be this sprint. It would
be its own numbered sprint with its own pre-commit.

## 9. What cannot be concluded from this audit

- The audit cannot vindicate or invalidate any **strategy**. It
  audits the substrate, not the entry logic.
- The audit cannot make any CAMPAIGN_010-014 verdict change. All
  five remain REJECT-anchored.
- The audit cannot rule out fixture bias forms it does not test
  for (e.g., look-ahead bias in the candle data itself would
  require a different sprint).
- The audit's output is descriptive, not approval-bearing. The
  verdict-word ban (APPROVE / PASS / PROMOTE / SHIP / GO-LIVE /
  GREEN-LIGHT) applies to every artifact this sprint produces.

## 10. Pre-committed refusals

The sprint will not, under any output it produces:

- approve any strategy.
- change any CAMPAIGN_001-014 verdict.
- propose a parameter tune.
- write to `configs/approved_strategies.yaml`, `configs/paper.yaml`,
  `configs/practice.yaml`, or `configs/live.example.yaml`.
- modify any `backtests/CAMPAIGN_*/walk_forward/*` artifact.
- modify any `CAMPAIGN_*_STATUS.md` / `*_WALK_FORWARD_RESULT.md`
  verdict-bearing doc.
- modify the evidence manifest or evidence index.
- call any broker endpoint, fetch new market data, or read the
  operator's `.env`.
- relax any existing ranking-rule threshold without an explicit
  sprint-level justification (per the ranking rules §G; this
  audit can only **tighten**).

## 11. Done-conditions

Phase 0 is done when:
- this plan is committed.
- the baseline freeze / secret-scan / archive checks PASS on the
  current worktree.
- `configs/approved_strategies.yaml` still has `approved: []`.
- `forex_bot.approval.StrategyNotApprovedError` still importable.

All four pre-conditions are confirmed on this branch as of
2026-05-24.

---

## Appendix A — pinned headline numbers from orientation

For provenance: the orientation `python -c "..."` probes that
established F0-1, F0-2, F0-3 above are committed to memory and
will be re-derived in Phases 1-3 by the inventory and audit
scripts. Headline numbers (fold-0 EUR_USD):

```
CAMPAIGN_010_session_breakout                          n=48   in_test=48   in_val=0    in_train=0
CAMPAIGN_011_random_entry_anchor                       n=12   in_test=12   in_val=0    in_train=0
CAMPAIGN_012_regime_switcher_atr_percentile            n=88   in_test=51   in_val=37   in_train=0
CAMPAIGN_013_cross_pair_currency_strength_rotation     n=296  in_test=112  in_val=136  in_train=48
CAMPAIGN_014_calendar_event_window_anomaly             n=15   in_test=5   in_val=10   in_train=0
```

The Phase-3 cross-campaign script must reproduce these counts as
a first-line invariant check before any aggregate is computed.

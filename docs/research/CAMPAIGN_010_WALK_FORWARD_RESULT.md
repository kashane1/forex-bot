# CAMPAIGN_010 — Walk-Forward Result and Verdict

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-walk-forward-001`
`strategy_evidence: false`

Phase 4 formal classification of the CAMPAIGN_010 walk-forward
evidence (`session_breakout 0.1.0-c010`). Verdict evaluated
strictly against the pre-committed gates in
[`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
§10. **No gate is relaxed after seeing results.** A REJECT is
called when the data falsifies the hypothesis; an INCONCLUSIVE
when sample-size or coverage is the issue; a RESEARCH_PASS_UNAPPROVED
when every gate passes — and even then, the candidate cannot enter
[`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
without items 4–6 of the six-evidence ladder.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked.

## 1. Headline verdict — **REJECT**

`session_breakout 0.1.0-c010` is **rejected as a research candidate
under its pre-committed walk-forward protocol**, on real OANDA H4
practice data for the 7-pair universe, 8 rolling folds spanning
2021-12-21 → 2025-11-29.

| dimension | value |
|---|---|
| `WalkForwardResults.overall_verdict` | **`REJECT`** |
| classification under the protocol | **REJECT** (not BLOCKED — the run produced clean evidence; not INCONCLUSIVE — sample sizes meet the trade-count gate; not RESEARCH_PASS — multiple gates fail by wide margins) |
| was any gate relaxed? | **no** — gates evaluated verbatim from §10 |
| was any parameter tuned? | **no** — frozen-parameter assertion in the runner aborts before any backtest if a single value drifts |
| could the strategy be approved? | **no** — even hypothetically, this REJECT closes the research gate for `session_breakout 0.1.0-c010`; a NEW candidate (different name/version, different rules) would need its own discovery + design + pre-commit cycle |

## 2. Aggregate-level gate evidence

Authoritative metrics from
[`backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json`](../../backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json)
and the extended
[`backtests/CAMPAIGN_010_session_breakout/walk_forward/fold_detail.json`](../../backtests/CAMPAIGN_010_session_breakout/walk_forward/fold_detail.json):

| gate (verbatim) | threshold | observed | result |
|---|---|---|:---:|
| `aggregate.fold_pass_rate` | `100 %` (strict) | **0 / 8 = 0 %** | **FAIL** |
| `aggregate.fold_count` | ≥ 6 | 8 | PASS |
| `aggregate.expectancy_R_net_of_stress_financing` (pre-financing here; financing overlay strictly worsens it — see Phase 5) | ≥ 0.05 R | **−0.0408 R** | **FAIL** |
| `aggregate.profit_factor_net_of_stress_financing` | ≥ 1.10 | **0.0428** | **FAIL** |
| `aggregate.trade_count` | ≥ 200 | 2,791 | PASS |
| `aggregate.pairs_positive` | ≥ 4 of 7 | **1 / 7 (USD_CHF only)** | **FAIL** |
| `aggregate.single_fold_dominance` | ≤ 60 % | 30.3 % | PASS |
| `aggregate.single_pair_dominance` | ≤ 40 % | 24.1 % | PASS |
| `financing.modeled_refused` | PASS | PASS (Phase 5 uses ESTIMATED + conservative stress; MODELED refused at four layers) | PASS |
| `financing.conservative_stress_run_does_not_flip_verdict` | PASS | Vacuously PASS — the pre-financing verdict is already REJECT; stress only deepens it (see [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md)) | PASS |

Five gates fail. Four pass. Under strict-pass, **REJECT**.

## 3. Per-fold gate evidence

Per
[`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
§10 (test fold row), each fold's pre-committed gates are:

- `expectancy_R_net_of_stress_financing ≥ 0.05 R`
- `profit_factor_net_of_stress_financing ≥ 1.10`
- `pairs_positive_net_of_stress_financing ≥ 4 of 7`
- `trade_count ≥ 30`
- `single_pair_dominance ≤ 60 %`

| fold | test window | exp_r | PF | pairs +ve | trades | pair_dom % | gates passed | result |
|---:|---|---:|---:|---:|---:|---:|---:|:---:|
| 0 | 2021-12-21 → 2022-06-18 | −0.0042 | 0.69 | 5 / 7 | 367 | 51.1 | 3 / 5 | **FAIL** |
| 1 | 2022-06-19 → 2022-12-15 | −0.1005 | 0.00 | 0 / 7 | 390 | 26.2 | 2 / 5 | **FAIL** |
| 2 | 2022-12-16 → 2023-06-13 | −0.0623 | 0.13 | 2 / 7 | 409 | 27.3 | 2 / 5 | **FAIL** |
| 3 | 2023-06-14 → 2023-12-10 | −0.0215 | 0.20 | 3 / 7 | 374 | 56.5 | 2 / 5 | **FAIL** |
| 4 | 2023-12-11 → 2024-06-07 | −0.0833 | 0.03 | 1 / 7 | 347 | 29.6 | 2 / 5 | **FAIL** |
| 5 | 2024-06-08 → 2024-12-04 | −0.0604 | 0.11 | 2 / 7 | 265 | 44.3 | 2 / 5 | **FAIL** |
| 6 | 2024-12-05 → 2025-06-02 | +0.0211 | 1.57 | 3 / 7 | 347 | 21.2 | 3 / 5 | **FAIL** |
| 7 | 2025-06-03 → 2025-11-29 | −0.0071 | 0.64 | 3 / 7 | 292 | 29.7 | 2 / 5 | **FAIL** |

**0 of 8 folds pass.** Fold 6 is the strongest (expectancy +0.0211,
PF 1.57, three pairs positive); even there the expectancy is
below the 0.05 R gate and only 3/7 pairs are positive.

## 4. Per-pair × all-folds aggregate (informational)

| pair | total trades | aggregate return % | expectancy R | sign |
|---|---:|---:|---:|:---:|
| EUR_USD | 310 | −6.21 | −0.0794 | − |
| GBP_USD | 565 | −6.11 | −0.0428 | − |
| USD_JPY | 492 | −5.36 | −0.0003 | ≈ 0 |
| AUD_USD | 511 | −9.63 | −0.0748 | − |
| USD_CAD | 434 | −9.26 | −0.0649 | − |
| **USD_CHF** | 432 | **+1.69** | **+0.0185** | **+** |
| NZD_USD | 47 | −1.67 | −0.1399 | − |

USD_CHF is the only pair with positive expectancy; NZD_USD has
both a low trade count and a strongly negative expectancy.
`pairs_positive` is 1 / 7 — well below the ≥ 4 / 7 gate.

## 5. No-lookahead audit

The candidate's no-lookahead guarantees were enforced at code time
by the structural unit tests in
[`tests/unit/test_session_breakout.py`](../../tests/unit/test_session_breakout.py):

- AST-level check that `generate_signal()` reads only `close[t]`
  on bar `t` and uses `[-2]` indices for `high`, `low`, and ATR.
- Source-grep that the strategy module imports nothing from
  `forex_bot.broker`.
- Source-grep that the strategy and runner do not reference any
  CAMPAIGN_002 key (no parameter contamination).

All passed at Phase 0 baseline (735 tests) and remain passing.
No fold's negative expectancy is attributable to a leakage bug.

## 6. Why this is REJECT, not INCONCLUSIVE or BLOCKED

| classification | criterion | this campaign |
|---|---|---|
| **BLOCKED** | the pipeline cannot execute (no candle data; tooling gap) | not blocked — the pipeline ran end-to-end in 7.9 s, 2,791 trades produced |
| **INCONCLUSIVE** | the gates are missed because of sample-size or coverage thinness, not directional negativity | not inconclusive — aggregate trade count 2,791 (≥ 200 gate) and 8 folds (≥ 6 gate); the issue is directional, not statistical |
| **REJECT** | gates fail directionally on out-of-sample evidence | **yes** — 7 / 8 folds are net negative; aggregate expectancy −0.0408 R; profit factor 0.04; 1 / 7 pairs positive |
| RESEARCH_PASS_UNAPPROVED | every gate passes — and even then, the candidate is *not approved* until human review under [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) | not applicable |

## 7. Implications for the strategy registry

- **No change to `configs/approved_strategies.yaml`.** It remains
  `approved: []`.
- **CAMPAIGN_010 reclassifies from `candidate-scaffold (no verdict)`
  to `rejected` in
  [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)** (Phase 8 will
  apply this change). The new row will read:

  > `session_breakout 0.1.0-c010` — rejected — paper: NO · demo: NO · live: NO — CAMPAIGN_010 walk-forward (8 folds, 7 pairs, 2,791 trades, fold pass rate 0 %, aggregate expectancy −0.04 R, 1/7 pairs positive)

  with paper / demo / live all NO and the primary-evidence
  reference being this document.

- The candidate joins the rejected-strategy list with
  CAMPAIGN_002/003/004/007/008/009 in
  [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md). The research-freeze
  posture is unchanged.

## 8. What this verdict does not do

1. **It does not approve any strategy.**
2. **It does not change CAMPAIGN_002's REJECT verdict.**
3. **It does not unblock paper / demo / live.** `paper-loop` and
   `demo-loop` continue to refuse via the empty registry; no
   `live-loop` command exists.
4. **It does not modify any frozen parameter.** A future variant
   (e.g. `session_breakout 0.2.0-…`) would be a NEW candidate
   requiring its own discovery + pre-commit cycle.
5. **It does not retire the H4 store** — that data is reusable
   for further research candidates.

## 9. What a future, NEW candidate would need

Per
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§12 (overfitting disqualifiers), a re-attempt at the same family
**is disqualified** unless:

- the new candidate is meaningfully different from CAMPAIGN_010
  along the 6-dimension distinctness scoring rubric;
- the rule difference is not a parameter tweak motivated by
  CAMPAIGN_010's results (no curve-fitting to a rejected campaign);
- a fresh `CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md` review picks it
  on merit, not on the prior result;
- a fresh pre-commit fixes new gates before any evidence is taken.

Recommended near-term posture is to **not** re-attempt this family
and to revisit
[`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
candidates C2–C5 with the same evidence discipline this sprint
demonstrated.

## 10. Safety state

- `configs/approved_strategies.yaml`: **`approved: []`** (untouched).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **Paper / demo / live remain blocked.**
- **No broker call** at any phase; **no `.env` read; no credential
  printed; no account / order / trade / position / transaction
  endpoint queried.**
- **No QuantConnect / LEAN.**
- **No engine-PnL change.** **No `src/forex_bot/financing.py`
  edit.**
- **No new external dependency.**
- **Bulky data uncommitted.** Only compact summaries + the
  committed campaign artifact directory (≈ 0.9 MB) live in the
  repo.

## 11. Cross-links

- [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md)
  (Phase 3 — commands, frozen-parameter enforcement, fold table)
- [`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md)
  (Phase 2 — fold geometry)
- [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md)
  (Phase 1 — data source + provenance hashes)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  §10 (the gates)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
  (Phase 8 will update this to `rejected`)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
  §9 (default rejection criteria)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
  (approval is a human action; this verdict cannot become approval)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
  (Phase 8 will add a row for `session_breakout 0.1.0-c010` as
  `rejected`)
- [`backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json`](../../backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json)
- [`backtests/CAMPAIGN_010_session_breakout/walk_forward/results.md`](../../backtests/CAMPAIGN_010_session_breakout/walk_forward/results.md)
- [`backtests/CAMPAIGN_010_session_breakout/walk_forward/fold_detail.json`](../../backtests/CAMPAIGN_010_session_breakout/walk_forward/fold_detail.json)

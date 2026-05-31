# CAMPAIGN_026 — Donchian + HTF confluence timeframe-ladder diagnostic (001) — PLAN

**Status:** SCAFFOLD / PLAN (no evidence yet). **Not approved. Not a paper/demo/live
enablement. Not a test-lockbox run. Not an unrestricted optimization.**

- **campaign_id:** `CAMPAIGN_026`
- **strategy_family:** `donchian_htf_confluence_timeframe_ladder`
- **version:** `0.1.0-c026`
- **branch:** `research-campaign-026-donchian-htf-timeframe-ladder-001`
- **base:** `main` @ `a38126d` (includes the merged CAMPAIGN_025 train-matrix **REJECT**)

---

## 1. Purpose

Determine whether the C025 Donchian + HTF-confluence breakout idea — which was
**rejected on M5** — is salvageable on a **different execution timeframe**, by running
a small, pre-committed timeframe-ladder diagnostic across **M3, M15, M30** and
comparing each against the M5 reference.

It answers five questions:

1. Was M5 *uniquely* cost-defeated (spread/ATR ≈ 0.45–0.50)?
2. Does M15 or M30 improve spread/ATR enough to be worth testing?
3. Is M3 even worse than M5 (as expected)?
4. Should any timeframe continue to validation / Backtrader parity / a future campaign?
5. Or should the entire lower-timeframe Donchian family be closed?

## 2. Relationship to CAMPAIGN_025

C025 (`m5_donchian_htf_confluence_breakout`, M5 execution) was **REJECTED**:
`REJECT_MATRIX_NO_TRAIN_CANDIDATE / TEST_LOCKBOX_CLOSED / NOT_APPROVED`. All 16
pre-committed M5 archetypes were net-negative after realistic costs (expectancy
−0.077…−0.178R, PF 0.70–0.85, ≤1/7 pairs non-negative, 2× stress −0.40…−0.75R); no
champion; validation never ran; lockbox stayed closed; `approved_strategies.yaml`
stayed `approved: []`. The decisive structural fact was **spread/ATR ≈ 0.45–0.50 on
M5** — the bid/ask spread was roughly half the per-bar ATR, fatal for a breakout
family that risks/targets a few multiples of ATR.

C025 evidence (preserved, REJECT): `CAMPAIGN_025_TRAIN_MATRIX_RESULT.md`,
`CAMPAIGN_025_TRAIN_MATRIX_VALIDATION_001_SUMMARY.md`,
`CAMPAIGN_025_INTERPRETATION_AND_PRIOR_COMPARISON.md`.

C026 reuses the **same** signal family (Donchian breakout with HTF confluence,
prior-completed-bars-only, `next_bar_open` fills, adverse-first same-bar policy). It
does **not** invent a new signal; it varies only the **execution timeframe** and the
matching HTF context ladder.

## 3. Why this is a timeframe diagnostic, not a retune

- The signal logic, cost model, evidence discipline, and selection rules are inherited
  from C025 unchanged.
- The candidate matrix is **small and pre-committed** (preferred 11, max 15), frozen
  before any train evidence is run.
- The hypothesis under test is mechanical and physical: **bar range scales with
  timeframe, spread does not**, so slower bars *may* carry a smaller spread/ATR drag.
  This is a falsifiable cost-structure question, not parameter mining.
- A **cost/ATR diagnostic runs before strategy evidence** (Phase 3). If all timeframes
  are cost-hostile, the matrix is classified `BLOCKED_COST_STRUCTURE` and strategy
  evidence does not run.

## 4. Materialization requirements

Known DB state (research Postgres `market_data.candles`, verified Phase 0):

| Granularity | Source | Status |
|---|---|---|
| M1 (canonical) | `oanda-practice-m1` | present, 2021-05-27 → 2026-05-26, 7/7 pairs |
| M5 | `m1_materialized` | present |
| M15 | `m1_materialized` | present |
| H1 | `m1_materialized` | present |
| H4M1 (M1-derived H4) | `m1_materialized` | present |
| H4 (native, for D1AGG) | `oanda-practice` | present (from 2020) |
| **M3** | — | **ABSENT — must materialize from M1** |
| **M30** | — | **ABSENT — must materialize from M1** |

Rules: derive **only** from canonical M1; bucket-start timestamps; complete buckets
only (omit incomplete); preserve provenance (`source = m1_materialized`); store under
granularity labels `M3` / `M30` (no native-broker conflict — broker natives are
M1/M5/M15/H1/H4). **No broker re-fetch. No raw candles or DB dumps committed.**

Note: adding M3/M30 to the materializer's target set will bump
`aggregation_config_hash` (the hashed config lists its targets). The aggregation
*rules* are unchanged; previously materialized M5/M15/H1/H4M1 bars remain valid and
are not re-materialized. This is documented in the Phase 1 design doc.

## 5. Candidate timeframes & context ladder

| Execution TF | Local setup | Trend context | Regime context |
|---|---|---|---|
| **M3** | M15 | H1, H4M1 | D1AGG |
| **M15** | H1 (or internal M15 pullback/compression — fixed before evidence) | H1, H4M1 | D1AGG |
| **M30** | H1 | H4M1 | D1AGG |

Data provenance: M3/M15/M30/H1/H4M1 from M1-derived materialized bars; D1AGG from
native-H4-derived aggregation. Fill realism: `next_bar_open`.

## 6. Evidence protocol

1. Materialize + verify M3 and M30 from canonical M1 (Phases 1–2).
2. Verify M15 already materialized (done — present).
3. Compute spread/ATR + coverage diagnostics for M3/M5/M15/M30, M5 as reference
   (Phase 3).
4. Freeze a small candidate matrix **before** train evidence (Phase 4).
5. Run the matrix on **TRAIN only** (Phase 7).
6. Select **at most one** champion using **train-only** rules.
7. If a champion exists, run validation **once** on that champion only (Phase 8).
8. Do **not** validate non-selected candidates.
9. Do **not** use validation for selection.
10. Do **not** open the test lockbox.

Preferred split (subject to coverage confirmation in Phase 6):
- **Train:** 2021-07-01 → 2023-06-30
- **Validation:** 2023-07-01 → 2024-12-31
- **Test:** closed / unused (lockbox).

## 7. No-validation-selection rule

Timeframe and parameters are chosen using **train evidence only**. Validation, if it
runs at all, runs exactly once on the single train-selected champion and is used only
to *confirm or reject* it — never to pick the timeframe, the candidate, or any
parameter. There is no test-lockbox run in this sprint.

## 8. No-test-lockbox rule

The 2025-01-01 → 2026-05-20 window is the sealed test lockbox. The runner refuses any
window intersecting it (`--fail-if-test-window`, default on). No promotion-grade
out-of-sample claim is produced here; Backtrader parity remains a prerequisite for any
future promotion-review classification.

## 9. Safety invariants (hard rules)

- `configs/approved_strategies.yaml` stays `approved: []`. **No strategy approved.**
- Paper/demo/live stay blocked. No executor/broker/OANDA mutation files touched.
- No OANDA order/trade/position/transaction/live endpoint calls. No live credentials.
- No `.env`, credentials, DB dumps, raw candles, or bulky artifacts committed.
- No tuning after seeing results. No gate changes after seeing results.
- If train evidence is poor, **reject honestly**.
- If no train candidate passes filters, **no promotion-style validation runs**.

## 10. Expected artifacts

Docs (`docs/research/`): this plan; `CAMPAIGN_026_M3_M30_MATERIALIZATION_DESIGN.md`;
`..._MATERIALIZATION_RESULT.md`; `CAMPAIGN_026_TIMEFRAME_COST_ATR_DIAGNOSTIC.md`;
`CAMPAIGN_026_TIMEFRAME_LADDER_SPEC.md`;
`CAMPAIGN_026_DATA_COVERAGE_AND_SPLIT_DECISION.md`;
`CAMPAIGN_026_TRAIN_TIMEFRAME_LADDER_RESULT.md`;
`CAMPAIGN_026_SELECTED_CHAMPION_VALIDATION_RESULT.md` (conditional);
`CAMPAIGN_026_TIMEFRAME_LADDER_INTERPRETATION.md`;
`CAMPAIGN_026_BACKTRADER_PARITY_READINESS.md`;
`CAMPAIGN_026_TIMEFRAME_LADDER_001_SUMMARY.md`.

Machine artifacts (`research/campaign_026/`): `materialization/` verification JSON;
`timeframe_cost_diagnostics/` CSV+JSON; `timeframe_ladder/` candidate registry, train
matrix CSV/JSON, optional validation result. (No raw candles / DB dumps.)

Code: extend `timeframe_aggregation.py` + `m1_timeframe_materialization.py` for
M3/M30; new `scripts/run_campaign_026_donchian_htf_timeframe_ladder.py`; generalize the
isolated C025 vectorized simulator for variable execution timeframe; unit tests.

## 11. Validation commands

```
python -m pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/run_campaign_026_donchian_htf_timeframe_ladder.py --preflight-only
python scripts/run_campaign_026_donchian_htf_timeframe_ladder.py --data-feature-preflight
python scripts/run_campaign_026_donchian_htf_timeframe_ladder.py --cost-diagnostic
```

## 12. Blocked / terminal conditions

- `BLOCKED_DATA_MATERIALIZATION / NOT_APPROVED` — M3/M30 cannot be materialized/verified.
- `BLOCKED_COST_STRUCTURE / NOT_APPROVED` — all timeframes cost-hostile pre-evidence.
- `REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE / NOT_APPROVED` — no candidate passes
  train filters.
- `TRAIN_VALIDATION_REJECT / NOT_APPROVED` — champion fails validation.
- `SINGLE_TIMEFRAME_REVIEW_ONLY / NOT_APPROVED` or
  `SINGLE_PAIR_REVIEW_ONLY / NOT_APPROVED` — narrow, non-promotable signal.
- `TRAIN_TIMEFRAME_LADDER_PASS_PARITY_REQUIRED / TEST_LOCKBOX_CLOSED / NOT_APPROVED` —
  best attainable: a train+validation-clean champion still gated behind Backtrader
  parity and a future, separately-authorized lockbox sprint.

Maximum attainable status from this sprint is **review-only / parity-required**;
**never** an approval.

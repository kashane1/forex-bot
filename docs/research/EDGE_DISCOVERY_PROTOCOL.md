# EDGE_DISCOVERY_PROTOCOL

**Status:** process doc (binding for future strategy search). Diagnostic/
infrastructure only — defines how a strategy idea must be *screened* before it
earns a full campaign. Approves nothing; opens no test lockbox.

> Companion docs: [`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md),
> [`PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md`](PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md),
> [`FUTURE_STRATEGY_SEARCH_WORKFLOW.md`](FUTURE_STRATEGY_SEARCH_WORKFLOW.md),
> [`FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`](FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md),
> [`EDGE_DISCOVERY_EXISTING_LAB_AUDIT_001.md`](EDGE_DISCOVERY_EXISTING_LAB_AUDIT_001.md).

---

## Why campaign-by-campaign search is too slow

A full campaign costs days: scaffold, materialize timeframes, run a train
matrix, gates, parity, write-ups. Across ~26 campaigns the dominant outcome was
REJECT at or below the C011 null. The C025 → C026 sequence is the canonical
lesson: a full M5 Donchian+HTF campaign was built and rejected purely because
**spread/ATR ≈ 0.45** made every candidate net-negative (C025); C026 then spent
a second campaign confirming a monotone cost ladder (M3 ≈ 0.59 → M30 ≈ 0.15)
with still no edge on any timeframe. Both verdicts were obtainable from cheap
pre-checks. The protocol exists so that *cost feasibility, signal information,
and a matched-null comparison are tested first*, and a campaign is only built
for ideas that survive.

## Four object types (do not conflate them)

1. **Market fact** — a measured property of the data (e.g. "M5 spread/ATR on
   the majors is ≈ 0.45"). No edge claim.
2. **Signal diagnostic** — a cheap lab measurement of whether a proposed
   signal/filter/exit/timeframe/pair/session carries information beyond a fair
   matched null. Produced by the edge-discovery lab. Maximum status: *candidate
   hypothesis with cheap supporting evidence.* Never a verdict.
3. **Strategy candidate** — a precommitted, fully-specified rule set that has
   passed the pre-campaign checklist and earned a campaign.
4. **Full campaign** — train/validation, parity, test-lockbox, the formal
   gate machinery. The only thing that can produce an approvable result.
5. **Promotion-review candidate** — a campaign that cleared every gate and is
   put to a human for approval via `configs/approved_strategies.yaml`.

The lab operates only at level 2. It cannot emit APPROVE / GO / PROMOTE — that
is structurally reserved for levels 4–5 (enforced by the report verdict-word
ban in `research/edge_discovery/report.py`).

## Required pre-campaign diagnostics

Run with the import-isolated lab (`research/edge_discovery/`). Each maps to a
module and the CLI in `scripts/run_edge_discovery_*.py`:

1. **Cost feasibility** — spread/ATR per pair/timeframe/session; flags
   `COST_FEASIBLE` / `COST_HOSTILE` / `TIMEFRAME_TOO_FAST` / `SESSION_HOSTILE` /
   `PAIR_COST_(DIS)ADVANTAGED`. Module: `cost_feasibility.py` (+ `costs.py`,
   `research/cost_atlas`). **A cost-hostile target is rejected here.**
2. **Forward-return information** — signed forward log-returns over horizons;
   does the signal point anywhere? Module: `windows.py`.
3. **Matched-null benchmark** — does the signal beat a null that *reproduces
   the idea's own structure* (pair/side/session/weekday/hold)? Module:
   `matched_nulls.py`. Beating a generic null is not enough.
4. **Entry/exit decomposition** — is the edge in the entry, the exit, or
   neither? Modules: `studies/exit_asymmetry_*`.
5. **Filter ablation** — does each filter add edge or only shrink the sample?
   Module: `filter_ablation.py`. Sample-only filters are demoted.
6. **Pair/timeframe/session opportunity map** — where, if anywhere, is the idea
   not cost-bound? Modules: `studies/study_session`, `study_pair_baseline`,
   `cost_feasibility.py`.
7. **Multiple-comparison sanity** — if many variants were screened, is the best
   meaningfully better than best-of-N selection noise, and does it survive
   pair/time-block holdout? Module: `multiple_comparison.py`.

## Minimum evidence to create a future strategy campaign

A campaign is "earned" only when an idea, screened with the lab, shows ALL of:

- cost feasibility passes for the target timeframe/session (`COST_FEASIBLE`);
- forward-return information present at a horizon the idea will actually trade;
- the idea's expectancy is **above its matched null** (not just a generic
  null) — ideally `BEATS_MATCHED_NULL` / above null p95;
- the edge does not vanish under entry/exit decomposition (it is not a pure
  exit-model artifact on random entries, nor a good entry destroyed by a bad
  exit unless the exit is the proposed contribution);
- every retained filter is `FILTER_ADDS_EDGE`, not `FILTER_ONLY_REDUCES_SAMPLE`;
- if a matrix was screened, the result is not `LIKELY_SELECTION_NOISE` and not
  `FRAGILE_SINGLE_PAIR_RESULT` / `FRAGILE_TIME_BLOCK_RESULT` (unless
  precommitted single-pair research);
- an expected trade count large enough that the campaign can reach the gate
  minimums.

The strict gate phrasing lives in
[`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md).

## Failure conditions that should block a campaign

- `COST_HOSTILE` / `TIMEFRAME_TOO_FAST` on the target (the C025/C026 trap).
- `WITHIN_MATCHED_NULL` / `BELOW_MATCHED_NULL` — no edge over a fair null.
- `BOTH_NO_EDGE` from the decomposition.
- All filters `FILTER_ONLY_REDUCES_SAMPLE` — the "edge" was selection variance.
- `LIKELY_SELECTION_NOISE` / `TOO_MANY_VARIANTS_FOR_EVIDENCE` on the matrix.
- Single-pair fragility without a precommitted single-pair mandate.

## Avoiding validation/test leakage

- All lab diagnostics run on **screening data only** — never the test lockbox
  (2025-01-01 → 2026-05-20). The matched-null module defaults to *not* sampling
  from the lockbox.
- The lab does not select parameters. It screens an idea; the campaign's own
  train/validation split selects parameters (and validation never chooses
  parameters either — see the gates doc).

## Avoiding parameter mining

- Precommit the idea (signal, filters, exits, pairs, timeframe, session) before
  running the lab. The lab measures *that* idea, it does not search variants to
  find one that beats null.
- If many variants are unavoidable, run `multiple_comparison.matrix_sanity` and
  treat `LIKELY_SELECTION_NOISE` as disqualifying.

## Documenting rejected ideas cheaply

A rejected idea gets a short note (idea, which diagnostic killed it, the flag,
one-line lesson) appended to the backlog — not a full campaign write-up. The
lab artifacts (compact JSON under `research/edge_discovery/cli_runs/` or a
study output) are the evidence. This keeps the cost of a "no" proportional to a
"no".

# Free / Local Parity Verifier — Comparison vs Bespoke Reference

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-001`
**Phase:** 5 · `strategy_evidence: false`
**Re-confirmed:** `infra-free-local-parity-verifier-002-full-data-run`
Phase 3 — the full-data run was attempted again on the new branch
and produced the same BLOCKED outcome (all seven CSVs absent
locally, no practice credentials configured, no SQLite store to
re-export from). The comparison harness was invoked programmatically
against `compare.blocked_report` with the real bespoke reference
JSON, producing a structurally identical seven-row BLOCKED report.
The full verbatim BLOCKED comparison output is preserved under
`/tmp/parity_verifier_002_run/comparison.md` (outside repo, not
committed); a transcript follows under "Sprint-002 re-run record"
below. Verifier-side bugs: **0**. Bespoke-side bugs: **N/A** (engine
not exercised; no real-candle cross-check possible without the CSVs).

> A PASS or FAIL here describes agreement between two engines on a
> rejected strategy. It **does not** approve a strategy and does not
> lift the freeze. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked.

## Status — full-data comparison BLOCKED

The full seven-pair comparison against the bespoke no-RiskEngine
reference (1,647 trades) cannot be run on this branch — the H4 export
CSVs at `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv`
are gitignored regenerable bulk data and are not present locally. See
[`FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md)
for the local data availability table and the recipe to unblock.

The fixture-level comparison logic is fully implemented and tested.
The BLOCKED status reflects **missing input data**, not a verifier
implementation gap.

## What ran in this sprint

| layer | status |
|---|---|
| comparison harness implementation (`research/parity_verifier/compare.py`) | done |
| comparison-tolerance ladder inherited from `LEAN_PARITY_COMPARISON_METHOD.md` | wired |
| divergence taxonomy (extended per `FREE_LOCAL_PARITY_VERIFIER_PLAN.md` §9) | wired |
| comparison-harness fixture tests | 11 cases pass |
| markdown rendering (`reporting.render_comparison_md`) | done |
| full seven-pair full-window comparison | **BLOCKED — CSVs absent locally** |

## Tolerance ranges and pass / fail rules

Inherited from
[`LEAN_PARITY_COMPARISON_METHOD.md`](LEAN_PARITY_COMPARISON_METHOD.md):

| metric | OK | WARN | FAIL |
|---|---|---|---|
| trade count, per pair & total | within ±5% | ±5%–15% | beyond ±15% |
| expectancy R, per pair | within ±0.03 | ±0.03–0.10 | beyond ±0.10 |
| return %, per pair | within ±0.5 pp | ±0.5–2.0 pp | beyond ±2.0 pp |

- **PASS** (overall OK) — every metric OK; the independent verifier
  corroborates the bespoke engine within tolerance.
- **WARN** — drift inside the review band; inspect before relying.
- **FAIL** — drift outside tolerance, missing pair, or malformed
  output.
- **BLOCKED** — the comparison could not be evaluated because the
  verifier did not produce a result (e.g., the gitignored CSVs are
  absent). BLOCKED is not silently treated as OK.

## Divergence taxonomy

Used by the comparison report to classify any non-OK pair:

- `data_mismatch` — verifier and bespoke consumed different candles
  (different rows, different OHLC, different timestamps).
- `timestamp_session_mismatch` — same candles, different
  timezone / session-boundary / Sunday-open handling.
- `indicator_mismatch` — EMA / ATR / Donchian / ADX series differ on
  identical input.
- `entry_exit_rule_mismatch` — indicator series agree, but the rule
  that turns them into a signal differs.
- `spread_slippage_fill_mismatch` — same signal bar, different fill
  price.
- `stop_trailing_mismatch` — same entry, different stop ladder or
  trailing rule.
- `sizing_pnl_mismatch` — same trade, different size or
  PnL-conversion.
- `financing_mismatch` — financing modeling difference.
- `unknown` — divergence the implementer has not yet localized.

The comparison harness starts with the most general label (`unknown`)
for any non-OK pair. Phase 6 refines a divergence to a more specific
bucket once it has been traced.

## Fixture-level comparison results

[`tests/research/test_parity_verifier_compare.py`](../../tests/research/test_parity_verifier_compare.py)
— **11 cases pass:**

- Perfect match across two pairs → overall OK, classification NONE.
- 4% trade-count delta → still OK.
- 10% trade-count delta → WARN.
- 50% trade-count delta → FAIL.
- 0.096 R expectancy drift → WARN (lands in the 0.03–0.10 band).
- Return-pct drift > 2 pp → FAIL.
- Pair missing from the verifier result → FAIL classified as
  `data_mismatch`; report carries the "missing" note.
- Pair status is the worst of per-metric statuses (one OK pair plus
  one count-FAIL pair → overall FAIL).
- `blocked_report` carries the bespoke side intact, status BLOCKED,
  reason recorded in `notes[0]`.
- Smoke: the harness runs against the **real bespoke reference JSON**
  (1,647 trades, 7 pairs) with an all-zero verifier result — produces
  a clean seven-row FAIL report without crashing.
- None-expectancy on both sides does not crash and does not flip an
  otherwise-FAIL count metric to OK.

## Per-pair comparison (BLOCKED placeholder)

This table will be populated by the script entry point's first
successful full-data run. Until then, every pair carries a BLOCKED
status sourced from `compare.blocked_report` so the document shape is
stable.

| instrument | bespoke trades | verifier trades | Δ % | bespoke exp R | verifier exp R | Δ R | bespoke ret % | verifier ret % | Δ pp | status | classification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EUR_USD | 233 | — | — | -0.196 | — | — | -10.83 | — | — | BLOCKED | unknown |
| GBP_USD | 215 | — | — | -0.097 | — | — | -5.12 | — | — | BLOCKED | unknown |
| USD_JPY | 247 | — | — | -0.0001 | — | — | -1.37 | — | — | BLOCKED | unknown |
| AUD_USD | 237 | — | — | -0.213 | — | — | -11.90 | — | — | BLOCKED | unknown |
| USD_CAD | 251 | — | — | -0.180 | — | — | -14.11 | — | — | BLOCKED | unknown |
| USD_CHF | 224 | — | — | -0.143 | — | — | -7.03 | — | — | BLOCKED | unknown |
| NZD_USD | 240 | — | — | -0.265 | — | — | -14.70 | — | — | BLOCKED | unknown |
| **total** | **1647** | **—** | — | | | | | | | **BLOCKED** | **unknown** |

`Bespoke ret %` values are quoted from
`research/lean_parity/campaign_002_h4_bespoke_reference.json` and the
`CAMPAIGN_002_LEAN_MAPPING_SPEC.md` §8 table.

## What happens when the user regenerates the CSVs

1. The user regenerates the seven CSVs (out-of-scope OANDA-touching
   step — `scripts/export_lean_parity_data.py`).
2. `python scripts/run_free_local_parity_verifier.py --output
   research/parity_verifier/results/campaign_002_h4/` produces
   `parity_summary.json` (verifier result) plus a `trades.csv`
   (gitignored).
3. The verifier result feeds back into this document: replace the
   BLOCKED rows with the harness's output of
   `reporting.render_comparison_md(report)`.

This is **infrastructure work**, not a research decision. A clean
PASS, a WARN, or a FAIL — none approves a strategy. CAMPAIGN_002
remains REJECT.

## Guardrails this report enforces

- `strategy_evidence: false` is hard-pinned in both
  `VerifierResult` and `ComparisonReport`; the Pydantic model
  refuses to construct an instance with `strategy_evidence=True`.
- `risk_engine_used: false` is hard-pinned in `VerifierResult` for
  the same reason — the verifier targets the no-RiskEngine bespoke
  reference and would not be a valid LEAN-era surrogate if marked
  otherwise.
- No tuning. A FAIL is a finding to localize, not a result to accept.
- No bespoke-engine edits to "make it match" the verifier.
- No CAMPAIGN_002 rule edits.
- No `configs/approved_strategies.yaml` edits.

## What this proves at fixture level

The comparison logic correctly:
- maps tolerances to the OK / WARN / FAIL ladder for trade count,
  expectancy, and return;
- escalates the per-pair status to the worst of its metrics;
- escalates the overall status to the worst of pairs + total;
- flags a missing pair as FAIL with `data_mismatch`;
- handles None / zero / large input gracefully.

## What this does NOT prove

- That the bespoke engine and the verifier agree on real candles —
  requires the absent CSVs.
- That CAMPAIGN_002 is any less REJECT than it was before this
  sprint. It is **still REJECT**.
- That any strategy is approved. None is.

## Sprint-002 re-run record

Captured 2026-05-22 on branch
`infra-free-local-parity-verifier-002-full-data-run` Phase 3. The
verifier was re-invoked end-to-end against the same absent-CSV
state, and the comparison harness was re-run programmatically.

### Verifier output (BLOCKED)

```text
Loaded bespoke reference: …campaign_002_h4_bespoke_reference.json (1647 trades, 7 pairs).
BLOCKED — AUD_USD: CSV not found at …AUD_USD_H4_lean.csv. …
BLOCKED — EUR_USD: CSV not found …
BLOCKED — GBP_USD: …
BLOCKED — NZD_USD: …
BLOCKED — USD_CAD: …
BLOCKED — USD_CHF: …
BLOCKED — USD_JPY: …
Verifier total trades: 0
Blocked pairs: ['AUD_USD', 'EUR_USD', 'GBP_USD', 'NZD_USD', 'USD_CAD', 'USD_CHF', 'USD_JPY']
```

Exit code: **2** (every pair blocked).

### Comparison report — BLOCKED

- Bespoke reference path: `research/lean_parity/campaign_002_h4_bespoke_reference.json`
- Bespoke total trades: **1,647**
- Verifier result path: — (not produced)
- Verifier total trades: — (none — BLOCKED)
- Δ %: —
- **Overall status: BLOCKED**
- **Overall classification: `unknown`** (the verifier did not run
  on candles, so divergence cannot be classified into a specific
  bucket; the comparison correctly avoids labelling the absence of
  output as PASS or FAIL).

### Per-pair table (sourced from the real bespoke reference)

| instrument | bespoke trades | verifier trades | Δ % | bespoke exp R | verifier exp R | Δ R | bespoke ret % | verifier ret % | Δ pp | status | classification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EUR_USD | 233 | — | — | -0.1961 | — | — | -10.8345 | — | — | BLOCKED | unknown |
| GBP_USD | 215 | — | — | -0.0971 | — | — | -5.1182 | — | — | BLOCKED | unknown |
| USD_JPY | 247 | — | — | -0.0001 | — | — | -1.3735 | — | — | BLOCKED | unknown |
| AUD_USD | 237 | — | — | -0.2134 | — | — | -11.9013 | — | — | BLOCKED | unknown |
| USD_CAD | 251 | — | — | -0.1804 | — | — | -14.1096 | — | — | BLOCKED | unknown |
| USD_CHF | 224 | — | — | -0.1430 | — | — | -7.0322 | — | — | BLOCKED | unknown |
| NZD_USD | 240 | — | — | -0.2645 | — | — | -14.7032 | — | — | BLOCKED | unknown |

### Reference scope confirmation (Sprint-002 lookup)

The bespoke reference used is the **no-RiskEngine** bespoke run at
`research/lean_parity/campaign_002_h4_bespoke_reference.json`,
exactly as the LEAN-era mapping spec §0 requires for an apples-to-
apples comparison with the verifier's strategy + engine mechanics
replica. The reference's top-level keys confirm scope:

- `parity_target`: `"CAMPAIGN_002 H4 trend_following baseline"`
- `risk_engine_used`: `false`
- `fill_timing`: `"signal_bar_close"`
- `window`: `["2020-01-01", "2026-05-20"]`
- `config_hash`: `d536a9b06818197f9915de6224e0b8ae58e77abe2c6f3c19426338646fb077bf`
- `strategy_evidence`: `false`
- `total_trades`: `1647`
- 7 pairs: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD.

The **1,032-trade with-RiskEngine** reference is **not** used; mixing
references is explicitly forbidden by the mapping spec §0 and was
not done.

### What this Sprint-002 comparison adds beyond Sprint 001

- A direct, programmatic invocation of `compare.blocked_report`
  against the real bespoke JSON on the new branch (not just the
  fixture-test invocation from Sprint 001).
- A full output transcript captured under
  `/tmp/parity_verifier_002_run/comparison.md` (outside repo, not
  committed) so the BLOCKED comparison shape is reviewable verbatim.
- Re-confirmation that the verifier's BLOCKED behavior, the
  comparison-harness BLOCKED behavior, and the script's exit code 2
  all line up.

### Divergence classification (Sprint-002)

- **Per pair:** `unknown` for all seven — the verifier never
  produced numbers to diverge from. Not classified as
  `data_mismatch` because the data side has not even been
  attempted (no fetch, no export); not `indicator_mismatch` because
  no indicator series ran; etc.
- **Overall:** `unknown`.
- **No divergence was hidden, relabelled, or tuned away.**

### Files committed by Sprint-002 Phase 3

- This `## Sprint-002 re-run record` section appended to the
  existing comparison doc.

### Files produced but not committed

- `/tmp/parity_verifier_002_run/parity_summary.json`
- `/tmp/parity_verifier_002_run/trades.csv` (header-only)
- `/tmp/parity_verifier_002_run/parity_summary.md`
- `/tmp/parity_verifier_002_run/comparison.md`
- `/tmp/parity_verifier_002_run/run.log`

All four live outside the repo and are not staged.

# Lean Parity — Comparison Method

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-run-001` · Phase 3

How a Lean CAMPAIGN_002 H4 parity run is compared against the bespoke
engine, by `scripts/compare_lean_campaign_002_parity.py`.

> Verification only — `strategy_evidence: false`. This compares
> *engines*, not strategies. CAMPAIGN_002 is REJECT and stays REJECT.

## What is compared

- **Reference:** the no-RiskEngine bespoke run
  `research/lean_parity/campaign_002_h4_bespoke_reference.json` (1,647
  trades). The reference is no-RiskEngine because the Lean algorithm
  replicates the strategy + engine mechanics, not the bespoke
  RiskEngine — see `CAMPAIGN_002_LEAN_MAPPING_SPEC.md` §0.
- **Lean result:** the algorithm's `parity_summary.json` — a `pairs`
  list, each entry with `instrument` and `trades`, optionally
  `expectancy_r` and `return_pct`.

Per pair, the harness compares: **trade count**, **expectancy R**, and
**return %** (the latter two only when the Lean result carries them).
It also compares the **total trade count** and flags any reference
instrument **missing** from the Lean result.

## Tolerance ranges

| metric | OK | WARN | FAIL |
|---|---|---|---|
| trade count (per pair & total) | within ±5% (relative) | ±5%–15% | beyond ±15% |
| expectancy R (per pair) | within ±0.03 (absolute) | ±0.03–0.10 | beyond ±0.10 |
| return % (per pair) | within ±0.5 pp (absolute) | ±0.5–2.0 pp | beyond ±2.0 pp |

A pair's status is the worst of its metrics; the overall status is the
worst of all pairs and the total-trade comparison. A missing instrument
is a FAIL. Malformed Lean output (unparseable JSON, no `pairs` list, a
pair lacking `instrument` / `trades`) is a FAIL.

## Pass / fail rules

- **PASS** (exit 0) — every metric OK. The independent Lean engine
  corroborates the bespoke engine within tolerance.
- **WARN** (exit 1) — drift inside the review band. Inspect before
  relying on the comparison; a WARN is not a clean parity.
- **FAIL** (exit 2) — drift outside tolerance, a missing pair, or
  malformed output.

## How to interpret divergence

A divergence is a **finding to localize**, not a result to accept or
hide. Classify it (per the mapping spec's mismatch risks):

- data-loading / timestamp-alignment mismatch;
- indicator seeding or definition mismatch (EMA / ATR / Donchian);
- fill-model or slippage mismatch;
- stop / trailing-stop behavior mismatch;
- sizing / PnL-conversion mismatch;
- warmup mismatch.

A divergence traced to a **Lean parity-implementation bug** is fixed on
the Lean side and the run repeated. A divergence traced to a real
**bespoke-engine discrepancy** is documented as an engine finding — it
is **never tuned away** and never hidden.

## Why a parity FAIL does not imply strategy quality

Parity checks whether two *engines* agree on the numbers for a fixed,
already-decided strategy. CAMPAIGN_002 is **REJECT**. A parity:

- **PASS** means only "the bespoke engine measured consistently with an
  independent engine" — the strategy it measured is still rejected;
- **FAIL** means "the two implementations disagree" — a software
  discrepancy to fix, saying nothing about the strategy either way.

Neither outcome approves a strategy, produces a trading verdict, or
lifts the research freeze. `configs/approved_strategies.yaml` stays
empty regardless.

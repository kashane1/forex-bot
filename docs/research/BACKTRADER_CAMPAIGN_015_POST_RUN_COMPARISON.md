# Backtrader Secondary-Lane Comparison — CAMPAIGN_015 (Post-Run)

**Sprint:** [CAMPAIGN_015 Post-Run Diagnostics 001](CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_PLAN.md)
**Branch:** `research-campaign-015-post-run-diagnostics-001`
**Date:** 2026-05-26
**Strategy:** `failed_breakout_reversal 0.1.0-c015`
**Config hash:** `17ddfd7eb87d93c502f148642c8ee883c66cb72bfa8ca72f981624a0dcfdd93c`
**Divergence classification:** **`DATA_MISMATCH`** (and therefore **`BLOCKED`**)

> Diagnostic-only document. The Backtrader lane is a **secondary
> verification lane**; it cannot approve any strategy under any
> outcome. `configs/approved_strategies.yaml` remains `approved: []`.
> The bespoke-runner verdict for CAMPAIGN_015 remains **REJECT**.

This doc is an **addition** to the prior
[`docs/research/BACKTRADER_CAMPAIGN_015_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_COMPARISON.md)
(which is left untouched). It is *not* a revision of that doc.

---

## 1 · Outcome

The Phase 4 post-run BT-vs-bespoke comparison is **`BLOCKED` with a
specific data-provenance reason**, not the inherited blanket BLOCKED
of the prior sprint:

- The bespoke lane **did** run successfully this sprint
  (see [rehydrate artifacts](../../research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/)).
- The BT lane **failed at the data preflight**: the row-sha256
  computed by `research.backtrader_lane.data_adapter.compute_csv_sha256`
  does **not** match the committed `data_sha256` in the
  `*.provenance.json` sidecar for **any of the 7 CAMPAIGN_002 H4
  instruments**.

Per the freeze, the runner correctly refuses to continue without
provenance verification. Bypassing the check (e.g. via a hypothetical
`--no-strict-provenance` flag, or rewriting provenance JSONs to
match the current CSVs) would violate the research-freeze invariants
and is explicitly out of scope for this post-run diagnostic.

---

## 2 · Why this is `DATA_MISMATCH`, not `BLOCKED-by-absence`

The CSV files **exist** at
`/Users/kashane/dev/forex-bot/research/lean_parity/exports/campaign_002_h4/`
in the main repo (gitignored, not in the worktree by default; this
sprint exposed them via gitignored symlinks). The committed
`*.provenance.json` sidecars are in the worktree.

The CSVs have drifted from the sidecars — both at the raw-file level
*and* at the row-sha256 level the data_adapter computes:

| instrument | raw file sha (prefix) | provenance sha (prefix) | row-sha256 from data_adapter (prefix) | match? |
|---|---|---|---|---|
| AUD_USD | `62938be3ac2d` | `fb9e619a93fb` | (runner error: row-sha mismatch) | ✗ |
| EUR_USD | `87cd3a130136` | `866d75446030` | `16ed0bc40d05` | ✗ |
| GBP_USD | `5a3c83e0a7d2` | `354a2da02ce3` | (runner stopped after EUR_USD) | ✗ |
| NZD_USD | `21a07eb294a1` | `3ba489b194c6` | n/a | ✗ |
| USD_CAD | `04e934629351` | `77f9bf8839b2` | n/a | ✗ |
| USD_CHF | `a3af10b39ba2` | `64ab6151e649` | n/a | ✗ |
| USD_JPY | `34a9454b5bb7` | `868b90906652` | n/a | ✗ |

The raw-file sha mismatch confirms the CSVs were regenerated (or
otherwise modified) after the provenance JSONs were committed. The
row-sha256 mismatch (computed by
`research.backtrader_lane.data_adapter.compute_csv_sha256`) confirms
that even the row-level content differs.

Per the prior precommit divergence-classification table, this is
**`DATA_MISMATCH`** — the engines cannot be compared because they
cannot demonstrably be reading the same candles. This is an
infrastructure / data-handling issue, not a strategy issue. The
correct fix lives in a separate **infra sprint**, not a research
sprint, and certainly not a post-run diagnostic sprint.

---

## 3 · Verbatim binding divergence-label set (from pre-commit §13)

- `PASS`
- `TOLERABLE_DRIFT`
- **`DATA_MISMATCH` ← this run**
- `TIMESTAMP_MISMATCH`
- `SIGNAL_RULE_MISMATCH`
- `FILL_TIMING_MISMATCH`
- `STOP_OR_TIME_EXIT_MISMATCH`
- `SIZING_OR_PNL_MISMATCH`
- `BLOCKED`

`DATA_MISMATCH` is the **primary** classification; `BLOCKED` is the
operational consequence (no comparison was performed). No trade-count,
expectancy, exit-reason, or R-drift comparison is fabricated.

---

## 4 · Non-fabrication statement

This document does NOT include:
- a BT-side trade count, expectancy, PF, or return %;
- a per-pair or per-fold R-drift table;
- a "BT confirms / refutes bespoke" sentence;
- any proxy that pretends to be a BT-vs-bespoke comparison.

It includes only verified sha256 evidence of CSV drift + the published
bespoke metrics (already produced in Phase 0 / 1 / 2 of this sprint).
That is the honest answer when the BT lane refuses to run.

---

## 5 · Reproduction recipe

To complete a real `PASS` / `TOLERABLE_DRIFT` comparison, a future
infra sprint must:

1. Re-export the CAMPAIGN_002 H4 CSVs via
   `scripts/export_lean_parity_data.py` and re-commit the matching
   `*.provenance.json` sidecars in lock-step, **or** restore the CSVs
   to the bit-identical state the existing sidecars expect.
2. Verify with:
   ```bash
   python -c "
   from pathlib import Path
   from research.backtrader_lane.data_adapter import load_candles
   for p in ('EUR_USD','GBP_USD','USD_JPY','AUD_USD','USD_CAD','USD_CHF','NZD_USD'):
       load_candles(p)
   print('all CSV provenance OK')
   "
   ```
3. Then run the BT lane:
   ```bash
   python scripts/run_backtrader_parity.py \
     --campaign CAMPAIGN_015 \
     --output research/campaign_015/diagnostics/backtrader_lane/
   ```
4. Compare to the bespoke rehydrate via the existing
   `scripts/compare_backtrader_parity.py` (if dispatched for CAMPAIGN_015):
   ```bash
   python scripts/compare_backtrader_parity.py \
     --bespoke research/campaign_015/diagnostics/walk_forward_rehydrate/ \
     --backtrader research/campaign_015/diagnostics/backtrader_lane/ \
     --output research/campaign_015/diagnostics/backtrader_comparison_full.json
   ```

None of these steps were performed in this sprint, because step 1
is an infra fix and this is a research diagnostic sprint.

---

## 6 · Safety invariants (verified)

- `configs/approved_strategies.yaml` remains `approved: []`.
- No engine was tuned to match the other.
- No CAMPAIGN_015 strategy parameter was changed.
- No prior campaign evidence was modified.
- No broker call, no `.env`, no live OANDA.
- The prior [`BACKTRADER_CAMPAIGN_015_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_COMPARISON.md)
  was not edited.

---

## 7 · What this means for the Phase 5 interpretation

The BT lane could neither corroborate nor refute the bespoke
CAMPAIGN_015 numbers in this sprint. The Phase 5 final interpretation
therefore relies on:

- the bespoke rehydrate (Phase 0),
- the gate-failure autopsy (Phase 1),
- the concentration / fragility diagnostics (Phase 2),
- the matched-null anti-overfit diagnostic (Phase 3).

The absence of BT corroboration is itself a data point: any follow-up
candidate work should require a clean BT lane *as a precondition*,
not as an afterthought.

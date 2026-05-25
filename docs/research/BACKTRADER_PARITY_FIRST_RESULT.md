# Backtrader Lane — Phase 6 First Real Comparison Result

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-001`
**Phase:** 6 of `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md`
**`strategy_evidence: false`**

> **This result cannot approve any strategy and does not enable
> paper / demo / live trading.** CAMPAIGN_002 remains REJECT.

## 0. Overall verdict

**BLOCKED — real CAMPAIGN_002 H4 candle data is not locally
regenerable in this worktree.** The Backtrader-lane runner and the
comparison harness work end-to-end against the committed provenance
sidecars and produce the documented `BLOCKED` artefacts, but the actual
H4 CSVs are gitignored and the rehydrated source SQLite store
(`data/oanda_h4_research.sqlite3`, ~80 MB) is also gitignored. No bug
was found in either engine and no campaign verdict changes.

## 1. Selected campaign

`CAMPAIGN_002` — H4 `trend_following 0.1.0-baseline-frozen`. Selection
rationale and adapter spec: see
[`BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md`](BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md).

## 2. Exact commands

```bash
# Preflight (dry run; just inspects local data availability):
python scripts/run_backtrader_parity.py \
    --campaign CAMPAIGN_002 \
    --output /tmp/bt_c002_preflight \
    --dry-run

# Real run (intended; ran as preflight in this sprint because no data):
python scripts/run_backtrader_parity.py \
    --campaign CAMPAIGN_002 \
    --output research/backtrader_lane/results/campaign_002/

# Comparison against the bespoke no-RiskEngine reference:
python scripts/compare_backtrader_parity.py \
    --campaign CAMPAIGN_002 \
    --backtrader-results /tmp/bt_c002_preflight \
    --bespoke-reference research/lean_parity/campaign_002_h4_bespoke_reference.json \
    --output /tmp/bt_c002_compare
```

## 3. Output paths (this run)

| artefact | path | size |
|---|---|---|
| runner `backtrader_summary.json` | `/tmp/bt_c002_preflight/backtrader_summary.json` | non-empty |
| runner `run_manifest.json` | `/tmp/bt_c002_preflight/run_manifest.json` | non-empty |
| runner `backtrader_trades.jsonl` | `/tmp/bt_c002_preflight/backtrader_trades.jsonl` | 0 trades |
| runner `run_log_summary.md` | `/tmp/bt_c002_preflight/run_log_summary.md` | non-empty |
| comparison `comparison_summary.json` | `/tmp/bt_c002_compare/comparison_summary.json` | non-empty |
| comparison `comparison_summary.md` | `/tmp/bt_c002_compare/comparison_summary.md` | non-empty |

These were written to `/tmp/` to avoid committing them to the repo;
the gitignore rule `research/backtrader_lane/results/` would also have
caught them. Bulky generated outputs are never committed.

## 4. Reference artefact paths

| reference | path | size |
|---|---|---|
| bespoke no-RiskEngine reference | `research/lean_parity/campaign_002_h4_bespoke_reference.json` | committed |
| Lean parity config (read by adapter) | `research/lean_parity/lean_parity_config.json` | committed |
| Lean mapping spec | `docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md` | committed |
| per-instrument provenance sidecars | `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.provenance.json` | committed (7 files) |
| per-instrument candle CSVs | `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv` | **gitignored — not present locally** |
| rehydrated H4 source store | `data/oanda_h4_research.sqlite3` | **gitignored — not present locally** |

## 5. Did Backtrader complete?

**No — preflight only.** The runner correctly reported every requested
instrument as `BLOCKED` because no CSV was found in
`research/lean_parity/exports/campaign_002_h4/`:

```text
instruments_runnable: []
instruments_blocked:  [EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD]
expected_in_export_dir: [AUD_USD, EUR_USD, GBP_USD, NZD_USD, USD_CAD, USD_CHF, USD_JPY]
available_in_export_dir: []
```

The runner emitted exactly the artefact set documented in
`BACKTRADER_RUNNER_CONTRACT.md` §3, with `total_trades = 0` and
`blocked_instruments` populated. **No fake trade was written.** The
manifest was JSON-sanitised against OANDA env-var leakage (no leakage).

## 6. Did the comparison complete?

**Yes — with overall classification `BLOCKED`.** The harness loaded
both inputs (the Backtrader summary above and the bespoke reference
JSON), discovered that the bespoke side has 7 pairs and the
Backtrader side has 0, classified each pair as `BLOCKED` (one side
missing pair data), and rolled up to overall `BLOCKED` per the
decision ladder in `BACKTRADER_PARITY_COMPARISON_SPEC.md` §4. No
metric drift was claimed; no spurious PASS / FAIL was emitted.

Excerpt from `comparison_summary.md`:

```text
- Total trades: backtrader 0 · bespoke 1647 · Δ -1647
- Overall classification: BLOCKED
- backtrader lane reported 7 blocked instruments: [...all 7 majors...]
```

## 7. Divergence classification

`BLOCKED` — by design, not by mismatch. The pipeline works; the data
isn't available in this worktree.

## 8. Suspected reason for divergence

There is no divergence: there is **no Backtrader-side trade list** to
diverge from the bespoke side. The cause is data unavailability:

- The seven `<INST>_H4_lean.csv` files (~0.95 MB each, gitignored per
  `.gitignore` line 72: `research/lean_parity/exports/**/*.csv`) are
  the input the adapter consumes.
- The source `data/oanda_h4_research.sqlite3` (gitignored per
  `.gitignore` line 60: `/data/`) is what
  `scripts/export_lean_parity_data.py` would regenerate the CSVs from.
- The worktree contains only `data/bot.sqlite3` (the operational bot
  DB, 167 KB), not the rehydrated research store.

Regenerating either artefact requires a separate operational sprint
(e.g. `scripts/rehydrate_oanda_h4_store.py` against a credentialed
practice account) — which is **out of scope** for this infra sprint,
and would require OANDA practice credentials that this sprint
deliberately does not use.

## 9. Bugs found

- **Bespoke-engine bug:** **none found.** Cannot find a bug we did
  not compare against.
- **Backtrader-adapter bug:** **none found.** Adapter, runner, and
  comparison harness all pass their unit + integration tests (75
  passes on the new code; 1179 total in the repo). The CAMPAIGN_002
  adapter's pure helpers (`_round_price`, `_fill_entry_price`,
  `_size_position`, `_trade_pnl`) bit-match the values the mapping
  spec specifies; the warmup-and-no-lookahead invariant holds on a
  flat 260-bar synthetic fixture; the entry/exit cycle is deterministic
  and bit-stable across two runs on the same 400-bar synthetic
  fixture.

## 10. Verdict change

**None.** This BLOCKED result cannot, and does not, alter:

- CAMPAIGN_002 REJECT verdict.
- CAMPAIGN_010 REJECT verdict.
- CAMPAIGN_011 REJECT (null model anchor) verdict.
- CAMPAIGN_012 REJECT verdict.
- CAMPAIGN_013 REJECT verdict.
- CAMPAIGN_014 scaffold-only status.
- `configs/approved_strategies.yaml` — still `approved: []`.
- paper / demo / live gates — still refuse every strategy.

## 11. What this run **did** prove

Even though no real candle data was processed, this end-to-end
exercise demonstrated:

1. The runner correctly detects missing CSVs and refuses to fabricate
   trades. Every blocked instrument is named in the output.
2. The runner's manifest sanitiser was active; the manifest
   `git_commit`, `git_dirty`, `backtrader` version, and Python /
   platform fields were populated correctly.
3. The comparison harness handles a 0-pairs-on-one-side input cleanly
   and rolls up to `BLOCKED` (not `PASS`, not a panic), with per-pair
   notes naming the missing side.
4. No OANDA call, no broker call, no credential read. (`-` echo from
   `scripts/scan_artifacts_for_secrets.py`: clean.)

## 12. To unblock this comparison in a future sprint

A separate (and out-of-scope-here) operational sprint can:

1. Restore `data/oanda_h4_research.sqlite3` via
   `scripts/rehydrate_oanda_h4_store.py` against a credentialed OANDA
   practice account, **or** copy the file in from a previous restore.
2. Regenerate the seven CSVs:
   ```bash
   python scripts/export_lean_parity_data.py \
       --config configs/campaign_002_real_oanda.yaml \
       --output research/lean_parity/exports/campaign_002_h4/
   ```
3. Run:
   ```bash
   python scripts/run_backtrader_parity.py \
       --campaign CAMPAIGN_002 \
       --output research/backtrader_lane/results/campaign_002/
   ```
4. Compare:
   ```bash
   python scripts/compare_backtrader_parity.py \
       --campaign CAMPAIGN_002 \
       --backtrader-results research/backtrader_lane/results/campaign_002/ \
       --bespoke-reference research/lean_parity/campaign_002_h4_bespoke_reference.json \
       --output research/backtrader_lane/results/campaign_002/comparison/
   ```
5. Read the divergence classification and document the result in
   `docs/research/BACKTRADER_PARITY_CAMPAIGN_002_COMPARISON.md`.

The Backtrader-lane code in this branch needs no change for that to
happen — it is the actual-data run, not a code change.

## 13. Required disclosure

**This result cannot approve any strategy and does not enable
paper / demo / live trading.** It is a verification-infrastructure
preflight that establishes the Backtrader-lane pipeline end-to-end
and documents the data-availability gap that blocks the
apples-to-apples engine comparison. `strategy_evidence: false`.

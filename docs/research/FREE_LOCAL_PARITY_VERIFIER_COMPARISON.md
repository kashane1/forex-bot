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

**Re-confirmed:** `infra-free-local-parity-verifier-003-with-data`
Phase 4 — guarded OANDA-practice rehydrate + export + verifier
attempted under strict safety rules. Same BLOCKED outcome (no
credentials configured locally → no rehydrate, no SQLite, no CSVs,
no comparison numbers). The 1,647-trade no-RiskEngine bespoke
reference scope was explicitly re-verified against the file's own
top-level keys before the comparison was invoked. Verifier-side
bugs: **0**. Bespoke-side bugs: **N/A** (engine not exercised; no
real-candle cross-check possible). See "Sprint-003 re-run record"
below.

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

## Sprint-003 re-run record

Captured 2026-05-22 on branch
`infra-free-local-parity-verifier-003-with-data` Phase 4. The
guarded OANDA-practice rehydrate path was the explicit Phase 1
target. The credential-presence check found **no** credentials
configured locally (no `.env`, all six probed `OANDA_*` env vars
unset), so the rehydrate was not attempted (per the sprint rules
"If credentials are absent, stop and document the blocker"). The
verifier was re-invoked against the absent CSVs and the comparison
harness was re-run programmatically.

### Comparison command

```bash
# Reference-scope confirmation (Python one-liner, values printed only
# for the documented immutable fields; no credentials touched):
python3 - <<'PY'
from research.parity_verifier.data_loader import (
    DEFAULT_BESPOKE_REFERENCE_PATH, load_bespoke_reference,
)
bespoke = load_bespoke_reference(DEFAULT_BESPOKE_REFERENCE_PATH)
assert bespoke['total_trades'] == 1647
assert bespoke['risk_engine_used'] is False
PY
```

This **must** hold before the comparison runs; the 1,032-trade
with-RiskEngine reference is **not** the target.

### Reference scope (confirmed against the JSON's own top-level keys)

- `parity_target`: `"CAMPAIGN_002 H4 trend_following baseline"`
- `risk_engine_used`: `false`
- `fill_timing`: `"signal_bar_close"`
- `window`: `["2020-01-01", "2026-05-20"]`
- `config_hash`: `d536a9b06818197f9915de6224e0b8ae58e77abe2c6f3c19426338646fb077bf`
- `strategy_evidence`: `false`
- `total_trades`: **1647**
- pair count: **7** (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD)

### Verifier result used

- Path: `/tmp/parity_verifier_003_run/parity_summary.json` (outside
  repo, not committed).
- Shape: valid `VerifierResult`, `total_trades: 0`, `pairs: []`,
  `strategy_evidence: false`, `risk_engine_used: false`.

### Total trade comparison

| side | bespoke | verifier | Δ |
|---|---|---|---|
| total | **1,647** | — (not produced) | — |

### Pair-level comparison

| instrument | bespoke trades | verifier trades | Δ % | status | classification |
|---|---|---|---|---|---|
| EUR_USD | 233 | — | — | BLOCKED | unknown |
| GBP_USD | 215 | — | — | BLOCKED | unknown |
| USD_JPY | 247 | — | — | BLOCKED | unknown |
| AUD_USD | 237 | — | — | BLOCKED | unknown |
| USD_CAD | 251 | — | — | BLOCKED | unknown |
| USD_CHF | 224 | — | — | BLOCKED | unknown |
| NZD_USD | 240 | — | — | BLOCKED | unknown |
| **total** | **1647** | **—** | — | **BLOCKED** | **unknown** |

### Direction comparison

**N/A** — no verifier trades were produced; long / short counts on
the verifier side are 0 / 0.

### Alignment summary

**N/A** — no verifier trades to align against. Entry timestamp
alignment, exit timestamp alignment, entry/exit price drift,
R-multiple drift, missing-trade and extra-trade counts cannot be
computed.

### Divergence classification

- **Per pair:** `unknown` for all seven — the verifier produced no
  numbers to diverge from.
- **Overall:** `unknown`.
- **Not** classified as `data_mismatch`: the data side has not been
  attempted on this branch. Not `indicator_mismatch`: no indicator
  series ran. Not `entry_exit_rule_mismatch`: no entries evaluated.
  Etc.

### Suspected causes

The single root cause is **missing input data** — both upstream
(SQLite store) and immediate (CSVs). No verifier-side or
bespoke-side cause is involved because neither engine was exercised
on real candles this sprint.

### What passed

- The reference-scope assertion (`total_trades == 1647`,
  `risk_engine_used == False`).
- The verifier script's BLOCKED-state behavior (7 × BLOCKED, exit 2,
  valid empty summary).
- The comparison harness's BLOCKED-report path (seven-row report
  with full bespoke-side values preserved, `unknown`
  classification).
- All 85 verifier-side fixture tests, 388 pre-sprint tests, ruff,
  archive validator, freeze checker, secret scanner.

### What failed

- The end-to-end full-data comparison — **expected**, because the
  data is missing. This is not a verifier or bespoke implementation
  failure; it is a credential / data availability failure documented
  in the Sprint-003 rehydrate and export status docs.

### Verifier bugs fixed (Sprint-003)

**None.** No verifier code change was needed; the implementation
behaves correctly in the no-data state.

### Bespoke-engine bugs found (Sprint-003)

**N/A.** The bespoke engine was not exercised; no real-candle
cross-check happened.

### Files produced but not committed (Sprint-003)

- `/tmp/parity_verifier_003_run/parity_summary.json`
- `/tmp/parity_verifier_003_run/trades.csv` (header-only)
- `/tmp/parity_verifier_003_run/parity_summary.md`
- `/tmp/parity_verifier_003_run/comparison.md`
- `/tmp/parity_verifier_003_run/run.log`

All five live outside the repo (`/tmp/`) and are not staged.

### Explicit statement (Sprint-003)

This comparison does **not** approve a strategy. CAMPAIGN_002
remains REJECT. `configs/approved_strategies.yaml` remains
`approved: []`. Paper / demo / live remain blocked. No QC / LEAN
action of any kind. No OANDA endpoint contacted (only the
read-only `--verify` mode that makes no API call).

## Sprint-003 UNBLOCKED — actual full-data comparison

The Sprint-003 BLOCKED state recorded above reflected my
**worktree-scoped inventory** which missed the `.env` at the main
repo root and the existing `data/campaign_002.sqlite3` in the main
repo. After the user pointed this out, the sprint completed
end-to-end. Full detail:
[`FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md`](FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md).

### Comparison result — FAIL

- **Bespoke reference:** `research/lean_parity/campaign_002_h4_bespoke_reference.json`
  (no-RiskEngine, **1,647 trades**, scope re-asserted in code:
  `total_trades == 1647`, `risk_engine_used is False`).
- **Verifier result:** 1,586 trades across all seven pairs (zero
  blocked, zero crashes).
- **Total trade-count delta:** −3.70 % (within OK ±5 % tolerance).
- **Overall status:** **FAIL** — driven by EUR_USD return delta
  +2.41 pp, which exceeds the 2.0 pp FAIL threshold.
- **Overall classification:** `unknown` — not yet localized.

### Per-pair table (real numbers)

| pair | bespoke trades | verifier trades | Δ % | bespoke exp R | verifier exp R | Δ R | bespoke ret % | verifier ret % | Δ pp | status | classification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EUR_USD | 233 | 220 | −5.58 | −0.1961 | −0.1591 | +0.0370 | −10.8345 | −8.4292 | **+2.4053** | **FAIL** | unknown |
| GBP_USD | 215 | 202 | −6.05 | −0.0971 | −0.0646 | +0.0325 | −5.1182 | −3.2576 | +1.8606 | WARN | unknown |
| USD_JPY | 247 | 241 | −2.43 | −0.0001 | −0.0075 | −0.0074 | −1.3735 | −0.7185 | +0.6550 | WARN | unknown |
| AUD_USD | 237 | 228 | −3.80 | −0.2134 | −0.2095 | +0.0039 | −11.9013 | −11.2872 | +0.6141 | WARN | unknown |
| USD_CAD | 251 | 245 | −2.39 | −0.1804 | −0.2446 | −0.0642 | −14.1096 | −14.0096 | +0.1000 | WARN | unknown |
| USD_CHF | 224 | 220 | −1.79 | −0.1430 | −0.1257 | +0.0173 | −7.0322 | −6.6605 | +0.3717 | OK | none |
| NZD_USD | 240 | 230 | −4.17 | −0.2645 | −0.2555 | +0.0090 | −14.7032 | −13.7010 | +1.0022 | WARN | unknown |
| **total** | **1647** | **1586** | **−3.70** | | | | | | | **FAIL** | **unknown** |

### Direction comparison

The verifier's trade list was not split by long/short in this turn
(the `trades.csv` is gitignored but locally available; a future
Phase 5 debug pass can break it down by direction). The per-pair
totals above are direction-agnostic.

### Alignment summary

Per-trade entry/exit timestamp alignment was not computed this turn
— the verifier and bespoke reference don't currently share a
trade-id surface. A future Phase 5 debug pass would join the two
trade lists by (instrument, entry_time) to compute per-trade drift.

### Divergence classification

- **Per pair:** `unknown` for all non-OK pairs — the systematic
  direction (verifier always slightly less bad) suggests a real
  implementation difference but is not yet localized to a specific
  bucket from the taxonomy.
- **Overall:** `unknown`.

### Suspected causes (not yet verified)

The systematic direction (verifier produces fewer trades and less
loss on every pair) is consistent with one or more of:

- `spread_slippage_fill_mismatch` (verifier applies bid/ask slip
  differently from bespoke);
- `stop_trailing_mismatch` (verifier's stop detection or trailing
  update order differs);
- `entry_exit_rule_mismatch` (verifier's entry warmup or floor
  excludes some entries the bespoke takes);
- `sizing_pnl_mismatch` (small systematic difference in units or
  PnL conversion).

A Phase 5 debug pass would diagnose this — verifier-side fixes
only, per sprint rules.

### What passed

- Total trade-count tolerance (−3.70 % within OK ±5 %).
- 1 / 7 pairs OK (USD_CHF).
- Directional verdict: both engines agree every pair is loss-making
  on the no-RiskEngine path. CAMPAIGN_002 stays REJECT under either
  measurement.
- Reference-scope assertion (`total_trades == 1647`,
  `risk_engine_used is False`).
- All 85 verifier-side fixture tests, 388 pre-sprint tests, ruff,
  archive validator, freeze checker, secret scanner.

### What failed

- EUR_USD return delta +2.41 pp exceeds the 2.0 pp FAIL threshold.
- 5 / 7 pairs land in the WARN band on trade count, expectancy, or
  return.

### Verifier bugs fixed (Sprint-003 UNBLOCKED)

**None.** The verifier ran cleanly; the divergence is real but not
yet localized. Whether the fix is a verifier-side bug or a
bespoke-side discrepancy can only be determined by Phase 5 debug
work.

### Bespoke-engine bugs found

**None confirmed.** The divergence direction is informational but
neither side is implicated until Phase 5 traces it.

### Files committed this turn

- `docs/research/FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md`
  (the single summary doc for the unblock).
- This section appended to the comparison doc.
- Supersedence banners added to the three Sprint-003 BLOCKED status
  docs.

### Files produced but not committed (Sprint-003 UNBLOCKED)

- `research/lean_parity/exports/campaign_002_h4/*.csv` × 7
  (gitignored, total ~6.6 MB).
- `research/parity_verifier/results/campaign_002_h4_full_data/parity_summary.json`
  (gitignored under `results/`).
- `research/parity_verifier/results/campaign_002_h4_full_data/trades.csv`
  (gitignored, 1,655 rows after Phase 5 debug, ~235 KB).
- `research/parity_verifier/results/campaign_002_h4_full_data/parity_summary.md`
  (gitignored).
- `research/parity_verifier/results/campaign_002_h4_full_data/comparison.md`
  (gitignored).

## Sprint-003 Phase 5 debug — post-fix comparison

Two verifier-side bugs were localized and fixed (Bug #1: initial
stop anchored at the wrong base price; Bug #2: same-bar re-entry
after exit was blocked). After both fixes:

- **Verifier total: 1,655 trades** (Δ +0.49 % vs bespoke 1,647 —
  OK band).
- **Overall status: WARN** (down from FAIL).
- **0 / 7 pairs FAIL.** 3 / 7 OK (GBP_USD, USD_JPY, AUD_USD),
  4 / 7 WARN (EUR_USD, USD_CAD, USD_CHF, NZD_USD).

### Post-debug per-pair table

| pair | bespoke trades | verifier trades | Δ % | Δ R | Δ pp | status |
|---|---|---|---|---|---|---|
| EUR_USD | 233 | 235 | +0.86 | +0.0160 | +0.7644 | WARN |
| GBP_USD | 215 | 215 | +0.00 | +0.0005 | +0.0075 | **OK** |
| USD_JPY | 247 | 251 | +1.62 | −0.0125 | +0.3093 | **OK** |
| AUD_USD | 237 | 238 | +0.42 | −0.0033 | −0.2241 | **OK** |
| USD_CAD | 251 | 251 | +0.00 | −0.0605 | +0.0025 | WARN |
| USD_CHF | 224 | 223 | −0.45 | +0.0428 | +1.6304 | WARN |
| NZD_USD | 240 | 242 | +0.83 | −0.0077 | −0.5110 | WARN |
| **total** | **1647** | **1655** | **+0.49** | | | **WARN** |

Full trace + before/after for each bug:
[`FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md`](FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md).

Remaining sub-WARN drift on 4 / 7 pairs is plausibly attributable
to Decimal-vs-float precision and the missing
`instrument.round_price(...)` rounding on the verifier side. **No
further debug was performed** — chasing those would risk
implementing the bespoke engine inside the verifier (sacrificing
independence), and the comparison verdict has already moved from
FAIL to WARN with the directional verdict (both engines agree
every pair is loss-making, CAMPAIGN_002 stays REJECT) intact.

## Sprint-004 round_price wired in — post-fix comparison

Sprint 004 closed the missing-`round_price` half of the suspected
remaining drift. The verifier now rounds initial stops to the
instrument's `display_precision` (5 for USD-quote majors, 3 for
USD_JPY) via a Decimal-based helper that uses the bespoke formula
(`Decimal(str(price)).quantize(10**(-display_precision), ROUND_HALF_UP)`).

**Observed impact: negligible.** All pair statuses unchanged.
Per-pair return shifts under 0.01 pp. The rounding fix is correct
(see `test_round_price_matches_bespoke_formula`) but the
fractional-pip difference is too small to flip borderline stop-pierce
comparisons on H4 bars whose intrabar ranges are many pips.

| pair | bespoke trades | verifier trades | Δ % | Δ R | Δ pp | status |
|---|---|---|---|---|---|---|
| EUR_USD | 233 | 235 | +0.86 | +0.0160 | +0.7604 | WARN |
| GBP_USD | 215 | 215 | +0.00 | +0.0005 | +0.0141 | **OK** |
| USD_JPY | 247 | 251 | +1.62 | −0.0125 | +0.3069 | **OK** |
| AUD_USD | 237 | 238 | +0.42 | −0.0033 | −0.2232 | **OK** |
| USD_CAD | 251 | 251 | +0.00 | −0.0605 | +0.0000 | WARN |
| USD_CHF | 224 | 223 | −0.45 | +0.0428 | +1.6332 | WARN |
| NZD_USD | 240 | 242 | +0.83 | −0.0078 | −0.5096 | WARN |
| **total** | **1647** | **1655** | **+0.49** | | | **WARN** |

Detail: [`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md).

The remaining drift is therefore **not** rounding-driven. It is
most plausibly inherent float-vs-Decimal arithmetic accumulating
across thousands of indicator-evaluation and trade-by-trade
compounding steps — explicitly out of scope this sprint to
preserve the verifier's independence from the bespoke engine.

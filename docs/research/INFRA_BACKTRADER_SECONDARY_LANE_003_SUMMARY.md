# INFRA — Backtrader Secondary Lane 003 — Real Data Run — Summary

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-003-real-data-run`
**Sprint kind:** infrastructure / parity (NOT a strategy campaign)
**`strategy_evidence: false`**

## 0. Headline

**CAMPAIGN_002 PASS.** The Backtrader secondary lane drove all seven
H4 pairs end-to-end against real local-data CSVs, produced exactly
1 647 trades (bit-equal trade count to the bespoke no-RiskEngine
reference), and — after one targeted fix to the BT adapter's
R-multiple formula — every per-pair expectancy R, return %, win rate,
profit factor, and trade count agrees with bespoke within tight
tolerance (Δ expR ≤ 0.0014, Δ ret % ≤ 0.061 pp, Δ PF ≤ 0.002).

**Bug found and fixed:** the BT adapter's R formula divided
`risk_home` by `exit_price` for USD-base pairs, inflating R
magnitudes by ~`exit_price` on USD_CAD and USD_JPY. The bespoke
engine deliberately does **not** convert the R denominator
(`src/forex_bot/backtesting/engine.py:411-415`). The fix is two
lines in
`research/backtrader_lane/strategies/campaign_002_trend_following.py`
plus a new approximation flag and two new regression tests.

CAMPAIGN_002 remains **REJECT**. The BT lane corroborates that REJECT
verdict to sub-pip / sub-0.002-R precision across all seven pairs.

## 1. Branch + commits by phase

Branch: `infra-backtrader-secondary-lane-003-real-data-run` (from
`infra-backtrader-secondary-lane-002-real-data-run` @ `85ca90a`).

| phase | commit | description |
|---|---|---|
| 0 | `c1ab550` | plan + data found in main repo `data/campaign_002.sqlite3` |
| 1 | `51db36a` | seven CAMPAIGN_002 H4 CSVs regenerated; sha256 ✅ |
| 2 | `49205e4` | real CAMPAIGN_002 run — 1 647 trades, 7 pairs, no error |
| 4 fix | `fcf67c5` | BT-lane R-formula fix + 2 new regression tests |
| 3 + 4 doc | `20f1fa7` | comparison doc with before / after measurement |
| 5 | `e71ac4d` | CAMPAIGN_011 BLOCKED-by-design (structural prereqs) |
| 6 | (this) | sprint summary + evidence-index update + final validation |

## 2. Data restored / generated

**Source SQLite (read-only):**
`/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` — 115 MB,
local rehydrated OANDA-practice H4 candle store. Lives in the main
repo working directory; this worktree's `data/` is gitignored and
worktree-isolated.

**Generated (Phase 1, gitignored — NOT committed):**
`research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv` —
seven CSVs totaling ~6.5 MB. Each `data_sha256` matches its
committed `*.provenance.json` sidecar bit-for-bit.

## 3. Whether any OANDA / API call was made

**No.** Zero OANDA endpoints contacted. Zero `httpx` calls. Zero
credentials read. Zero env vars touched. Zero `.env` authored.
Path C (rehydration with credentials) was **not** taken — Path B
(regenerate from existing local SQLite) was used.

## 4. CAMPAIGN_002 Backtrader run status

**PASS.** 1 647 trades total. Per-pair trade counts:

```
EUR_USD 233  GBP_USD 215  USD_JPY 247  AUD_USD 237
USD_CAD 251  USD_CHF 224  NZD_USD 240             total 1 647
```

Every per-pair trade count matches the bespoke reference exactly.

Wall clock: ~10 s. No warnings. No errors. No OANDA env-var leak.

## 5. CAMPAIGN_002 comparison status

**PASS (overall).** Both passes documented in
`BACKTRADER_CAMPAIGN_002_REAL_COMPARISON_003.md`:

- Phase 3 initial harness: **PASS** on trade counts; silent on
  expectancy R / return % (those fields are not currently emitted by
  the BT runner summary, so the harness's `_derive_*` stubs return
  None and treat them as agreeing).
- Manual richer comparison (computed from `backtrader_trades.jsonl`):
  USD_CAD initial Δ expR = −0.0605 (material, would classify as
  `SIZING_OR_PNL_MISMATCH`); USD_JPY initial Δ expR = −0.0180
  (suspicious, same root cause).
- Phase 4 fix landed; **post-fix** all 7 pairs Δ expR ≤ 0.0014, all
  return-% within ±0.061 pp, all PF within ±0.002.

## 6. CAMPAIGN_002 divergence classification

**Pre-fix:** `SIZING_OR_PNL_MISMATCH` on USD-base pairs (the
R-formula bug, in the `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md`
§7 vocabulary).

**Post-fix:** **`PASS`** on every pair, every metric. The remaining
sub-bps drift on EUR_USD / NZD_USD / USD_CHF / USD_CAD is the
documented float-vs-Decimal precision noise (also documented for the
parity_verifier in `FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md`).

## 7. Backtrader-lane bugs fixed

**One fix:**

- `research/backtrader_lane/strategies/campaign_002_trend_following.py`
  `_close_trade`: removed the
  `if base_ccy == "USD": risk_home = risk_home / exit_price`
  adjustment that was inflating R magnitudes on USD-base pairs by
  ~`exit_price`. Renamed `risk_home` → `risk_distance` to match the
  bespoke convention. Added inline reference to
  `src/forex_bot/backtesting/engine.py:411-415`. Added approximation
  flag `R_FORMULA_MATCHES_BESPOKE`.
- 2 new tests in `tests/unit/backtrader_lane/test_campaign_002_adapter.py`:
  - `test_r_multiple_matches_bespoke_formula_for_usd_base_pair`
  - `test_r_multiple_is_pure_function_of_pnl_and_entry_minus_stop`

## 8. Bespoke-engine bugs found

**None.** The bespoke engine's R formula
(`risk_distance = (entry − stop) × units; r = pnl / risk_distance`)
is the canonical CAMPAIGN_002 convention. The BT lane was matched to
bespoke — bespoke was not changed.

## 9. CAMPAIGN_011 status

**BLOCKED-by-design (Sprint 003).** Phase 5's precondition was met
(CAMPAIGN_002 PASS), but two structural prerequisites are missing
that would make a CAMPAIGN_011 comparison apples-to-oranges:

1. No published no-RiskEngine bespoke reference for CAMPAIGN_011
   (the campaign ran with the RiskEngine wired in). A
   no-RiskEngine reference is a separate bespoke-side operation.
2. CAMPAIGN_011's bespoke artefacts are per-fold walk-forward (8
   folds × 7 pairs = 56 cells); the BT-lane runner is full-window
   single-run. A meaningful fold-level comparison would need a
   fold-aware runner extension (new feature).

Per the prompt's "do not let CAMPAIGN_011 distract from completing
CAMPAIGN_002 first," this sprint deliberately did **not** author
`research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`.
The carry-forward implementation prompt (frozen parameters, R1–R8
rules, approximation flags, test plan) remains at
`BACKTRADER_CAMPAIGN_011_BLOCKED_002.md` §4, supplemented in
`BACKTRADER_CAMPAIGN_011_BLOCKED_003.md` with the new requirement
that the future adapter use the post-fix R formula.

CAMPAIGN_011 remains REJECT (null-model anchor by design).

## 10. Unsupported / approximated behaviour

Same set as Sprint 001, plus the new `R_FORMULA_MATCHES_BESPOKE` flag:

```
MID_OHLC_DERIVED          # mid OHLC derived from bid/ask
BAR_OPEN_TIMESTAMP        # index is bar OPEN time, 17:00-NY aligned
HALF_SPREAD_CLOSE         # close-time half-spread only
BACKTRADER_INDICATORS     # EMA + ATR via bt.indicators
DONCHIAN_PRIOR_BARS_ONLY  # manual deque; bt's stock would lookahead
BACKTRADER_BROKER_BYPASSED # manual one-position state machine
MANUAL_SIZING_RISK_FRACTION
TRAILING_STOP_RATCHET
NO_RISK_ENGINE
NO_FINANCING
R_FORMULA_MATCHES_BESPOKE # NEW Sprint 003: no quote→home conversion
```

## 11. Local generated files not committed

| location | contents | rule |
|---|---|---|
| `research/lean_parity/exports/campaign_002_h4/*.csv` | seven Phase-1-regenerated H4 CSVs (~6.5 MB) | gitignored |
| `research/backtrader_lane/results/campaign_002_real_data_003/` | pre-fix run artefacts (manifest, summary, metrics, 1 647-line trades JSONL, log) | gitignored |
| `research/backtrader_lane/results/campaign_002_real_data_003_post_fix/` | post-fix run + comparison artefacts | gitignored |
| `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` | source SQLite (115 MB, read-only) | already gitignored |

## 12. Validation commands run

```bash
python -m pytest tests/unit/backtrader_lane -q       # 77 PASS  (75 prior + 2 new)
python -m pytest -q                                  # full suite — see final §
ruff check src tests scripts research/backtrader_lane # All checks passed
python scripts/check_research_freeze.py              # ALL CHECKS PASSED
python scripts/validate_research_archive.py          # ALL CHECKS PASSED
python scripts/scan_artifacts_for_secrets.py         # PASSED
```

The full pytest re-run is in §14.

## 13. Safety state

- `configs/approved_strategies.yaml` byte-identical to `main`:
  `approved: []`.
- `src/forex_bot/` untouched (no diff vs parent branch).
- `configs/paper.yaml`, `configs/practice.yaml` untouched.
- `backtests/` untouched.
- `research/lean_parity/lean_parity_config.json` untouched.
- `research/lean_parity/campaign_002_h4_bespoke_reference.json` untouched.
- All seven `research/lean_parity/exports/campaign_002_h4/*.provenance.json`
  untouched (the exporter rewrote them with a new `exported_at`
  timestamp; reverted via `git checkout --` so the commit is clean).
- No `.env` staged. No SQLite staged. No bulk CSV staged. No large
  raw Backtrader output staged.

Files added on this branch (relative to sprint 002):

```
docs/research/BACKTRADER_REAL_DATA_RUN_003_PLAN.md           NEW
docs/research/BACKTRADER_REAL_DATA_PREFLIGHT_003.md          NEW
docs/research/BACKTRADER_CAMPAIGN_002_REAL_RUN_003.md        NEW
docs/research/BACKTRADER_CAMPAIGN_002_REAL_COMPARISON_003.md NEW
docs/research/BACKTRADER_CAMPAIGN_011_BLOCKED_003.md         NEW
docs/research/INFRA_BACKTRADER_SECONDARY_LANE_003_SUMMARY.md NEW (this)
research/backtrader_lane/strategies/campaign_002_trend_following.py MODIFIED (R-formula fix + flag)
tests/unit/backtrader_lane/test_campaign_002_adapter.py      MODIFIED (+2 tests)
docs/research/EVIDENCE_INDEX.md                              +1 section
docs/research/EVIDENCE_MANIFEST.json                         +6 entries
```

## 14. Files to review first

1. [`BACKTRADER_CAMPAIGN_002_REAL_COMPARISON_003.md`](BACKTRADER_CAMPAIGN_002_REAL_COMPARISON_003.md) — the load-bearing result doc: bug found, fix applied, before/after measurement, classification `PASS`.
2. [`BACKTRADER_REAL_DATA_PREFLIGHT_003.md`](BACKTRADER_REAL_DATA_PREFLIGHT_003.md) — proves the seven regenerated CSVs match committed sha256 sidecars and the lane ran without any OANDA call.
3. [`BACKTRADER_CAMPAIGN_002_REAL_RUN_003.md`](BACKTRADER_CAMPAIGN_002_REAL_RUN_003.md) — the run record (1 647 trades, per-pair table).
4. [`BACKTRADER_CAMPAIGN_011_BLOCKED_003.md`](BACKTRADER_CAMPAIGN_011_BLOCKED_003.md) — why CAMPAIGN_011 in this sprint is apples-to-oranges; the two structural prerequisites.
5. [`research/backtrader_lane/strategies/campaign_002_trend_following.py`](../../research/backtrader_lane/strategies/campaign_002_trend_following.py) — see the `_close_trade` method, lines around 340 — the R-formula fix.

## 15. Recommended next branch

**`infra-bespoke-campaign-011-norisk-reference-001`** — produce a
no-RiskEngine CAMPAIGN_011 bespoke reference (or per-fold no-RiskEngine
references) by running the bespoke engine in `risk_engine=None` mode.
This is a bespoke-engine operation; it does NOT touch the Backtrader
lane and does NOT approve any strategy. Once that reference exists,
the natural follow-up is
**`infra-backtrader-secondary-lane-004-campaign-011`** to port +
run + compare CAMPAIGN_011 per the spec in
`BACKTRADER_CAMPAIGN_011_BLOCKED_002.md` §4 + sprint-003 R-formula
note.

For a strictly Backtrader-lane-only follow-up, **fold-aware runner
support** is the other independent next step — but only worthwhile
if walk-forward parity becomes a target (currently it is not).

## 16. Required disclosure

This sprint **cannot approve any strategy** and does **not** enable
paper / demo / live trading. CAMPAIGN_002 remains **REJECT** —
the BT lane now corroborates that REJECT at sub-pip precision.
CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain
rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked. `strategy_evidence: false`.

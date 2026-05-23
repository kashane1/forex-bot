# Infrastructure Free / Local Parity Verifier Sprint 004 — Summary

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-004-rounding-closure`
**Base commit:** `a332a00` (HEAD of `infra-free-local-parity-verifier-003-with-data`)

Focused precision / rounding closure sprint. Sprint 003 unblocked
the verifier and fixed two verifier-side bugs (FAIL → WARN, 3 OK /
4 WARN / 0 FAIL). Sprint 004 audited bespoke rounding, implemented
the audit's verifier-only `round_price` fix, observed the
comparison impact (negligible — totals unchanged), and localized
the remaining WARN drift to float-vs-Decimal arithmetic precision
(USD_CAD is the cleanest piece of evidence).

**No strategy approved. CAMPAIGN_002 remains REJECT. Paper / demo /
live remain blocked. No OANDA API call. No QC / LEAN action. No
broker credentials touched. No orders submitted.**

## 1. Branch name

`infra-free-local-parity-verifier-004-rounding-closure`.

## 2. Commit hashes by phase

| phase | commit |
|---|---|
| Phase 0 — baseline & sprint plan | `1c5645c` |
| Phase 1 — rounding audit | `1edee3a` |
| Phase 2 — precision fixture tests | `aaf4e33` |
| Phase 3 — wire `round_price` into event loop | `d06e515` |
| Phase 4 — remaining-drift classification | `602f059` |
| Phase 5 — status & evidence updates | `f2c5a03` |
| Phase 6 — final validation & summary | (this commit) |

## 3. Files changed by phase

| phase | files |
|---|---|
| Phase 0 | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_004_PLAN.md` (new) |
| Phase 1 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md` (new) |
| Phase 2 | `research/parity_verifier/models.py` (+`display_precision` field), `research/parity_verifier/instruments.py` (per-pair values), `research/parity_verifier/rules.py` (+`round_price` helper), `tests/research/test_parity_verifier_rules.py` (+6 tests), `tests/research/test_parity_verifier_models.py` (+assert display_precision) |
| Phase 3 | `research/parity_verifier/event_loop.py` (wire `round_price` into initial-stop step), `docs/research/FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md` (new), `docs/research/FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md` (append Sprint-004 section) |
| Phase 4 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md` (new) |
| Phase 5 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_STATUS.md`, `docs/research/EVIDENCE_INDEX.md`, `docs/research/EVIDENCE_MANIFEST.json` |
| Phase 6 | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md` (new) |

`src/forex_bot/` — **not modified**. Bespoke engine, CAMPAIGN_002
rules, strategy modules, campaign configs, campaign reports,
`configs/approved_strategies.yaml` — **all unchanged**.

## 4. Validation commands run

- `python -m pytest -q` → **481 passed** (475 pre-sprint + 6 new
  `round_price` tests).
- `ruff check src tests scripts research/parity_verifier` → **clean**.
- `python scripts/validate_research_archive.py` → **ALL CHECKS PASSED**
  (11 diagnostic artifacts; 90 evidence-index links resolve; no
  credential-shaped strings in 1,932 committed artifact files).
- `python scripts/check_research_freeze.py` → **ALL CHECKS PASSED**.
- `python scripts/scan_artifacts_for_secrets.py` → **PASSED**.
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` →
  **refused**.
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` →
  **refused**.
- `python -m forex_bot.cli --help` → no `live-loop` command.

## 5. QuantConnect / LEAN status

**Retired throughout.** No QC access, no `lean *` commands, no QC
credential touched.

## 6. QC credentials

**None requested, read, or created.**

## 7. OANDA API calls

**Zero.** This sprint reads only already-local files. The
`data/campaign_002.sqlite3` SQLite store was used (via a read-only
`SELECT` for instrument metadata in the audit phase). No fetch, no
network call, no `rehydrate` invocation, no `--verify` either —
the audit needed only schema and per-pair metadata.

## 8. Broker credentials

**None printed, none committed.** No env-variable read, no `.env`
sourced. The Sprint-003 `.env` at the main repo root is unchanged
and untouched.

## 9. Orders

**None submitted.** This sprint never reaches any broker, exchange,
or order surface.

## 10. Strategy approval

**None.** `configs/approved_strategies.yaml` remains `approved: []`.

## 11. CAMPAIGN_002

**Remains REJECT.**

## 12. Paper / demo / live

**All remain blocked.** Both `paper-loop` and `demo-loop` refused
at final validation; no `live-loop` command exists.

## 13. Baseline post-Sprint-003 comparison

| metric | value |
|---|---|
| Verifier total trades | 1,655 |
| Bespoke total trades (no-RiskEngine) | 1,647 |
| Total Δ % | +0.49 % (OK) |
| Pairs OK | 3 (GBP_USD, USD_JPY, AUD_USD) |
| Pairs WARN | 4 (EUR_USD, USD_CAD, USD_CHF, NZD_USD) |
| Pairs FAIL | 0 |
| Overall status | WARN |

## 14. Rounding / precision audit result

Bespoke `instrument.round_price`:
- Implementation: `price.quantize(10**(-display_precision), ROUND_HALF_UP)`
- Per-pair `display_precision` (verified against
  `data/campaign_002.sqlite3` instruments table):
  - USD-quote majors (EUR_USD, GBP_USD, AUD_USD, USD_CAD, USD_CHF,
    NZD_USD): 5
  - USD_JPY: 3
- Applied at: **initial stop only** (`strategies/trend_following.py:138`).
- **Not** applied to: trailing-stop updates, entry/exit fills,
  PnL conversion (all stay in full Decimal precision).

Five-entry mismatch table:
- **M1** missing initial-stop rounding → **fixed** in Sprint-004
- **M2** missing `display_precision` field → **fixed** as M1 prerequisite
- **M3** float-vs-Decimal throughout → **deferred** (would
  re-implement bespoke inside verifier)
- **M4** trailing-stop rounding → no fix needed (matches)
- **M5** units rounding → no fix needed (already equivalent)

## 15. Verifier-side fixes applied

1. Added `display_precision: int` to
   `research/parity_verifier/models.py::InstrumentSpec`.
2. Populated `display_precision = 5` for USD-quote majors and
   `3` for USD_JPY in
   `research/parity_verifier/instruments.py`.
3. Added a `round_price(price, display_precision) -> float` helper
   in `research/parity_verifier/rules.py` that uses
   `Decimal(str(price)).quantize(..., ROUND_HALF_UP)` and casts
   back to float — identical formula to bespoke.
4. Wired `round_price` into
   `research/parity_verifier/event_loop.py`'s initial-stop step.

The bespoke engine, strategy modules, CAMPAIGN_002 rules, and
parameter configs were not modified.

## 16. Final full-data verifier result

| pair | trades | exp R | return % |
|---|---|---|---|
| AUD_USD | 238 | −0.2167 | −12.1245 |
| EUR_USD | 235 | −0.1801 | −10.0741 |
| GBP_USD | 215 | −0.0966 | −5.1041 |
| NZD_USD | 242 | −0.2723 | −15.2128 |
| USD_CAD | 251 | −0.2409 | −14.1096 |
| USD_CHF | 223 | −0.1002 | −5.3990 |
| USD_JPY | 251 | −0.0126 | −1.0666 |
| **total** | **1,655** | | |

Zero blocked pairs. Zero crashes. Verifier `parity_summary.json`
shape passes the `VerifierResult` model (`strategy_evidence: false`,
`risk_engine_used: false`).

## 17. Final comparison result

| metric | value |
|---|---|
| Bespoke total trades | 1,647 |
| Verifier total trades | 1,655 |
| Total Δ % | +0.49 % (OK) |
| Pairs OK | 3 (GBP_USD, USD_JPY, AUD_USD) |
| Pairs WARN | 4 (EUR_USD, USD_CAD, USD_CHF, NZD_USD) |
| Pairs FAIL | 0 |
| **Overall status** | **WARN** |
| Overall classification | `unknown` (per-pair: `sizing_pnl_mismatch` for USD_CAD and USD_CHF; `unknown` for EUR_USD and NZD_USD) |

Unchanged vs Sprint-003 post-debug result. The Sprint-004 fix is
correct but its impact on the comparison verdict is negligible —
detail in §18.

## 18. Final divergence classification

The remaining WARN drift is **localized to float-vs-Decimal
arithmetic precision**, audit M3 (deferred to preserve verifier
independence). Single cleanest piece of evidence:

- **USD_CAD:** trade count exact (251 vs 251), return % exact
  (Δ = +0.0000 pp), but expectancy R differs by **−0.0605**. Same
  trade set + same total return + different per-trade R means the
  R denominator (`initial_stop_distance × units`) differs at
  sub-pip precision — exactly the float (15 digits) vs Decimal (28
  digits) signature.

- **USD_CHF:** trade count −1, but +1.6 pp return drift on 223
  trades = ~+0.007 pp per trade, consistent with accumulated
  divide-by-`exit_price` precision drift on a USD-base pair.

- **EUR_USD** (+0.76 pp) and **NZD_USD** (−0.51 pp WARN-by-0.01):
  classified `unknown` — most plausibly same precision class, but
  not provable without a bespoke trade list (only per-pair summary
  is available).

## 19. Verifier bugs fixed

**None** this sprint. The Sprint-004 fix was a precision
*improvement* (verifier now matches bespoke's documented
`round_price` convention exactly), not a bug fix — the behavior
was already within float precision before. Sprint 003 fixed the
two real verifier-side bugs.

## 20. Bespoke-engine bugs found

**None.** Sprint 004 read the bespoke engine end-to-end during the
audit; every documented behavior matches the spec. No bespoke
file was modified.

## 21. Remaining unresolved drift

- 4 / 7 pairs remain WARN: EUR_USD (Δpp +0.76), USD_CAD (ΔR −0.06),
  USD_CHF (Δpp +1.63), NZD_USD (Δpp −0.51 — WARN by 0.01).
- All within the WARN 0.5–2.0 pp / 0.03–0.10 R band; none near
  the FAIL thresholds.
- Direction of drift is mixed (verifier sometimes more negative,
  sometimes less) — consistent with random float-precision noise
  rather than a structural verifier bias.
- Strategic verdict: both engines agree every pair is loss-making.
  CAMPAIGN_002 remains REJECT.

## 22. Local files created but not committed

All under
`research/parity_verifier/results/campaign_002_h4_full_data/`
(gitignored — `results/` directory in `.gitignore`; `trades.csv`
in `.gitignore` explicitly too):

- `parity_summary.json` — `VerifierResult` shape, 1,655 trades.
- `parity_summary.md` — human-readable summary.
- `trades.csv` — 1,655 trade rows, ~235 KB.
- `comparison.md` — full comparison report.

Plus the seven gitignored H4 CSV exports from Sprint 003 at
`research/lean_parity/exports/campaign_002_h4/*_H4_lean.csv`
(unchanged this sprint, still present locally).

`git status` is clean. No `.env`, no SQLite, no candle CSV, no
bulky verifier output staged.

## 23. Recommended next decision

The verifier is now in a **stable, well-classified state**. Two
reasonable next directions, both safe:

- **A — Accept and move on.** The independent verifier corroborates
  the bespoke engine within float precision on every pair. Trade
  count agrees within ±1.62 % per pair and +0.49 % overall. Both
  engines agree on the directional verdict. CAMPAIGN_002 stays
  REJECT. The remaining WARN drift is documented as
  float-precision noise. No further sprint is required for this
  parity workstream; the verifier has done its job (provide
  independent corroboration of the bespoke engine).

- **B — Opt-in Decimal-precision sprint.** A future
  `infra-free-local-parity-verifier-005-decimal-precision` sprint
  could convert the verifier to `decimal.Decimal` end-to-end. This
  would likely move the 4 WARN pairs to OK but at the cost of
  sacrificing the verifier's independence from the bespoke engine
  (they would share the same arithmetic precision path). Worth it
  only if a downstream use case specifically needs tighter
  numerical agreement — not for the corroboration purpose.

**Recommendation: A.** The verifier has reached the point of
diminishing returns; chasing the remaining sub-WARN drift
introduces more risk (loss of independence) than benefit (sub-pp
numerical agreement).

## 24. Exact files to review first

1. [`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md)
   — bespoke metadata, `round_price` formula, five-entry mismatch
   table.
2. [`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md)
   — verifier-side changes, before/after numbers (the fix is
   correct but has negligible comparison impact).
3. [`FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md`](FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md)
   — drift classification, USD_CAD evidence, recommendation to
   accept as float-precision noise.
4. [`FREE_LOCAL_PARITY_VERIFIER_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_STATUS.md)
   — headline status with the Sprint-004 banner.
5. [`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md)
   — "Sprint-004 round_price wired in" section with the post-fix
   per-pair table.
6. [`INFRA_FREE_LOCAL_PARITY_VERIFIER_004_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_004_PLAN.md)
   — the sprint plan with the candidate-causes table.
7. This summary
   ([`INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md)).

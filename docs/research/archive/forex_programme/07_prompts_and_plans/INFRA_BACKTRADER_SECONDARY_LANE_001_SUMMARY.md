# INFRA — Backtrader Secondary Lane 001 — Summary

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-001`
**Sprint kind:** infrastructure / parity (NOT a strategy campaign)
**`strategy_evidence: false`**

## 0. Headline

A second independent local verification lane — built on top of the
canonical `backtrader 1.9.78.123` Python package — is now scaffolded,
unit-tested, and integration-tested against synthetic fixtures. The
first real end-to-end CAMPAIGN_002 comparison is BLOCKED on local data
availability (gitignored H4 CSVs + gitignored source SQLite); the
runner and harness correctly produce BLOCKED artefacts and report no
spurious trades or verdict changes.

> **No strategy approved. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
> CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
> CAMPAIGN_014 remains scaffold-only. `configs/approved_strategies.yaml`
> remains `approved: []`. Paper / demo / live remain blocked.**

## 1. Branch + commits by phase

Branch: `infra-backtrader-secondary-lane-001`.

| phase | commit | description |
|---|---|---|
| 0 | `2c38dc4` | plan doc — `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md` |
| 1 | `431dfa0` | install + smoke test — `backtrader 1.9.78.123`, 7 tests PASS |
| 2 | `ed7655a` | data adapter — Lean H4 CSV + provenance sha-validated, 15 tests PASS |
| 3 | `42b03c1` | runner contract — `scripts/run_backtrader_parity.py`, 17 tests PASS |
| 4 | `a4875a8` | CAMPAIGN_002 adapter — `trend_following 0.1.0-baseline-frozen` port, 20 tests PASS |
| 5 | `d45c5ca` | comparison harness — `scripts/compare_backtrader_parity.py`, 16 tests PASS |
| 6 | `ada15e9` | first real comparison — BLOCKED, end-to-end pipeline verified |
| 7 | `1521f9d` | second campaign — BLOCKED with scoped next-step prompt |
| 8 | (this) | sprint summary |

## 2. Files changed (by phase, with line counts)

```
.gitignore                                          |    6 +
docs/research/
  INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md       |  377 +
  BACKTRADER_INSTALL_AND_SMOKE_RESULT.md            |  153 +
  BACKTRADER_DATA_ADAPTER_SPEC.md                   |  205 +
  BACKTRADER_RUNNER_CONTRACT.md                     |  231 +
  BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md              |  198 +
  BACKTRADER_PARITY_COMPARISON_SPEC.md              |  201 +
  BACKTRADER_PARITY_FIRST_RESULT.md                 |  218 +
  BACKTRADER_SECOND_CAMPAIGN_BLOCKED.md             |  137 +
  INFRA_BACKTRADER_SECONDARY_LANE_001_SUMMARY.md    |  (this file)
  EVIDENCE_INDEX.md                                 |   (+1 section)
  EVIDENCE_MANIFEST.json                            |   (+9 entries)
pyproject.toml                                      |    6 +
research/backtrader_lane/
  __init__.py                                       |   25 +
  smoke.py                                          |  167 +
  data_adapter.py                                   |  399 +
  runner.py                                         |  671 +
  compare.py                                        |  521 +
  strategies/__init__.py                            |   17 +
  strategies/campaign_002_trend_following.py        |  580 +
scripts/
  run_backtrader_parity.py                          |  181 +
  compare_backtrader_parity.py                      |  150 +
tests/unit/backtrader_lane/
  __init__.py                                       |    0 +
  test_smoke.py                                     |  129 +
  test_data_adapter.py                              |  273 +
  test_runner.py                                    |  313 +
  test_campaign_002_adapter.py                      |  430 +
  test_compare.py                                   |  315 +
  fixtures/__init__.py                              |    0 +
  fixtures/build_tiny_csv.py                        |  119 +
  fixtures/TEST_PAIR_H4_lean.csv                    |   13 +
  fixtures/TEST_PAIR_H4_lean.provenance.json        |   16 +
```

Total: ~6,100 LOC of new code + doc; **zero** lines deleted /
modified under `src/forex_bot/`.

## 3. Dependency status

| package | version | role |
|---|---|---|
| `backtrader` | `1.9.78.123` | opt-in research extra (`pip install -e .[backtrader-lane]`); not a runtime dep of the bot |
| `pandas` | ≥ 2.2 (existing) | feed construction |
| `pydantic` | ≥ 2.6 (existing) | unchanged — adapter does not use Pydantic models |

`pyproject.toml` adds the `backtrader-lane = ["backtrader>=1.9.78,<2.0"]`
optional dependency only. If the extra is not installed, every
backtrader-lane test skips via `pytest.importorskip`, leaving the rest
of the repo's 1104 tests untouched.

## 4. Backtrader version

`1.9.78.123` (MIT, pure-Python wheel from PyPI). Imports cleanly under
the repo's `filterwarnings = ["error", ...]` pytest config.

## 5. Data adapter status

**Complete + tested.** The Phase 2 adapter reads the same CSV format
the existing Lean parity export bundle uses (defined in
`research/lean_parity/lean_h4_export_format.md`), validates each CSV's
SHA-256 against the committed `*.provenance.json` sidecar, enforces
monotonic 4h-spaced timestamps and OHLC invariants on derived mid
prices, and surfaces three documented approximation flags
(`MID_OHLC_DERIVED`, `BAR_OPEN_TIMESTAMP`, `HALF_SPREAD_CLOSE`) to the
runner.

## 6. Runner status

**Complete + tested.** Emits exactly the five documented artefacts
(`run_manifest.json`, `backtrader_summary.json`,
`backtrader_trades.jsonl`, `backtrader_metrics.json`,
`run_log_summary.md`). Includes a manifest sanitiser that refuses to
keep any `OANDA_TOKEN` / `OANDA_API_TOKEN` / `OANDA_ACCOUNT_ID` /
`OANDA_ACCOUNT` name OR value in the rendered manifest text. CLI
exits 0 on success / 2 on bad arg. Manifest carries the data
provenance sha + every approximation flag.

## 7. First campaign selected

**CAMPAIGN_002** — H4 `trend_following 0.1.0-baseline-frozen`.

Selection rationale ([`BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md`](BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md) §1):

- Bespoke no-RiskEngine reference is a single committed JSON (1,647
  trades, per-pair expectancy / return / PF / win-rate / drawdown).
- Lean mapping spec pins every rule, indicator, fill, sizing formula,
  and approximation in one place.
- Existing `research/parity_verifier/` lane provides a second
  independent re-implementation to cross-reference.

## 8. First campaign run status

**BLOCKED (Phase 6).** Real CAMPAIGN_002 H4 CSVs
(`research/lean_parity/exports/campaign_002_h4/*.csv`) are gitignored
and the rehydrated source SQLite
(`data/oanda_h4_research.sqlite3`) is also gitignored and absent in
this worktree. Preflight + actual run both correctly reported every
requested instrument as `BLOCKED`; no fake trade was written.

## 9. First comparison status

**BLOCKED (Phase 6).** The comparison harness loaded the Backtrader
summary (0 pairs) and the bespoke reference (7 pairs), classified each
pair as `BLOCKED`, and rolled up to overall `BLOCKED` — the
documented expected outcome.

## 10. Second campaign status

**BLOCKED, deferred (Phase 7).** Implementing a CAMPAIGN_011 port in
this sprint while the verification target is unreachable would be
infra for its own sake. The recommended second campaign is
**CAMPAIGN_011 `random_entry_anchor`** for the future unblock sprint,
because it exercises a different failure mode (deterministic SHA-256
seed reproducibility, minimal indicator surface) — see
`BACKTRADER_SECOND_CAMPAIGN_BLOCKED.md` §2 for the scoped 6-step
next-sprint prompt.

## 11. Divergence classifications

| campaign | classification |
|---|---|
| CAMPAIGN_002 | `BLOCKED` (Phase 6 — first comparison) |
| CAMPAIGN_011 | (not attempted; recommended target for Phase 7 of a future sprint) |

## 12. Known Backtrader limitations / approximations

Documented in `BACKTRADER_RUNNER_CONTRACT.md` §6 and
`BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md` §3:

- `MID_OHLC_DERIVED` (data) — Backtrader sees mid; bid/ask carried separately.
- `BAR_OPEN_TIMESTAMP` (data) — index value is the bar OPEN time.
- `HALF_SPREAD_CLOSE` (data) — close-time half-spread carried only.
- `BACKTRADER_INDICATORS` (adapter) — `bt.indicators.ExponentialMovingAverage`
  + `AverageTrueRange` (Wilder); early-warmup seeding may produce sub-pip
  differences in the first few hundred bars.
- `DONCHIAN_PRIOR_BARS_ONLY` (adapter) — manual prior-bars deque
  (Backtrader's stock `Highest`/`Lowest` includes the current bar).
- `BACKTRADER_BROKER_BYPASSED` (adapter) — strategy maintains its own
  one-position state machine; the Cerebro broker is **not** used for
  fills.
- `MANUAL_SIZING_RISK_FRACTION` (adapter) — manual sizing; sub-bps
  drift from Decimal-vs-float precision is expected.
- `TRAILING_STOP_RATCHET` (adapter) — same multiple as the initial
  stop, per CAMPAIGN_002 spec.
- `NO_RISK_ENGINE` (adapter) — spread / session / loss-limit gates are
  NOT modelled (matches the no-RiskEngine bespoke reference at 1,647
  trades).
- `NO_FINANCING` (lane-wide) — financing/swap not modelled either side;
  comparison is pre-financing only.

## 13. Bugs found

- **Bespoke-engine bug:** **none found** in this sprint. The Phase 6
  comparison did not produce a real comparison signal, so no bespoke
  behaviour was contradicted.
- **Backtrader-adapter bug:** **none found.** The Phase 4 adapter's
  pure helpers (`_round_price`, `_fill_entry_price`, `_size_position`,
  `_trade_pnl`) bit-match the values the mapping spec specifies; a
  flat 260-bar synthetic fixture produces zero trades (warmup +
  no-lookahead honoured); a 400-bar fixture with a controlled breakout
  produces a deterministic long entry; two runs on the same fixture
  produce bit-identical trade JSONL.

## 14. Verdict / approval status

| campaign | verdict | changed by this sprint? |
|---|---|---|
| CAMPAIGN_002 | REJECT | NO |
| CAMPAIGN_010 | REJECT | NO |
| CAMPAIGN_011 | REJECT (null-model anchor) | NO |
| CAMPAIGN_012 | REJECT | NO |
| CAMPAIGN_013 | REJECT | NO |
| CAMPAIGN_014 | scaffold-only | NO |

`configs/approved_strategies.yaml` — byte-identical to `main`:
**`approved: []`**.

## 15. Paper / demo / live status

**Blocked.** All loops refuse every configured strategy (verified by
`scripts/check_research_freeze.py`).

## 16. Broker / API / credential usage

**None.** Verified:

- No new `httpx` call site against any OANDA endpoint.
- No `forex_bot.broker` / `forex_bot.execution` / `forex_bot.loops`
  import in any new file (greppable tests enforce).
- No `backtrader.brokers.oandabroker` / `backtrader.stores.oandastore`
  / `backtrader.feeds.oanda` import anywhere in the new tree
  (greppable tests enforce).
- No LEAN / QuantConnect import (greppable tests enforce).
- The runner manifest sanitiser refuses to keep any `OANDA_TOKEN` /
  `OANDA_API_TOKEN` / `OANDA_ACCOUNT_ID` / `OANDA_ACCOUNT` key OR
  value (test-enforced).
- `scripts/scan_artifacts_for_secrets.py` PASS.

## 17. Local generated files not committed

| location | content | rule |
|---|---|---|
| `research/backtrader_lane/results/` | per-run BT outputs | gitignored (new rule, `.gitignore` line ~131) |
| `research/backtrader_lane/exports/**/*.csv` | reserved for any future BT-only export | gitignored (new rule) |
| `/tmp/bt_c002_preflight/`, `/tmp/bt_c002_compare/` | Phase 6 preflight artefacts | outside repo; not committed |

## 18. Files to review first

1. `docs/research/INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md` — the
   non-goals + safety invariants.
2. `docs/research/BACKTRADER_PARITY_FIRST_RESULT.md` — the BLOCKED
   end-to-end Phase 6 result.
3. `docs/research/BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md` — why
   CAMPAIGN_002 was chosen + the rules-implemented table.
4. `docs/research/BACKTRADER_RUNNER_CONTRACT.md` — the runner's
   inputs, outputs, failure modes, and OANDA env-var sanitiser.
5. `research/backtrader_lane/strategies/campaign_002_trend_following.py`
   — the actual adapter code.
6. `docs/research/BACKTRADER_SECOND_CAMPAIGN_BLOCKED.md` — the scoped
   next-sprint prompt for the future unblock branch.

## 19. Recommended next branch

`infra-backtrader-secondary-lane-002-real-data-run`.

Tasks (from `BACKTRADER_SECOND_CAMPAIGN_BLOCKED.md` §4):

1. Restore `data/oanda_h4_research.sqlite3` (no new fetch unless
   intentional and credentialed; the rehydration script is read-only
   OANDA practice).
2. Regenerate the seven CAMPAIGN_002 H4 CSVs via
   `scripts/export_lean_parity_data.py`.
3. Run `scripts/run_backtrader_parity.py --campaign CAMPAIGN_002` +
   `scripts/compare_backtrader_parity.py` and document the per-pair
   divergence in `docs/research/BACKTRADER_PARITY_CAMPAIGN_002_COMPARISON.md`.
4. Implement
   `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`
   per `RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md` R1–R8.
5. Run + compare CAMPAIGN_011; document in
   `docs/research/BACKTRADER_PARITY_CAMPAIGN_011_COMPARISON.md`.

Binding non-goals carry over: no approval, no tuning, no broker, no
LEAN, no verdict mutation.

## 20. Test inventory

```
Phase 1 smoke:             7 tests
Phase 2 data adapter:     15 tests
Phase 3 runner:           17 tests
Phase 4 CAMPAIGN_002:     20 tests
Phase 5 comparison:       16 tests
Phase 6 (no new tests; preflight + harness exercised end-to-end)
Phase 7 (doc-only — no new tests)
                          ────
backtrader_lane subtotal: 75 tests
existing repo tests:    1104 tests
                          ────
total tests:            1179 (all PASS)
```

## 21. Validation commands run

```bash
python -m pytest -q                                      # 1179 PASS
python -m pytest tests/unit/backtrader_lane -q           # 75 PASS
ruff check src tests scripts research/backtrader_lane    # All checks passed
python scripts/check_research_freeze.py                  # ALL CHECKS PASSED
python scripts/validate_research_archive.py              # ALL CHECKS PASSED
python scripts/scan_artifacts_for_secrets.py             # PASSED
```

## 22. Explicit non-approval statement (required)

**No strategy is approved.** The Backtrader secondary lane is
verification infrastructure. It cannot, does not, and must not
approve any strategy. Backtests of any kind on this lane are research,
not evidence. `strategy_evidence: false`. CAMPAIGN_002, CAMPAIGN_010,
CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/
research-only. CAMPAIGN_014 remains scaffold-only. Paper / demo / live
remain blocked.

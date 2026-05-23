# Infrastructure Free / Local Parity Verifier Sprint 001 — Summary

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-001`
**Base commit:** `72b8d3c` (HEAD of `infra-retire-quantconnect-lean-001`)

The first working implementation of the free / local independent
parity verifier designed in
[`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md).
**No strategy is approved, CAMPAIGN_002 remains REJECT, paper / demo /
live remain blocked, no broker credentials were used, no orders were
submitted, no LEAN run exists, no QuantConnect credentials were
requested or written.**

## 1. Branch name

`infra-free-local-parity-verifier-001`.

## 2. Commit hashes by phase

| phase | commit |
|---|---|
| Phase 0 — baseline & sprint plan | `2a50f45` |
| Phase 1 — verifier architecture & interfaces | `a567ba0` |
| Phase 2 — indicator fixture verifier | `2c69afd` |
| Phase 3 — rule fixture verifier | `f73bbed` |
| Phase 4 — minimal event-loop verifier + script | `4a130aa` |
| Phase 5 — comparison harness | `92505bd` |
| Phase 6 — verifier-side debugging pass | (skipped — conditional on full-data divergence; not run because full-data run was BLOCKED) |
| Phase 7 — evidence docs & status | `9aa35ba` |
| Phase 8 — final validation & summary | (this commit) |

## 3. Files changed by phase

| phase | files |
|---|---|
| Phase 0 | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md` (new); `docs/research/EVIDENCE_INDEX.md` |
| Phase 1 | `research/__init__.py` (new); `research/parity_verifier/__init__.py` (new); `research/parity_verifier/{models,instruments,data_loader,indicators,rules,event_loop,compare,reporting,README}.py` / `.md` (new, 8 files); `tests/research/__init__.py` (new); `tests/research/test_parity_verifier_models.py` (new); `pyproject.toml` (added `pythonpath = ["."]` for pytest) |
| Phase 2 | `tests/research/test_parity_verifier_indicators.py` (new); `docs/research/FREE_LOCAL_PARITY_VERIFIER_INDICATOR_FIXTURES.md` (new) |
| Phase 3 | `tests/research/test_parity_verifier_rules.py` (new); `docs/research/FREE_LOCAL_PARITY_VERIFIER_RULE_FIXTURES.md` (new) |
| Phase 4 | `scripts/run_free_local_parity_verifier.py` (new); `tests/research/test_parity_verifier_event_loop.py` (new); `docs/research/FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md` (new); `.gitignore` (added `research/parity_verifier/results/**/trades.csv`) |
| Phase 5 | `tests/research/test_parity_verifier_compare.py` (new); `docs/research/FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md` (new) |
| Phase 7 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_STATUS.md` (new); `docs/research/EVIDENCE_INDEX.md`; `docs/research/EVIDENCE_MANIFEST.json` (new diagnostic-artifact entry) |
| Phase 8 | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md` (new); `docs/research/EVIDENCE_INDEX.md` |

`src/forex_bot/` was **not** modified at any phase. No code under
`src/`, no campaign config, no campaign report, no
`configs/approved_strategies.yaml` was touched.

## 4. Tests and validation commands run

Per-phase and at this final phase:

- `python -m pytest -q` → **473 passed** (388 pre-sprint + 85
  verifier-side fixture tests).
- `ruff check src tests scripts research/parity_verifier` → **clean**.
- `python scripts/validate_research_archive.py` → **ALL CHECKS PASSED**
  (5 diagnostic artifacts present; 74 evidence-index links resolve;
  no credential-shaped strings in 1916 committed artifact files).
- `python scripts/check_research_freeze.py` → **ALL CHECKS PASSED**
  (paper-loop + demo-loop both refuse `['trend_following']` — frozen).
- `python scripts/scan_artifacts_for_secrets.py` → **PASSED**.
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` →
  **refused** with the empty-registry message.
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` →
  **refused** with the empty-registry message.
- `python -m forex_bot.cli --help` → no `live-loop` command exists.

## 5. QuantConnect / LEAN status

**Retired throughout.** No QC account was created, accessed, or
requested. No `lean login` / `lean init` / `lean backtest` was
attempted. The retirement decision record from the prior sprint
remains the source of truth; this sprint adds no recommendation to
reopen it.

## 6. QC credentials

**None requested, read, or created.** This sprint did not contact
QuantConnect, did not source `~/.lean/credentials`, and did not
prompt for any QC value. The local `/tmp/lean-venv` LEAN CLI install
is untouched and is not expected to be used again under this project.

## 7. Broker credentials

**None used.** The verifier package contains no `httpx` / `requests`
calls, no OANDA client imports, no `os.environ` reads beyond the
script's argument-parser defaults. The `forex_bot.config` module,
which is the only path that loads OANDA practice credentials, is not
imported by any verifier code path — guarded by a grep-enforced
import rail in `tests/research/test_parity_verifier_models.py`.

## 8. Orders

**None submitted.** This sprint never reaches any broker abstraction,
order placement, or `paper-loop` / `demo-loop` execution path.

## 9. Strategy approval

**None.** `configs/approved_strategies.yaml` remains `approved: []`.
The verifier's `VerifierResult` and `ComparisonReport` models hard-pin
`strategy_evidence: false` — constructing an instance with the rail
flipped raises `ValidationError`.

## 10. CAMPAIGN_002

**Remains REJECT.** The verifier targets the no-RiskEngine bespoke
reference (1,647 trades) for cross-check purposes only; no campaign
re-run was triggered, no campaign verdict was edited,
`EVIDENCE_MANIFEST.json` campaign verdicts are unchanged.

## 11. Paper / demo / live

**All remain blocked.** Direct CLI invocations at this phase
re-confirmed it; the freeze checker re-confirmed it on every commit.

## 12. Indicator fixture status

**16 cases pass** —
[`tests/research/test_parity_verifier_indicators.py`](../../tests/research/test_parity_verifier_indicators.py).
Pinned conventions: EMA alpha = 2/(L+1) with `adjust=False` seeding;
Wilder ATR alpha = 1/L with TR-mean seed; Donchian prior-bar
convention. No divergence from the canonical mathematical definitions.

## 13. Rule fixture status

**31 cases pass** —
[`tests/research/test_parity_verifier_rules.py`](../../tests/research/test_parity_verifier_rules.py).
Covers entry / no-entry branches (incl. trend-filter block + ATR
floor); long/short symmetric initial stop; trailing-stop ratchet
direction; exit ladder precedence (stop > time > EOD); bid/ask-aware
fills; 0.25%-risk sizing for USD-quote (250 units expected) and
USD-base (375 units expected for USD_JPY) pairs; PnL conversion.

## 14. Event-loop verifier status

**8 integration tests pass** —
[`tests/research/test_parity_verifier_event_loop.py`](../../tests/research/test_parity_verifier_event_loop.py).
Includes the no-lookahead rail (a giant spike on the last bar does
not back-propagate to prior-bar entries), the authoritative
CAMPAIGN_002 50/200/20/14/2.0/2.0/240 config-shape load, and the
USD_JPY divide-by-mid sizing path.

## 15. Full-data verifier status

**BLOCKED locally.** The seven-pair H4 export CSVs at
`research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv` are
gitignored regenerable bulk data and are not present on this branch.
The script exits 2 when every requested pair is blocked, writes a
zero-trade `parity_summary.json`, and lists the blocked pairs in the
markdown summary. No silent zero-trade "success".

## 16. Comparison status

- **Fixture-level:** 11 cases pass —
  [`tests/research/test_parity_verifier_compare.py`](../../tests/research/test_parity_verifier_compare.py).
- **Full-data:** BLOCKED — no verifier result was produced for the
  seven pairs. The comparison report shows BLOCKED rows for every
  pair, sourced from `compare.blocked_report` against the real
  bespoke reference JSON.

## 17. Divergence classification

- **Fixture level:** NONE — no divergence observed in 85 cases.
- **Full data level:** N/A — no full-data run, nothing to classify.
- Taxonomy in place
  ([`research/parity_verifier/models.py`](../../research/parity_verifier/models.py)
  `DivergenceClassification`) for the first full-data run.

## 18. Verifier bugs found / fixed

- **Fixture-assertion bug** in
  `test_uptrend_then_drop_produces_long_entry_and_stop_exit`. The
  original assertion `exit_price < entry_price` assumed every stop
  exit is a loss; the actual fixture bar walk produced a winning
  trailing-stop exit (entry 1.0052, exit at the ratcheted stop
  1.0133). Assertion corrected to
  `exit_price == pytest.approx(final_stop_price)`, which holds for
  both winning and losing stops.
- **Verifier production code:** no bug found. The fixture-assertion
  fix did not change any logic in `research/parity_verifier/`.

## 19. Bespoke-engine bugs found

**None.** The verifier was never exercised against real candles
during this sprint, so the bespoke engine was not yet end-to-end
cross-checked. A bespoke-engine bug, if it exists, will only surface
on a future full-data run once the CSVs are regenerated locally.

## 20. Local files created but not committed

- `/tmp/verifier_test/parity_summary.json` — the Phase 4 smoke run's
  output. Lives outside the repo. Not staged.
- `/tmp/verifier_test/trades.csv` — empty trades CSV from the same
  smoke run. Not staged.
- `/tmp/verifier_test/parity_summary.md` — markdown summary from the
  same smoke run. Not staged.

No `.env`, no SQLite store, no candle CSV, no committed bulk output
was added by this sprint.

## 21. Large outputs intentionally gitignored

- `research/parity_verifier/results/**/trades.csv` — added to
  `.gitignore` this sprint; regenerable from
  `scripts/run_free_local_parity_verifier.py`.
- `data/oanda_h4_research.sqlite3` — already gitignored before this
  sprint; verifier does not require it directly.
- `research/lean_parity/exports/campaign_002_h4/**/*.csv` — already
  gitignored before this sprint; verifier reads these but the absence
  is reported as BLOCKED rather than crashing.

## 22. Remaining blockers

1. **Local H4 candle CSVs absent** → full seven-pair full-window
   verifier run cannot execute on this branch. Unblock by
   regenerating the OANDA H4 store and running
   `scripts/export_lean_parity_data.py` (out of scope for this
   sprint — the regenerate step touches OANDA practice and was not
   permitted by the sprint rules).
2. **Verifier debugging pass (Phase 6) not yet exercised.** It is
   conditional on a material divergence from a full-data run; until
   step 1 is resolved, Phase 6 cannot begin.
3. **Financing is estimated / stress-only.** Unchanged standing live
   blocker; out of scope for the verifier.

## 23. Recommended next branch

`infra-free-local-parity-verifier-002-full-data-run` — once the user
chooses to regenerate the seven-pair H4 CSVs (an OANDA-touching step
that this sprint avoided), the next sprint executes the full-data
verifier run, runs the comparison against the no-RiskEngine bespoke
reference, classifies any divergence under the taxonomy, and runs
Phase 6 verifier-side debugging if needed. That sprint touches no
broker code, modifies no strategy, and approves no strategy — same
guardrails as this one.

## 24. Exact files to review first

1. [`FREE_LOCAL_PARITY_VERIFIER_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_STATUS.md)
   — the headline verifier status.
2. [`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md)
   — this sprint's plan, including the artifact-discovery table that
   recorded the BLOCKED state up front.
3. [`FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md)
   — exactly what is implemented, what is unsupported, what the
   BLOCKED full-data run looks like, and the unblock recipe.
4. [`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md)
   — comparison harness status, tolerance ladder, divergence
   taxonomy, fixture-level results.
5. [`research/parity_verifier/README.md`](../../research/parity_verifier/README.md)
   — module-level overview of the verifier package.
6. This summary (`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md`).

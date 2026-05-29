# CAMPAIGN_027_TRAIN_VALIDATION_001_SUMMARY

**Status:** TRAIN/VALIDATION EXECUTION — close-out / **REJECT_TRAIN_GATE** /
TEST_LOCKBOX_CLOSED / NOT_APPROVED (2026-05-28). Branch
`research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`.

The 28-item close-out of the CAMPAIGN_027 train/validation sprint. The single idea
that survived the edge-discovery front gate was run through train evidence on its
own ledgers under the binding conservative cost and **rejected at the train gate**;
validation was not run; the test lockbox stays sealed; nothing is approved.

---

### 1. Branch
`research-campaign-027-h4-filtered-zscore-reversion-train-validation-001` (off
`origin/main` @ `7b50b0e`, after the scaffold sprint merge).

### 2. Commit hashes by phase
- Phase 0 — truth audit + plan: `653c544`
- Phase 1 — data coverage + split decision: `dfb297b`
- Phase 2 — execution engine + runner + tests: `33ef674`
- Phase 3 — artifact-contract compliance pre-run: `090f0ae`
- Phase 4 — execute train + REJECT_TRAIN_GATE: `5683eca`
- Phase 5 — validation NOT run: `4d2c602`
- Phase 6 — matched-null + filter-ablation confirmation: `55cad8f`
- Phase 7 — recency + robustness interpretation: `6e8d310`
- Phase 8 — Backtrader parity readiness (DEFER): `01408d5`
- Phase 9 — final interpretation: `7117c96`
- Phase 10 — status/index/manifest/backlog: `1b6d2ec`
- Phase 11 — final validation + summary: *(this commit)*

### 3. Files changed by phase
- **P0:** `docs/research/CAMPAIGN_027_TRAIN_VALIDATION_001_PLAN.md`
- **P1:** `docs/research/CAMPAIGN_027_DATA_COVERAGE_AND_SPLIT_DECISION.md`
- **P2:** `research/campaign_027/__init__.py`, `research/campaign_027/engine.py`,
  `scripts/run_campaign_027_h4_filtered_zscore_reversion.py`,
  `tests/unit/test_campaign_027_train_validation.py`
- **P3:** `docs/research/CAMPAIGN_027_ARTIFACT_CONTRACT_COMPLIANCE_PRE_RUN.md`,
  `.gitignore` (schema-check dir)
- **P4:** `docs/research/CAMPAIGN_027_TRAIN_RESULT.md`,
  `research/campaign_027/train_validation/*` (22 artifacts)
- **P5:** `docs/research/CAMPAIGN_027_VALIDATION_NOT_RUN.md`
- **P6:** `docs/research/CAMPAIGN_027_EDGE_DISCOVERY_CONFIRMATION.md`
- **P7:** `docs/research/CAMPAIGN_027_RECENCY_AND_ROBUSTNESS_INTERPRETATION.md`
- **P8:** `docs/research/CAMPAIGN_027_BACKTRADER_PARITY_READINESS.md`
- **P9:** `docs/research/CAMPAIGN_027_FINAL_INTERPRETATION.md`
- **P10:** `docs/research/{STRATEGY_STATUS,EVIDENCE_INDEX,FUTURE_RESEARCH_BACKLOG}.md`,
  `docs/research/EVIDENCE_MANIFEST.json`
- **P11:** this summary + preflight artifact refresh

### 4. Data coverage and split decision
Local read-only `data/campaign_002.sqlite3`, native H4, mid OHLC. 7/7 majors
uniformly covered (~9,949 bars each, 2020-01-01 → 2026-05-24). Store begins exactly
at train start → ≈264-bar leading warmup drawn from inside 2020 (documented
limitation). Frozen split: **train 2020-01-01..2022-12-31 / validation
2023-01-01..2024-12-31 / test 2025-01-01..2026-05-20 (sealed)**. Self-contained
trade-completion policy (entry + full 12-bar exit within the split window) keeps the
lockbox strictly sealed; `dropped_trailing_signals = 0` on train. No pair excluded.

### 5. Train window
`2020-01-01 → 2022-12-31`, 7 majors. **Executed.**

### 6. Validation window, if run
`2023-01-01 → 2024-12-31` — **NOT run** (train gates failed).

### 7. Whether artifact contract passed
**Yes.** `--artifact-schema-check` and the real run both emit **22/22** required
artifacts with all contract-critical ledger fields present;
`artifact_contract_compliance.json` → `all_required_present=true`, `blocked=null`.

### 8. Train metrics (conservative cost binding)
180 short trades · expectancy **+0.00011974** (optimistic +0.00023494) · profit
factor **1.0433** · hit 0.500 · pairs non-negative 4/7 · years non-negative 1/3 ·
avg bars held 10.38 · avg spread 1.665 pips · exits time_stop 137 /
protective_atr_stop 43 · **2× cost stress −0.00007745 (PF 0.973)**. Funnel: 5,617
base triggers → 180 short entries.

### 9. Train gate result
**FAIL (4/8 binding gates).** PASS: expectancy>0, trades≥100, pairs≥4/7,
matched-null-above-random. **FAIL:** profit factor ≥1.05 (1.043); years
non-negative ≥2/3 (1/3); 2× cost stress ≥0 (−0.00007745); filter-ablation retained
add edge (`f_strong_extension` only reduces sample). → **REJECT_TRAIN_GATE.**

### 10. Whether validation ran
**No.** Per protocol, validation runs only if train gates pass (confirmation, not a
rescue).

### 11. Validation metrics, if run
N/A (not run). Validation artifacts emitted as empty placeholders
(`validation_run=false`).

### 12. Validation gate result, if run
N/A (not run).

### 13. Matched-null confirmation
Train, post conservative cost, seeds 0–49, window 12: strategy **above** the
structure-matched null on all three informative modes (timestamp_random_same_pair,
session_matched_random, full_matched_null) at percentile **90**
(`ABOVE_MATCHED_NULL`); `side_shuffled` degenerate (short-only ledger). The
**information** is real, but the null means are negative → "loses less than
random," **not** "makes money." This gate passed and is not why the campaign was
rejected.

### 14. Filter-ablation confirmation
Train, value = fixed-horizon h12 log return. `f_low_vol` **+0.000572
(FILTER_ADDS_EDGE)** and `f_quiet_session` **+0.000339 (FILTER_ADDS_EDGE)** confirm;
`f_strong_extension` **+0.000034 (FILTER_ONLY_REDUCES_SAMPLE)** — fails
confirmation (forking-path). Dropped filters behave as expected (`f_long_side`
hurts → short-only; `f_cost_adv_pair` only reduces sample).

### 15. Pair robustness
4/7 positive but AUD_USD-dominated (+0.00223, ≈4× the next pair); USD_JPY **negative**
(−0.00052) — confirms the precommit's "USD_JPY not a standalone thesis" caution.
GBP_USD (−0.00197) and USD_CHF (−0.00082) also negative.

### 16. Year / recency robustness
Train years: 2020 −0.00057, 2021 −0.00029, 2022 +0.00119 — only **1/3** positive
(single-year 2022 artifact). The 2024 recency gate was never reached (validation not
run); 2025–2026 remain sealed. Recency risk unresolved and unfavourable.

### 17. Cost stress result
2× conservative cost turns train expectancy **negative** (−0.00007745, PF 0.973) —
the wafer-thin edge does not survive a doubled cost assumption (kill condition #7).

### 18. Backtrader parity readiness
**DEFER_PARITY_REJECTED.** No passing result to reproduce; no Backtrader code
written; design risks recorded for completeness.

### 19. Final verdict
**REJECT_TRAIN_GATE / TEST_LOCKBOX_CLOSED / NOT_APPROVED.** The front-gate
information signal is real but did not become a tradable, cost-surviving, robust
strategy on a clean split. The `h4_filtered_zscore_reversion` family is **CLOSED**;
revival requires a new external thesis/data, not a re-tune.

### 20. Whether the test lockbox was opened
**No.** (Expected: no.) The runner refuses `--train/--validation/--test/--backtest/
--execute` and any window overlapping 2025-01-01 → 2026-05-20.

### 21. Whether any strategy is approved
**No.** (Expected: no.) `not_approved: true`, `promotion_eligible: false`.

### 22. Whether `approved_strategies.yaml` remains `approved: []`
**Yes.** (Expected: yes.) Unchanged.

### 23. Whether paper/demo/live remain blocked
**Yes.** (Expected: yes.) Loops refuse (`approved: []`); config keeps
`trading_enabled/allow_order_submission/allow_live_trading: false`.

### 24. Archive / freeze / secrets status
`check_research_freeze.py` ALL CHECKS PASSED; `validate_research_archive.py` ALL
CHECKS PASSED; `scan_artifacts_for_secrets.py` PASSED (pattern scan clean; value
scan skipped — no live creds in env).

### 25. Ruff / pytest results
`ruff check src tests scripts research` → All checks passed.
`pytest tests/ -q` → **2202 passed, 3 skipped** (skips pre-existing,
local-data-absent).

### 26. Known blockers or warnings
None blocking. Notes: (a) worktree runs require `PYTHONPATH=$PWD/src:$PWD`; the H4
store resolves worktree-aware to the primary checkout's `data/campaign_002.sqlite3`;
(b) the matched-null information benchmark is close-to-close, intentionally distinct
from the realized `next_bar_open` post-cost PnL (both reported); (c) `side_shuffled`
is degenerate for a short-only ledger; (d) the bounded `--artifact-schema-check`
output dir is gitignored; (e) preflight artifacts carry a wall-clock `checked_at_utc`
and differ on re-run (expected).

### 27. Recommended next sprint and why
**No CAMPAIGN_028 from this thread.** The `h4_filtered_zscore_reversion` family —
the last surviving edge-discovery front-gate idea — is closed; all of C022-family,
C025/C026, and now C027 are rejected/closed, and the strategy-search lanes are
null/exhausted. The disciplined next step is to **source a new external thesis or
new data** (per the standing restart criteria) rather than re-tune a dead family.
Secondary option: extend the edge-discovery lab with a Postgres M1/M15 data path to
screen sub-H1 ideas (currently SQLite-only). The lab remains the mandated front gate.

### 28. Exact files to review first
1. [`CAMPAIGN_027_FINAL_INTERPRETATION.md`](CAMPAIGN_027_FINAL_INTERPRETATION.md) — the verdict (most important).
2. [`CAMPAIGN_027_TRAIN_RESULT.md`](CAMPAIGN_027_TRAIN_RESULT.md) — train metrics + gate table.
3. [`research/campaign_027/train_validation/gate_result.json`](../../research/campaign_027/train_validation/gate_result.json) — machine-readable gates.
4. [`CAMPAIGN_027_EDGE_DISCOVERY_CONFIRMATION.md`](CAMPAIGN_027_EDGE_DISCOVERY_CONFIRMATION.md) — matched-null + filter-ablation.
5. [`research/campaign_027/engine.py`](../../research/campaign_027/engine.py) — the frozen-rule execution engine.
6. [`CAMPAIGN_027_TRAIN_VALIDATION_001_PLAN.md`](CAMPAIGN_027_TRAIN_VALIDATION_001_PLAN.md) — the pre-registered gates.
</content>

# CAMPAIGN_027_H4_FILTERED_ZSCORE_REVERSION_SCAFFOLD_001_SUMMARY

**Status:** SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED. Close-out of
`research-campaign-027-h4-filtered-zscore-reversion-scaffold-001` (2026-05-28).

Scaffold/precommit sprint for the **single idea that survived the edge-discovery
front gate**. No train/validation/test evidence; test lockbox closed; nothing
approved; `configs/approved_strategies.yaml` stays `approved: []`; paper/demo/live
blocked.

---

### 1. Branch
`research-campaign-027-h4-filtered-zscore-reversion-scaffold-001` (off
`origin/main` @ `556759a`, after the front-gate sprint merge).

### 2. Commit hashes by phase
- Phase 0 — truth audit + plan: `7dea1cd`
- Phase 1 — evidence-to-precommit reconciliation: `ae65391`
- Phase 2 — precommit strategy scope (FROZEN): `4bdb1af`
- Phase 3 — artifact contract + compatibility: `3f54f3a`
- Phase 4 — scaffold strategy/config skeleton: `678f5ab`
- Phase 5 — preflight-only runner: `2fb53b1`
- Phase 6 — Backtrader parity design: `4fccd57`
- Phase 7 — future train/validation prompt: `dcafef2`
- Phase 8 — status/index/manifest/backlog: `c294563`
- Phase 9 — final validation + summary: *(this commit)*

### 3. Files changed by phase
- **P0:** `docs/research/CAMPAIGN_027_H4_FILTERED_ZSCORE_REVERSION_SCAFFOLD_001_PLAN.md`
- **P1:** `docs/research/CAMPAIGN_027_EDGE_DISCOVERY_TO_PRECOMMIT_RECONCILIATION.md`
- **P2:** `docs/research/CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md`
- **P3:** `docs/research/CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT.md`,
  `research/campaign_027/artifact_contract.json`,
  `tests/unit/test_campaign_027_artifact_contract.py`
- **P4:** `configs/campaign_027_h4_filtered_zscore_reversion.yaml`,
  `src/forex_bot/strategies/h4_filtered_zscore_reversion.py`,
  `src/forex_bot/config.py`, `tests/unit/test_h4_filtered_zscore_reversion.py`
- **P5:** `scripts/run_campaign_027_h4_filtered_zscore_reversion.py`,
  `tests/unit/test_campaign_027_runner.py`,
  `research/campaign_027/preflight/*.json`
- **P6:** `docs/research/CAMPAIGN_027_BACKTRADER_PARITY_DESIGN.md`
- **P7:** `docs/research/NEXT_SPRINT_PROMPT_AFTER_CAMPAIGN_027_SCAFFOLD.md`
- **P8:** `docs/research/{STRATEGY_STATUS,EVIDENCE_INDEX,FUTURE_RESEARCH_BACKLOG}.md`,
  `docs/research/EVIDENCE_MANIFEST.json`
- **P9:** this summary + `EVIDENCE_INDEX.md` link + preflight artifact refresh

### 4. Campaign identity
CAMPAIGN_027 · `h4_filtered_zscore_reversion` · `0.1.0-c027` · timeframe **H4** ·
universe = 7 majors (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF,
NZD_USD). CAMPAIGN_027 was **verified free** (all prior references forward-looking
/ negative). Status: **SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED.**

### 5. Edge-discovery evidence that justified the scaffold
Only idea (of 12 screened) rated `CAMPAIGN_ELIGIBLE`: cost-feasible (H4
spread/ATR 0.04–0.10); forward-return info monotone with horizon; **beats all six
matched nulls** (pct 100, effect 3.7–6.0); **3/5 filters add edge** (low-vol
+0.000301, strong-extension +0.000208, quiet-session +0.000234); edge-adding
subset (n=1,065) post-cost **+0.000626 conservative / +0.000754 optimistic**, hit
0.55; pair-robust **6/7**; multi-year positive **4/7** conservative.

### 6. Known risks
Wafer-thin edge (≈0.005–0.007%/trade, hit ≈0.50) inside the cost band;
**2024 and 2026-partial negative** (recency); filter forking-path (3/5 retained
post-ablation); raw-matrix `LIKELY_SELECTION_NOISE` (USD_JPY single-pair);
signal information ≠ a proven tradable strategy.

### 7. Exact precommitted rules (frozen)
Signal: 20-bar z of mid close, **mean/σ shifted 1 bar, σ ddof=1**; base trigger
|z|≥2.0, **strong-extension entry |z|≥2.5**. Low-vol filter: ATR-14 **simple mean
of TR**, trailing-250 percentile **shifted 1**, **≤0.33**. Quiet-session filter:
UTC bucket ∈ {asia[0,7), london[7,12)}. Dropped filters: `f_cost_adv_pair`
(sample-only), `f_long_side` (hurts). Entry fill: **`next_bar_open`**.

### 8. Side rule
**Short-only.** Enter short when `z ≥ +2.5` (sell the rich extension). Long
signals (`z ≤ −2.5`) are **diagnostic-only, never entered** (`f_long_side` is the
sole `FILTER_HURTS_EDGE`; leave-one-out shows dropping the long side *raises*
expectancy).

### 9. Filter rules
Retained (precommitted set): **low-vol** (ATR-14 trailing-250 pct ≤0.33),
**strong-extension** (|z|≥2.5), **quiet-session** (asia/london). All three were
`FILTER_ADDS_EDGE` and structurally motivated.

### 10. Exit rules
**Primary:** time stop at **12 H4 bars** (the measured h12 horizon, ≈48h), filled
`next_bar_open`. **Protective:** wide **3×ATR-14** hard stop (tail-risk control;
adverse stop wins a same-bar tie). **No take-profit, no trailing.** (Mean-touch
target documented as a future variant only — it changes the measured proxy.)

### 11. Cost model
Optimistic = realized spread + 2×0.2-pip slip. **Conservative (BINDING)** = flat
1.5-pip spread + 2×0.2-pip slip + worst-case financing over the 12-bar hold.
2× cost stress = conservative with spread+slip doubled.

### 12. Artifact contract
`docs/research/CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT.md` +
`research/campaign_027/artifact_contract.json` enumerate the required future
ledgers (signal/trade/funnel/registry), metadata items 4–12, both cost metrics,
the C011 null reference, and lab-diagnostic targets — so a future sprint is
edge-discovery-re-screenable without the C025/C026 gap. The contract is enforced
by 9 contract tests (scaffold-safe, lockbox sealed, no future artifact produced).

### 13. Tests added (40 cases, all green)
- `tests/unit/test_h4_filtered_zscore_reversion.py` — pure-signal (threshold fires,
  low-vol/quiet-session gates, long disabled, no-lookahead, last-bar-only, no
  broker import, paper-only/unapproved).
- `tests/unit/test_campaign_027_artifact_contract.py` — contract JSON validity +
  scaffold-state/no-approval assertions.
- `tests/unit/test_campaign_027_runner.py` — refuses evidence modes, no trade
  ledger, diagnostic-only, no approval flag, lockbox guard.

### 14. Preflight results
`--preflight-only`: **preflight_ok = true**, 7/7 pairs PASS (~9,949 deduped H4
bars/pair, warmup 270). `--data-feature-preflight`: **preflight_ok = true**,
features computable for all 7 pairs over the **train** window (2020–2022; never
the lockbox). `--sample-signals-only` (EUR_USD, 2021-01-01, 300 bars): 300
decisions → **1 short entry**, **3 diagnostic-only long (not entered)**; filter
passes strong=20 / low-vol=125 / quiet=150 — confirms short-only entry + the
funnel. All artifacts under `research/campaign_027/preflight/`.

### 15. Whether train evidence ran
**No.** (Expected: no.)

### 16. Whether validation evidence ran
**No.** (Expected: no.)

### 17. Whether the test lockbox was opened
**No.** (Expected: no.) The runner refuses `--train/--validation/--test/
--backtest/--execute` and guards the 2025-01-01→2026-05-20 window.

### 18. Whether any strategy is approved
**No.** (Expected: no.) `not_approved: true`, `promotion_eligible: false`.

### 19. Whether `approved_strategies.yaml` remains `approved: []`
**Yes.** (Expected: yes.) Unchanged.

### 20. Whether paper/demo/live remain blocked
**Yes.** (Expected: yes.) Loops refuse (`approved: []`); config has
`trading_enabled/allow_order_submission/allow_live_trading: false`.

### 21. Archive / freeze / secrets status
`check_research_freeze.py` ALL CHECKS PASSED; `validate_research_archive.py` ALL
CHECKS PASSED; `scan_artifacts_for_secrets.py` PASSED (pattern scan clean; value
scan skipped — no live creds in env).

### 22. Ruff / pytest results
`ruff check src tests scripts research` → All checks passed.
`pytest tests/ -q` → **2188 passed, 3 skipped** (skips are pre-existing,
local-data-absent).

### 23. Known blockers or warnings
None blocking. Notes: (a) worktree runs require `PYTHONPATH=$PWD/src` and the H4
store resolves to the primary checkout's `data/campaign_002.sqlite3`
(worktree-aware); (b) preflight artifacts carry a wall-clock `checked_at_utc` and
will differ on re-run (expected); (c) the strategy computes z/ATR **inline** to
match the lab engine (shift-1, ddof=1, simple-mean ATR) rather than via
`indicators.*` — a deliberate fidelity choice the parity sprint must honour.

### 24. Recommended next sprint
The future train/validation sprint per
[`NEXT_SPRINT_PROMPT_AFTER_CAMPAIGN_027_SCAFFOLD.md`](NEXT_SPRINT_PROMPT_AFTER_CAMPAIGN_027_SCAFFOLD.md)
— **only on explicit instruction**: no tuning, one frozen candidate,
train/validation only, conservative cost binding, matched-null + filter-ablation
confirmation, pair/year robustness, the 2024/2026 recency gate, artifact-contract
compliance, the nine kill conditions; no lockbox until parity passes; no approval.

### 25. Exact files to review first
1. [`CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md`](CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md) — the frozen rule (most important).
2. [`CAMPAIGN_027_EDGE_DISCOVERY_TO_PRECOMMIT_RECONCILIATION.md`](CAMPAIGN_027_EDGE_DISCOVERY_TO_PRECOMMIT_RECONCILIATION.md) — why each rule.
3. [`../../src/forex_bot/strategies/h4_filtered_zscore_reversion.py`](../../src/forex_bot/strategies/h4_filtered_zscore_reversion.py) — the implementation.
4. [`CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT.md`](CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT.md) + [`../../research/campaign_027/artifact_contract.json`](../../research/campaign_027/artifact_contract.json).
5. [`NEXT_SPRINT_PROMPT_AFTER_CAMPAIGN_027_SCAFFOLD.md`](NEXT_SPRINT_PROMPT_AFTER_CAMPAIGN_027_SCAFFOLD.md) — the future execution prompt.

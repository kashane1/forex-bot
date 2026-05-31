# `research-cross-pair-currency-strength-rotation-walk-forward-001` — Sprint Plan (Phase 0)

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

Phase 0 repo truth audit + 10-phase evidence-sprint plan for
**CAMPAIGN_013 / `cross_pair_currency_strength_rotation 0.1.0-c013`**.
**Evidence sprint — runs walk-forward + financing overlay + risk
diagnostics + verifier assessment.** Even a clean PASS produces
`RESEARCH_PASS_UNAPPROVED`.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. **CAMPAIGN_011 is the null
> baseline only, not a trading candidate.** This sprint **cannot
> approve any strategy**; even a clean walk-forward PASS produces
> `RESEARCH_PASS_UNAPPROVED` pending the verifier extension + a
> deliberate human approval action per
> [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 1. Branch / base commit / repo state

| dimension | value |
|---|---|
| git branch (worktree) | `claude/affectionate-fermi-d950fc` |
| logical sprint branch | `research-cross-pair-currency-strength-rotation-walk-forward-001` |
| base commit (HEAD before Phase 0) | `248736c` — Phase 7 of `research-cross-pair-currency-strength-rotation-001` (scaffold-sprint close) |
| working tree at Phase 0 start | clean (only `.claude/` tooling cache untracked) |

## 2. Repo truth summary (verified)

| dimension | value |
|---|---|
| pytest count (baseline) | **875 passed** in 3.81 s |
| ruff status (baseline) | **3 pre-existing** in `research/lean_parity/algorithms/` (`2× RUF100` unused-noqa + `1× I001` unsorted-imports); untouched; out of scope |
| `validate_research_archive.py` | ALL CHECKS PASSED (12 campaigns; 14 diagnostic artifacts; 237 evidence-index links resolve; 2,465 committed artifact files clean) |
| `check_research_freeze.py` | ALL CHECKS PASSED (loops refuse; no credentials) |
| `scan_artifacts_for_secrets.py` | PASSED |
| `paper-loop -c configs/paper.yaml` | **refused** |
| `demo-loop -c configs/practice.yaml` | **refused** |
| `forex_bot.cli --help` | **no `live-loop` command** present |
| `configs/approved_strategies.yaml` | `approved: []` (verified verbatim) |

## 3. CAMPAIGN_013 scaffold status (verified)

| artifact | status |
|---|---|
| `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py` | **present** |
| `CrossPairCurrencyStrengthRotationStrategyConfig` in `src/forex_bot/config.py` | **present** |
| `StrategyConfig.cross_pair_currency_strength_rotation` slot + enabled-list check | **present** |
| `tests/unit/test_cross_pair_currency_strength_rotation.py` | **present** (57 tests, all passing) |
| `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` | **present**; loads cleanly via `load_settings()` |
| 10× `docs/research/CAMPAIGN_013_*` and `CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_*` docs | **all present** |
| `backtests/CAMPAIGN_013_*/` directory | **does NOT exist yet** — this evidence sprint creates it |

## 4. Local data status (verified)

| dimension | value |
|---|---|
| symlink | `data/campaign_002.sqlite3` → `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` |
| target file size | 112 MB (gitignored at `*.sqlite3`) |
| H4 coverage | **all 7 pairs present** (verified in CAMPAIGN_012 evidence sprint; data unchanged since) |
| span | **2020-01-01 → 2026-05-19** (matches CAMPAIGN_010 / 011 / 012) |
| data source label | `oanda-practice` (runner-enforced) |
| **regeneration needed?** | **NO** — local data covers the exact universe + span |
| committed bulky data | **none** (`*.sqlite3` gitignored) |

## 5. Frozen parameters (verified from `configs/campaign_013_cross_pair_currency_strength_rotation.yaml`)

| parameter | value |
|---|---|
| `version` | `0.1.0-c013` |
| `timeframe` | `H4` |
| `currency_strength_lookback_bars` | `24` |
| `rank_gap_threshold` | `4` |
| `atr_lookback` | `14` |
| `atr_stop_multiple` | `2.0` |
| `trailing_stop_atr_multiple` | `null` (validator rejects non-None) |
| `max_bars_in_trade` | `6` |
| `min_atr_pips` | `{}` |
| `warmup_bars_required()` | `50` (strategy class) |

**Universe (frozen):** 7 pairs — EUR_USD, GBP_USD, USD_JPY, AUD_USD,
USD_CAD, USD_CHF, NZD_USD.

**Risk settings (frozen):** `risk.max_open_positions = 1`,
`risk.max_positions_per_instrument = 1`, `risk.risk_per_trade_pct = 0.25`.

## 6. Safety state (verified)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 | all REJECT (untouched) |
| CAMPAIGN_013 | scaffold only; this sprint produces the verdict |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers; intact) |

## 7. Cross-pair runner integration contract (binding for Phase 3 — MANDATORY)

The Phase 3 runner **MUST**:

1. Load all 7 pairs' completed H4 candles for the test window +
   warm-up margin (≥ 25 H4 bars + slack).
2. **Align all 7 pairs' completed H4 close series to a common
   timestamp index** (intersection of completed bars).
3. Build per-pair closes-only `pd.Series` indexed by the common
   index.
4. **Inject `cross_pair_closes` into each pair's `strategy_config`
   (via the `strategy_config` dict passed to `BacktestEngine`)**
   exactly as expected by
   `CrossPairCurrencyStrengthRotationStrategy` R3 contract.
5. Ensure the strategy sees completed-only close series for all 7
   required pairs.
6. **Fail closed (CLASSIFY VERDICT AS BLOCKED) if** any required
   pair is missing, misaligned, non-finite, or insufficient.

The strategy's R3 already fails closed on missing dict or key-set
mismatch; the runner's responsibility is to make sure the dict is
correctly assembled and injected. **If the runner cannot satisfy
this contract, the verdict is BLOCKED — NOT a strategy-rule
modification.**

## 8. Evidence pipeline phases

| phase | output | binding rule |
|---|---|---|
| 0 | this plan doc | repo truth + safety state |
| 1 | `CAMPAIGN_013_DATA_PROVENANCE.md` | data hashes match CAMPAIGN_010 / 011 / 012 verbatim |
| 2 | `backtests/CAMPAIGN_013_*/walk_forward/plan.{json,md}` + `CAMPAIGN_013_WALK_FORWARD_PLAN.md` | 8 folds rolling/frozen |
| 3 | `scripts/run_campaign_013.py` | binding cross-pair runner integration contract (§7) |
| 4 | per-fold artifacts + `walk_forward/results.{json,md}` + `walk_forward/fold_detail.json` + `CAMPAIGN_013_WALK_FORWARD_EXECUTION.md` | 8 folds × 7 pairs = 56 backtests |
| 5 | `CAMPAIGN_013_WALK_FORWARD_RESULT.md` | verdict classification: REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED |
| 6 | `scripts/build_campaign_013_financing_overlay.py` + financing artifacts + `CAMPAIGN_013_FINANCING_OVERLAY.md` | ESTIMATED + conservative stress; MODELED refused |
| 7 | `scripts/build_campaign_013_risk_diagnostics.py` + risk artifacts + `CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md` | standard + CAMPAIGN_013-specific (rank-gap, simultaneous-signal, MAX_OPEN_POSITIONS_EXCEEDED rate) |
| 8 | `CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md` | verifier capability lock; not required for REJECT |
| 9 | `CAMPAIGN_013_EVIDENCE_SUMMARY.md` + `CAMPAIGN_013_STATUS.md` (UPDATE) + `CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md` + `EVIDENCE_INDEX.md` (UPDATE) + `EVIDENCE_MANIFEST.json` (UPDATE 12→13) + `STRATEGY_STATUS.md` (UPDATE) + test (12→13) | final validation; safety-state preservation |

## 9. Expected commands

### Phase 2 — plan generation
```bash
python scripts/run_walk_forward_dry_run.py \
  --campaign-name CAMPAIGN_013_cross_pair_currency_strength_rotation \
  --style rolling --parameter-mode frozen \
  --train-days 540 --validation-days 180 --test-days 180 --step-days 180 \
  --universe-start 2020-01-01 --universe-end 2026-05-20 \
  --output backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward
```

### Phase 4 — per-fold execution
```bash
python scripts/run_campaign_013.py \
  --config configs/campaign_013_cross_pair_currency_strength_rotation.yaml \
  --plan backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.json \
  --out backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation
```

### Phase 6 — financing overlay
```bash
python scripts/build_campaign_013_financing_overlay.py \
  --campaign-dir backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation
```

### Phase 7 — risk diagnostics
```bash
python scripts/build_campaign_013_risk_diagnostics.py \
  --campaign-dir backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation
```

## 10. Validation plan (per phase + at sprint close)

```bash
python -m pytest -q
ruff check src tests scripts research
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py
python -m forex_bot.cli paper-loop -c configs/paper.yaml      # expect refusal
python -m forex_bot.cli demo-loop -c configs/practice.yaml    # expect refusal
python -m forex_bot.cli --help                                 # expect no live-loop
git status --short
```

## 11. Non-goals (binding)

- **Do not approve any strategy.** Even a clean PASS produces `RESEARCH_PASS_UNAPPROVED`.
- **Do not modify `configs/approved_strategies.yaml`.**
- **Do not enable** `cross_pair_currency_strength_rotation` in `configs/paper.yaml` / `configs/practice.yaml`.
- **Do not run paper-loop or demo-loop** except for the standing refusal check.
- **Do not create or invoke a `live-loop` command.**
- **Do not submit / create / modify / cancel / close / query any broker order.**
- **Do not query account orders / trades / positions / account snapshots / transaction streams.**
- **Do not use QuantConnect / LEAN.**
- **Do not tune CAMPAIGN_013 parameters** based on intermediate results.
- **Do not weaken null-baseline comparison gates** after seeing results.
- **Do not relax `max_open_positions` or any risk limits** to "rescue" trade count if cross-pair concurrent signals produce high `MAX_OPEN_POSITIONS_EXCEEDED` rates. This is **known behavior** of C6, NOT a bug.
- **Do not change any historical campaign verdict** (CAMPAIGN_002 / 010 / 011 / 012 all stay REJECT).
- **Do not present a trading recommendation.**
- **Do not commit bulky data.**

## 12. Safety invariants (binding)

- `configs/approved_strategies.yaml` must read `approved: []` at every phase boundary.
- CAMPAIGN_002 / 010 / 011 / 012 verdicts unchanged at every phase boundary.
- MODELED financing remains refused at all 4 layers.
- Loops continue to refuse; no `live-loop` command appears.
- No broker call at any phase.
- No `.env` read; no credential printed.
- Frozen parameters unchanged across all 10 phases.

## 13. Explicit safety statements

1. **This sprint cannot approve any strategy.** Even RESEARCH_PASS_UNAPPROVED is not approval.
2. **A research pass remains unapproved.** Verdict options are REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED.
3. **CAMPAIGN_011 is only the null baseline, not a trading candidate.**
4. **The cross-pair runner integration contract is MANDATORY.** Failure to satisfy it means **BLOCKED** — not a strategy-rule modification.

## 14. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md) (scaffold-sprint summary)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md) (binding gate vector)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) (binding sprint spec)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md), [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md), [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md) (sibling references)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

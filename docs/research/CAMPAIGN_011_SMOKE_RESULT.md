# CAMPAIGN_011 — Non-Evidence Smoke Result

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-001`
`strategy_evidence: false`

Phase 5 **non-evidence** smoke result for CAMPAIGN_011 /
`random_entry_anchor 0.1.0-c011`. **These smokes are NOT
evidence.** They certify that the scaffold loads, instantiates,
and produces deterministic signals against in-memory fixtures —
nothing more. **No backtest was run. No verdict was produced.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.
> **CAMPAIGN_011 is a null model — cannot be approved by design.**

## 1. Commands run

### 1.1 Config-load smoke

```bash
.venv/bin/python -c "
from forex_bot.config import load_settings
from forex_bot.strategies import RandomEntryAnchorStrategy
s = load_settings('configs/campaign_011_random_entry_anchor.yaml')
assert s.strategy.enabled == ['random_entry_anchor']
assert s.strategy.random_entry_anchor is not None
strat = RandomEntryAnchorStrategy(version=s.strategy.random_entry_anchor.version)
assert strat.name == 'random_entry_anchor'
assert strat.version == '0.1.0-c011'
print('CONFIG-LOAD SMOKE: PASS')
"
```

**Result: PASS.**

| field | value (from loaded `Settings`) |
|---|---|
| `strategy.enabled` | `['random_entry_anchor']` |
| `strategy.random_entry_anchor.master_seed` | `20260523` |
| `strategy.random_entry_anchor.entry_probability_per_bar` | `0.05` |
| `strategy.random_entry_anchor.atr_lookback` | `14` |
| `strategy.random_entry_anchor.atr_stop_multiple` | `2.0` |
| `strategy.random_entry_anchor.trailing_stop_atr_multiple` | `None` |
| `strategy.random_entry_anchor.max_bars_in_trade` | `6` |
| `strategy.random_entry_anchor.min_atr_pips` | `{}` |
| `app.trading_enabled` | `False` |
| `app.allow_order_submission` | `False` |
| `app.allow_live_trading` | `False` |
| `risk.max_open_positions` | `1` |
| `risk.max_positions_per_instrument` | `1` |
| `risk.risk_per_trade_pct` | `0.25` |
| `RandomEntryAnchorStrategy.name` | `"random_entry_anchor"` |
| `RandomEntryAnchorStrategy.version` | `"0.1.0-c011"` |
| `RandomEntryAnchorStrategy.warmup_bars_required()` | `32` |

Every value matches
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§5 verbatim.

### 1.2 Unit-test smoke

```bash
.venv/bin/python -m pytest tests/unit/test_random_entry_anchor.py -q
```

**Result: 36 passed in 0.09s.**

All 36 cases pass: config defaults / validation (9), determinism
— seed dependence (5), determinism — content invariance (2),
distribution / frequency (2), strategy core R1/R2/R5/R7/R8 (7),
no-forbidden-imports structural audit (3), rejected-family
contamination audit (2), approval / safety regression (5),
strategy doesn't mutate config (1). The deterministic-signal
test cases (`test_signal_emitted_with_expected_fields` and
`test_signal_id_is_deterministic`) confirm signals fire with
the expected shape on fixture H4 frames, which doubles as the
"tiny fixture signal-generation smoke" — no separate ad-hoc
smoke script is needed.

### 1.3 Walk-forward dry-run plan (to `/tmp` only — not committed)

```bash
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_011 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output /tmp/campaign_011_smoke/
```

**Result: 8 folds emitted; `style=rolling`; `parameter_mode=frozen`;
`validate_plan()` passed implicitly inside the script (the script
exits non-zero on a `PlanValidationError`).**

The plan was written to `/tmp/campaign_011_smoke/{plan.json,plan.md}`
and is **not committed**. The future evidence sprint
(`research-random-entry-diagnostic-anchor-walk-forward-001`) will
re-run this command writing the authoritative plan to
`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/`
(committed). Fold count matches CAMPAIGN_010's authoritative plan
exactly (8 folds), confirming the inherited gate-vector
comparison will be apples-to-apples.

### 1.4 Full repo regression test

```bash
.venv/bin/python -m pytest -q
```

**Result: 771 passed in 2.88s** (735 prior + 36 new). No
regression introduced by the scaffold sprint.

## 2. What passed

- Config-load (the YAML loads through Pydantic with all frozen
  parameters at their expected values).
- Unit-test suite (36 cases — all rules, determinism, distribution,
  structural audits, approval regression).
- Walk-forward dry-run plan (8 folds; rolling; frozen; matches
  CAMPAIGN_010 fold structure).
- Full repo regression (771 pytests; no regression).
- Strategy module instantiation + correct version / warmup.

## 3. What was NOT run

- **No historical backtest.** No `BacktestEngine` invocation.
- **No walk-forward evidence campaign.** No
  `WalkForwardResults` produced; no per-fold metrics; no
  verdict.
- **No financing overlay.** No `research.financing.calculate_run`
  invocation against committed trades.
- **No risk diagnostics.** No `scripts/build_campaign_011_risk_diagnostics.py`
  invocation (the script does not yet exist; it is the future
  evidence sprint's task to add it as a clone of CAMPAIGN_010's
  equivalent).
- **No data fetch.** Existing symlinked
  `data/campaign_002.sqlite3` was not even read in this Phase 5
  (the dry-run plan generator does not consume candle data; it
  just emits fold dates).
- **No broker call.** No `OandaBroker` invocation; no
  account-state query; no order submission.
- **No `/tmp/campaign_011_smoke/` output committed.** Verified
  via `git status --short` (clean).

## 4. Is this evidence?

**No.** Per
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§7 and
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§7.1:

- A config-load smoke is not evidence.
- A unit-test pass is not evidence.
- A walk-forward dry-run plan (in `/tmp`) is not evidence.
- A fixture-deterministic signal-shape check is not evidence.

The evidence pipeline begins with `WalkForwardResults`
production in the future evidence sprint — which this scaffold
sprint **does not** invoke.

## 5. Was any broker call made?

**No.** All commands above run entirely off the local repo +
the existing pip-installed dependencies. No `OandaBroker`
import was triggered in the loaded strategy path; no network
call; no environment-variable read for credentials.

## 6. Were any credentials read?

**No.** `.env` was not opened. The config's
`broker.account_id_env` and `broker.token_env` fields are
present (matching the CAMPAIGN_010 config pattern for
configuration completeness), but they are **not consumed** by
the scaffold sprint — the runner doesn't exist yet, and
nothing in Phase 5 invokes the broker.

## 7. Was any data fetched?

**No.** No `scripts/rehydrate_oanda_h4_store.py` invocation,
no OANDA API call, no SQLite write. The dry-run plan generator
in step 1.3 produces fold date ranges from CLI args alone —
no candle data is read.

## 8. Explicit no-approval statement

This smoke result, the scaffold itself, the unit tests, and the
config YAML **do not approve the strategy**.

**CAMPAIGN_011 cannot be approved by design.** It is a null
model. The protocol's §4 whitelist places it under "Baseline /
null model" — "allowed only as a diagnostic comparison anchor
for the preferred candidate; cannot itself be the 'preferred
candidate' for paper promotion."

The candidate cannot be added to
[`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
under any circumstance — even if the future evidence sprint
records an unexpected PASS (which would itself trigger the
investigation playbook in
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§12, never promotion).

## 9. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **Paper / demo / live remain blocked.**
- No broker / OANDA call this sprint.
- No `.env` read; no credential printed; no account / order /
  trade / position / transaction endpoint queried.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.
- `MODELED` financing remains refused at four layers.
- pytest baseline: **771 passes** (735 prior + 36 new from
  Phase 3).
- `git status --short` is clean.
- `/tmp/campaign_011_smoke/` is local-only, gitignored
  (outside the repo entirely).

## 10. Cross-links

- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
  (the binding spec for the future evidence sprint)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`scripts/run_walk_forward_dry_run.py`](../../scripts/run_walk_forward_dry_run.py)

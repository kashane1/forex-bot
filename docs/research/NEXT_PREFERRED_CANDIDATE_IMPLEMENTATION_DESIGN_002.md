# Next Preferred Candidate — Implementation & Evaluation Design (Sprint 002)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-002`
`strategy_evidence: false`

Phase 4 detailed implementation + evaluation design for the
selected next preferred candidate, **C5 — `random_entry_anchor
0.1.0-c011` (CAMPAIGN_011)** — per the Phase 3 selection in
[`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md).
**This design is binding for the future scaffold + evidence
sprints; no strategy code is written here.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_011 is a diagnostic anchor / null
> model; it cannot be approved by design.**

## 1. Hypothesis (verbatim, frozen)

> **A deterministic-seed coin-flip entry on the 7-pair OANDA
> H4 universe, executed under the same RiskEngine gates and the
> same ATR-stop / time-stop exit logic as CAMPAIGN_010, has
> *no edge by construction*. Its per-fold and aggregate
> expectancy under rolling walk-forward will set the
> falsifiability bar that every subsequent C2 / C3 / C4 /
> new-family candidate must beat by a meaningful margin to be
> considered evidence of an edge. The headline gate vector is
> inherited verbatim from
> [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
> §10 so the comparison is on the entry signal alone, not on a
> shifted goalpost.**

The expected outcome is **REJECT** with a clean fold-pass-rate
of 0 / 8 and an aggregate expectancy R approximately equal to
CAMPAIGN_005's reported random baseline (≈ −0.095 R per trade,
deepened by the longer 6-bar time stop and the per-fold
financing overlay). Any deviation from this expected outcome
is itself a diagnostic finding worth investigating.

## 2. Universe + timeframe + data requirements

| dimension | value |
|---|---|
| universe (exact, frozen) | `["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"]` |
| timeframe | H4 |
| data source | local SQLite store at `data/campaign_002.sqlite3` (gitignored symlink — matches CAMPAIGN_010) |
| required source label | `oanda-practice` (runner-enforced) |
| data span | 2020-01-01 → 2026-05-19 inclusive (matches CAMPAIGN_010) |
| new data fetch needed? | **no** |
| new credentials needed? | **no** |
| new external dependency? | **no** |

## 3. Signal rules (R1–R8; binding)

### R1 — Warm-up

The strategy requires at least `atr_lookback + 2 = 16` H4 bars
of history (matches CAMPAIGN_010's R1 for a clean exit-mechanics
comparison). Signals before this point return `None`.

### R2 — Block re-entry while a position is open

If `ctx.open_positions` contains a flat-`False` position for
`ctx.instrument`, return `None`. Mirrors CAMPAIGN_010's R2 and
the engine's single-instrument single-position invariant.

### R3 — Deterministic coin flip per bar

At completed bar `t`:

1. Compute `seed_input = (master_seed, ctx.instrument.name, bar_timestamp_iso_8601)`.
2. Hash via SHA-256 to produce a 256-bit value; take the
   low-order 64 bits as `bar_random`.
3. `direction = "long"` if `bar_random & 1 == 0` else `"short"`.

The deterministic seed makes the strategy reproducible across
runs (same `(master_seed, pair, t)` → same direction).

### R4 — Entry frequency control

Naïve coin flip would emit a signal on every completed bar.
That overstates the trade frequency for a meaningful
falsifiability anchor. Apply an entry-frequency rule:

- `entry_probability_per_bar` (frozen) = `0.05` (matches
  CAMPAIGN_005's 85-trade-per-seed sample over ~9,930 bars: a
  reference frequency of ~0.86 % per bar, but C5 doubles this
  to ~5 % to give enough trades per fold to meet the
  `trade_count ≥ 30` gate).
- Decision: at each bar, derive `gate_value = sha256((master_seed, pair, t, "gate")) % 1000`.
  If `gate_value / 1000.0 < entry_probability_per_bar`, the
  R3 direction stands. Otherwise return `None`.

This keeps the signal deterministic *and* matches the per-fold
trade-count regime of CAMPAIGN_010 (~50–80 trades per pair per
fold) so the gate vector is comparable.

### R5 — Fail-closed on insufficient ATR

Compute `prior_atr = atr(df["high"], df["low"], df["close"], atr_lookback).iloc[-2]`.
If `prior_atr` is not finite or `<= 0`, return `None`.

### R6 — Spread filter (delegated to RiskEngine)

The candidate does **not** implement its own spread filter; the
RiskEngine's per-pair `spread_filter` gates apply identically
to CAMPAIGN_010. This is essential for a clean comparison.

### R7 — Stop placement

| side | stop |
|---|---|
| long | `close[t] - atr_stop_multiple * prior_atr` |
| short | `close[t] + atr_stop_multiple * prior_atr` |

If `stop == close[t]` (shouldn't happen given R5), return `None`.

### R8 — Emit `Signal`

Emit a `Signal` with:

- `signal_id` = `sha256("|".join(["random_entry_anchor", "0.1.0-c011", ctx.instrument.name, timeframe, bar_timestamp_iso, direction]))[:24]`
- `strategy_name = "random_entry_anchor"`
- `strategy_version = "0.1.0-c011"`
- `instrument = ctx.instrument.name`
- `timeframe = "H4"`
- `timestamp = bar_timestamp_utc`
- `side = direction`
- `entry_intent = "market"`
- `stop_model = f"ATR{atr_lookback}*{atr_stop_multiple}"`
- `stop_price = ctx.instrument.round_price(Decimal(str(stop)))`
- `exit_model = "time_stop_only"`
- `features = {"bar_random": int(bar_random), "gate_value": int(gate_value), "prior_atr": float(prior_atr), ...}`
- `reason = "Random entry (deterministic-seed; null model)"`

The position is then sized by `RiskEngine` using the same
`risk_per_trade_pct` as CAMPAIGN_010.

## 4. Frozen parameter set (verbatim — pre-commit-bound)

| parameter | value | rationale |
|---|---|---|
| `version` | `"0.1.0-c011"` | candidate id |
| `timeframe` | `"H4"` | matches CAMPAIGN_010 universe / harness |
| `master_seed` | `20260523` (or another single integer fixed before any run) | deterministic-seed root; chosen *before* any pilot run |
| `entry_probability_per_bar` | `0.05` | calibrated so per-fold trade count is in the CAMPAIGN_010 regime (~50–80 per pair per fold); not "tuned" but explicitly justified |
| `atr_lookback` | `14` | matches CAMPAIGN_010 / CAMPAIGN_002 / CAMPAIGN_004 — the project's standard for stop sizing; deliberately matched for clean comparison |
| `atr_stop_multiple` | `2.0` | matches CAMPAIGN_010 — the project's standard for stop multiple; deliberately matched |
| `max_bars_in_trade` | `6` | matches CAMPAIGN_010 (≈ 1 trading day) for clean exit-mechanics comparison |
| `trailing_stop_atr_multiple` | `null` | no trail in v1 — matches CAMPAIGN_010 |
| `min_atr_pips` | `{}` | no per-pair minimum (matches CAMPAIGN_010) |

**Any change to any of these parameters constitutes a NEW
candidate** that requires its own discovery + design cycle.

## 5. No-lookahead rules (binding)

- The strategy reads only `close[t]` from bar `t` itself; bar
  `t`'s `high`, `low`, `open`, and `volume` are deliberately
  not consulted.
- The ATR is computed once over the full series; the value at
  index `-2` (i.e. as of bar `t-1`) is used for stop sizing.
- The random seed input contains *only* `(master_seed,
  ctx.instrument.name, bar_timestamp_iso)`. **It must not
  include the close price, the ATR, or any other bar-`t`
  data.** This is the key no-lookahead invariant for a
  null-model strategy.
- A grep test in
  `tests/unit/test_random_entry_anchor.py` will assert the
  strategy module does not import from `forex_bot.broker` and
  does not reference any CAMPAIGN_002 / CAMPAIGN_010 frozen
  parameter key.

## 6. Missing-data behavior

- A bar with `NaN` `prior_atr` returns `None` (R5).
- A bar where the pair's row count is < warm-up returns
  `None` (R1).
- A bar where `ctx.open_positions` already has an active
  position for the instrument returns `None` (R2).
- A bar where `gate_value / 1000.0 >= entry_probability_per_bar`
  returns `None` (R4 — most bars).

The strategy never raises an exception on bad data; it
fail-closes by emitting no signal. Consistent with CAMPAIGN_010.

## 7. Config schema needs

Add to `src/forex_bot/config.py`:

```python
class RandomEntryAnchorStrategyConfig(BaseModel):
    """Frozen-parameter config for the random_entry_anchor
    diagnostic anchor (CAMPAIGN_011)."""
    model_config = ConfigDict(extra="forbid")
    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    master_seed: int
    entry_probability_per_bar: float = 0.05
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = None
    max_bars_in_trade: int = 6
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> RandomEntryAnchorStrategyConfig:
        # reject invalid: entry_probability not in (0, 1],
        # atr_lookback < 2, atr_stop_multiple <= 0,
        # max_bars_in_trade < 1.
        ...
```

Add to `StrategyConfig`:

```python
random_entry_anchor: RandomEntryAnchorStrategyConfig | None = None
```

Plus the matching enabled-list check in
`StrategyConfig._check_enabled`.

## 8. Strategy module location

`src/forex_bot/strategies/random_entry_anchor.py` — implements
the `Strategy` protocol identically in shape to
`src/forex_bot/strategies/session_breakout.py` but with the R1–R8
rules from §3 above. Estimated size: ~150 LOC (smaller than
session_breakout because there is no session-window or
prior-bar-range logic).

Add to `src/forex_bot/strategies/__init__.py`:

```python
from forex_bot.strategies.random_entry_anchor import (
    RandomEntryAnchorStrategy,
)
__all__ = [
    ...,
    "RandomEntryAnchorStrategy",
]
```

## 9. Tests required (`tests/unit/test_random_entry_anchor.py`)

Minimum 20 cases covering:

- **Determinism** (≥ 3 cases): same seed → same trades; different
  seed → different trades; bar-timestamp dependence of the seed.
- **No-lookahead structural audit** (≥ 4 cases): AST-level check
  that `generate_signal()` doesn't read `close[t]` past index
  `-1` for hashing; grep-style asserts on no `forex_bot.broker`
  import; grep on no CAMPAIGN_002 / CAMPAIGN_010 key references;
  signal-id stability test.
- **Distribution** (≥ 3 cases): with fixed seed over N bars
  (e.g. 10,000), long-short distribution is 50 / 50 within 3σ;
  entry rate matches `entry_probability_per_bar` within 2σ.
- **Config validation** (≥ 4 cases): valid config loads; invalid
  `entry_probability_per_bar` (0, negative, > 1) rejected;
  invalid `atr_lookback` rejected; missing `master_seed`
  rejected.
- **Strategy core** (≥ 4 cases): R1 warm-up; R2 block re-entry;
  R5 fail-closed on NaN ATR; R7 stop placement long/short.
- **Approval / safety regression** (≥ 2 cases): `approved_strategies.yaml`
  still empty; `random_entry_anchor` not in any active loop.

The structural tests mirror the
`tests/unit/test_session_breakout.py` pattern (33 cases there;
~20 here because the strategy is simpler).

## 10. Walk-forward requirements

Inherited verbatim from CAMPAIGN_010's pre-commit so the
comparison is on the entry signal alone:

| field | value |
|---|---|
| `--style` | `rolling` |
| `--parameter-mode` | `frozen` |
| `--train-days` | `540` |
| `--validation-days` | `180` |
| `--test-days` | `180` |
| `--step-days` | `180` |
| `--universe-start` | `2020-01-01` |
| `--universe-end` | `2026-05-20` |
| expected fold count | **8** (same as CAMPAIGN_010) |
| min fold count gate | **≥ 6** (same) |

### 10.1 Per-fold gates (inherited from CAMPAIGN_010 §10)

| level | gate | threshold |
|---|---|---|
| test fold | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| test fold | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| test fold | `pairs_positive_net_of_stress_financing` | ≥ 4 of 7 |
| test fold | `trade_count` | ≥ 30 |
| test fold | `single_pair_dominance` | ≤ 60 % |

### 10.2 Aggregate gates (inherited from CAMPAIGN_010 §10)

| level | gate | threshold |
|---|---|---|
| aggregate | `fold_pass_rate` | 100 % (strict) |
| aggregate | `fold_count` | ≥ 6 |
| aggregate | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| aggregate | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| aggregate | `pairs_positive` | ≥ 4 of 7 |
| aggregate | `trade_count` | ≥ 200 |
| aggregate | `single_fold_dominance` | ≤ 60 % |
| aggregate | `single_pair_dominance` | ≤ 40 % |
| financing | `conservative_stress_run_does_not_flip_verdict` | PASS |
| financing | `modeled_refused` | PASS |
| financing | `missing_rate_event_count` | 0 |

The expected outcome under random entry is **REJECT on every
PnL-direction gate**; the dominance + cost gates should
**PASS** because they are structural, not directional.

### 10.3 Dominance checks (structurally expected to pass for random)

Random entry should distribute trades uniformly across pairs
and folds; single-pair / single-fold dominance should be near
the uniform-distribution value (1/7 ≈ 14 % per pair; 1/8 ≈ 13 %
per fold). Any large deviation is itself a diagnostic finding.

## 11. Financing requirements

- **Expected holding period.** ≤ 6 H4 bars (matches CAMPAIGN_010).
  Most trades incur 0–1 daily rollover events. Wednesday triple
  applies to ~⅛ of multi-day trades.
- **Expected financing sensitivity.** Modest. The conservative
  stress source debits both sides at the same bp/day; net
  cashflow ≈ −(trades × hold_days × bp/day / 10,000). For ~2,500
  random trades × ~0.7 rollovers/trade × ~5 bp/day debit ≈ −$45
  (similar order of magnitude to CAMPAIGN_010's −$55.69).
- **ESTIMATED + conservative stress** — the only authorized
  source today. **MODELED remains refused at four layers.**
- **Whether MODELED financing blocks promotion.** Irrelevant —
  C5 is a null model and cannot be promoted. Item 5 / item 6 of
  the six-evidence ladder are structurally not binding for C5.
- **Whether financing flips the verdict.** No (vacuously) —
  the pre-financing verdict is REJECT; stress only deepens it.

## 12. Portfolio-risk diagnostics

| diagnostic | expected value (random) |
|---|---|
| max concurrent open positions per instrument | 1 (engine-enforced) |
| per-pair trade count | ≈ uniform across 7 pairs (~290–410 per pair × 8 folds — but subject to R5 NaN-ATR rejections + R6 spread filter rejections) |
| aggregate notional | bounded by `risk_per_trade_pct = 0.25 %` of `$500` per pair |
| pair concentration (single-pair dominance %) | ≤ 25 % (uniform target ≈ 14 %) |
| session clustering | **uniform across hours (this differs from CAMPAIGN_010 which was 100 % London-window)** — useful contrast |
| loss streaks per pair | distributed per binomial(N, p ≈ 0.5 − cost-bias) |
| drawdown clustering | mild; no per-fold drawdown should exceed the engine's `max_total_drawdown_pct = 8 %` |
| RiskEngine rejection profile | spread filter and spread-to-ATR rejection rate similar to CAMPAIGN_010 (~30 %) since the spread thresholds are identical |

## 13. Independent-verifier requirements

- **Verifier extension is not required for CAMPAIGN_011 to
  REJECT.** C5 is a null model and cannot be paper-promoted;
  item 5 of the six-evidence ladder is structurally not binding.
- **Verifier extension is uniquely valuable for C5** (as a
  follow-up) because:
  - random has zero tunable parameters,
  - the comparison can be exact (deterministic seed → deterministic trades),
  - the extension is a useful template for adding any future
    family to the verifier.
- **Recommended follow-up** (not required by this design):
  `infra-free-local-parity-verifier-random-entry-001` —
  add `random_entry_anchor` coverage to the verifier; produce
  a deterministic exact-equivalence corroboration report.

## 14. Rejection criteria before any paper/demo consideration

**CAMPAIGN_011 cannot be paper-promoted by design.** The
following criteria nevertheless apply to the future evidence
sprint's verdict:

- **REJECT** if any gate from §10 fails (expected outcome).
- **INCONCLUSIVE** if trade count < 200 aggregate or < 30
  per fold (would indicate the entry-probability calibration
  is wrong — the future evidence sprint can re-calibrate
  `entry_probability_per_bar` in a *separate* sprint, never
  during the evidence run).
- **BLOCKED** if the data, the engine, or the financing
  calculator fails to produce clean output.
- **UNEXPECTED PASS** if the gates pass — treat as a bug
  report against the pipeline (information leakage somewhere);
  do not celebrate, do not promote.

The unexpected-PASS investigation playbook (for the future
evidence sprint):

1. Confirm `seed_input` does not include any bar-`t` data
   (re-grep the strategy module).
2. Confirm fold-boundary leakage rules pass (validate_plan).
3. Confirm the strategy module's structural audits pass
   (no `forex_bot.broker` import; no CAMPAIGN_002 / CAMPAIGN_010
   key references).
4. Confirm the entry-probability rate matches the expected
   ~5 % per bar within statistical bounds.
5. Confirm the long-short distribution matches 50 / 50 within
   statistical bounds.
6. If all of the above are clean, escalate to a *separate*
   investigation sprint (`infra-pipeline-validation-investigation-001`).

## 15. Required artifacts (committed by the future evidence sprint)

The future
`research-random-entry-diagnostic-anchor-walk-forward-001`
evidence sprint must commit:

- `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.md`
- `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.md`
- `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_<PAIR>_summary.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_<PAIR>_trades.csv`
- `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.{json,md}`
- `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_summary.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.{json,md}`
- `docs/research/CAMPAIGN_011_DATA_PROVENANCE.md`
- `docs/research/CAMPAIGN_011_WALK_FORWARD_PLAN.md`
- `docs/research/CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`
- `docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md`
- `docs/research/CAMPAIGN_011_FINANCING_OVERLAY.md`
- `docs/research/CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`
- `docs/research/CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`
- `docs/research/CAMPAIGN_011_EVIDENCE_SUMMARY.md`
- `docs/research/CAMPAIGN_011_STATUS.md` (updated to `rejected (null model — diagnostic anchor)`)
- `docs/research/ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md` *— this is a typo placeholder; the actual filename is* `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`

The pattern strictly mirrors CAMPAIGN_010's evidence sprint.

## 16. Future scaffold sprint cannot approve

The future
`research-random-entry-diagnostic-anchor-001` scaffold sprint
**cannot approve** the strategy. Per the protocol:

- Adding `random_entry_anchor` to `configs/approved_strategies.yaml`
  is forbidden.
- Running `paper-loop -c configs/campaign_011_random_entry_anchor.yaml`
  is forbidden.
- Running `demo-loop -c configs/campaign_011_random_entry_anchor.yaml`
  is forbidden.
- Creating any `live-loop` command is forbidden.

Even if a future evidence sprint records an unexpected PASS, the
strategy is **not** automatically approved — the six-evidence
ladder + human approval gate apply, and C5 is structurally a
null model that should not be on a paper / demo / live path.

## 17. Future evidence sprint cannot approve

Same as §16. Even a clean PASS produces *research evidence*
(in the form of `WalkForwardResults` + financing overlay +
risk diagnostics + verifier status), not approval. Approval is
the human-in-the-loop gate per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 18. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **Paper / demo / live remain blocked.**
- No strategy code edited this phase.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 19. Pre-flight checklist for the future scaffold sprint

The future `research-random-entry-diagnostic-anchor-001`
sprint's Phase 0 audit should verify:

- [ ] Repo state clean.
- [ ] `configs/approved_strategies.yaml` reads `approved: []`.
- [ ] CAMPAIGN_002 and CAMPAIGN_010 verdicts unchanged.
- [ ] 735 pytests pass (Phase 0 baseline).
- [ ] 11 pre-existing UP042 ruff findings in untouched files (unchanged).
- [ ] Archive validator + freeze checker + secret scanner PASS.
- [ ] Loops refuse; no `live-loop`.
- [ ] No `random_entry_anchor.py` exists yet.
- [ ] No `RandomEntryAnchorStrategyConfig` in `src/forex_bot/config.py` yet.
- [ ] No `CAMPAIGN_011_*` artifact directory under `backtests/` yet.
- [ ] The selected `master_seed = 20260523` (or another fixed value)
      is committed to the pre-commit doc *before* any backtest run.

## 20. Cross-links

- [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
  (Phase 3 selection)
- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)
  (Phase 2 scoring)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
  (anti-overfit guardrails)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  (the gate vector C5 inherits)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md)
  (Phase 5 future scaffold-branch spec)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
  (Phase 5 future evidence-branch spec)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)

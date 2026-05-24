# CAMPAIGN_013 — Pre-Commit Checklist (`cross_pair_currency_strength_rotation 0.1.0-c013`)

**Branch:** `research-cross-pair-currency-strength-rotation-001` (scaffold) /
`research-cross-pair-currency-strength-rotation-walk-forward-001` (future evidence)
**Date:** 2026-05-23 · `strategy_evidence: false`

Binding pre-commit for CAMPAIGN_013 / `cross_pair_currency_strength_rotation 0.1.0-c013`,
the C6 cross-pair currency-strength rotation real candidate. **This
pre-commit binds the future evidence sprint to a specific gate vector,
frozen parameters, data source, no-lookahead invariants, cross-pair
runner contract, and null-baseline comparison — all agreed BEFORE any
backtest fires.** Approval requires the full six-evidence ladder + a
deliberate human approval action per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 remain REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked. CAMPAIGN_011 is the **null baseline
> only**, not a trading candidate.

## 1. Hypothesis (frozen, verbatim)

> The G7 USD-denominated H4 universe contains 4 USD-base pairs
> (EUR_USD, GBP_USD, AUD_USD, NZD_USD) and 3 USD-quote pairs
> (USD_JPY, USD_CAD, USD_CHF). For each USD-base pair, the non-USD
> currency's relative-performance can be inferred from the H4
> close-to-close return. For each USD-quote pair, the non-USD
> currency's relative-performance is the inverse. Aggregating across
> all 7 pairs over a fixed rolling window yields a currency-strength
> rank for each of the 8 currencies. The C6 hypothesis is that the
> strongest-vs-weakest currency rank gap predicts the direction of
> that pair over the next ~6 H4 bars, provided the rank gap exceeds
> a threshold large enough to overcome H4 cost drag.

## 2. Implementation files (scaffold sprint deliverables)

| file | purpose |
|---|---|
| `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py` | `CrossPairCurrencyStrengthRotationStrategy` implementing R1-R8 |
| `src/forex_bot/strategies/__init__.py` | re-export `CrossPairCurrencyStrengthRotationStrategy` |
| `src/forex_bot/config.py` | `CrossPairCurrencyStrengthRotationStrategyConfig` + `StrategyConfig.cross_pair_currency_strength_rotation` slot + enabled-list check |
| `tests/unit/test_cross_pair_currency_strength_rotation.py` | 57 deterministic unit tests |

## 3. Config files

| file | purpose |
|---|---|
| `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` | research-only loadable YAML; 7-pair H4 universe; frozen parameters; `trading_enabled: false`; `allow_order_submission: false`; `allow_live_trading: false`; `max_positions_per_instrument: 1` |
| `configs/approved_strategies.yaml` | **must remain `approved: []`** |
| `configs/paper.yaml` | **must NOT enable `cross_pair_currency_strength_rotation`** |
| `configs/practice.yaml` | **must NOT enable `cross_pair_currency_strength_rotation`** |

## 4. Frozen parameters (binding — runner must assert)

| parameter | value | type | role |
|---|---|---|---|
| `version` | `"0.1.0-c013"` | str | candidate id |
| `timeframe` | `"H4"` | Literal | execution timeframe |
| `currency_strength_lookback_bars` | `24` | int | rolling window (≈ 4 trading days) for the log-return-based strength feature |
| `rank_gap_threshold` | `4` | int | min `\|rank(quote) − rank(base)\|` to fire (~half the 8-currency spectrum); must be in `[1, 7]` |
| `atr_lookback` | `14` | int | H4 ATR for stop sizing |
| `atr_stop_multiple` | `2.0` | float | stop = `close[t] ± 2.0 × prior_atr_h4` |
| `max_bars_in_trade` | `6` | int | engine-enforced time stop (≈ 1 trading day) |
| `trailing_stop_atr_multiple` | `null` | None | forbidden in v1; validator rejects non-None |
| `min_atr_pips` | `{}` | dict | per-pair floor; default empty |

**Any deviation from any value above constitutes a NEW candidate.**
The runner / config loader must reject any deviation.

## 5. No-lookahead checklist (binding — Phase 3 unit tests enforce)

- [x] `cross_pair_closes` is **completed-only** (runner contract; integration contract §6).
- [x] Per-pair log returns use `iloc[-1]` and `iloc[-1 - n]` (both closed bars; `_log_return_n` checks only these endpoints).
- [x] Rank computation uses the trailing n-bar return only — never a global / full-sample rank.
- [x] Rank computation is deterministic with alphabetic tiebreak (independent of input-dict iteration order).
- [x] H4 ATR uses `iloc[-2]` (bar `t-1`'s ATR; matches CAMPAIGN_010 / 011 / 012 convention).
- [x] `close[t]` for the focal pair is the only bar-`t` field read; `high` / `low` / `open` / `volume` at bar `t` are never read.
- [x] Strategy module imports nothing from `forex_bot.broker` / `.execution` / `.loops`.
- [x] Strategy module does not import `random` / `numpy.random` / `secrets` / use builtin `hash()`.
- [x] Strategy module does not reference CAMPAIGN_002 / 010 / 011 / 012 strategy-specific parameter keys.
- [x] Strategy does not mutate `ctx.config` during signal generation.
- [x] Strategy exposes no approval-shaped public attribute.

## 6. Cross-pair-closes contract (binding for the future evidence runner)

The strategy NEVER reaches into the engine / broker / loops / data
layer directly; it relies on `ctx.config["cross_pair_closes"]` to
receive sibling-pair close series. The future runner is responsible
for:

1. Loading all 7 pairs' completed H4 candles for the relevant window
   + warm-up margin.
2. Aligning all 7 pairs to a common H4 timestamp index (intersection
   of completed bars).
3. Building per-pair closes-only `pd.Series` indexed by the common
   index.
4. Injecting the dict `{pair: pd.Series}` into
   `strategy_config["cross_pair_closes"]` for each pair's engine
   invocation.

The strategy's R3 fails closed if `cross_pair_closes` is missing or
its key-set ≠ `EXPECTED_PAIRS` (7-pair universe).

## 7. Currency-strength sign convention (binding)

| pair | non-USD currency | strength sign |
|---|---|---|
| EUR_USD | EUR | `+log_return(EUR_USD)` (USD-base) |
| GBP_USD | GBP | `+log_return(GBP_USD)` |
| AUD_USD | AUD | `+log_return(AUD_USD)` |
| NZD_USD | NZD | `+log_return(NZD_USD)` |
| USD_JPY | JPY | `−log_return(USD_JPY)` (USD-quote; invert) |
| USD_CAD | CAD | `−log_return(USD_CAD)` |
| USD_CHF | CHF | `−log_return(USD_CHF)` |

`strength["USD"] = −sum(non-USD strengths) / 7`.

## 8. Rank-gap rule (binding)

```python
sorted_currencies = sorted(strength.items(), key=lambda kv: (-kv[1], kv[0]))
ranks = {c: r for r, (c, _) in enumerate(sorted_currencies, start=1)}

base, quote = parse_pair(instrument)
rank_gap = ranks[quote] - ranks[base]
if abs(rank_gap) < rank_gap_threshold:
    return None
side = "long" if rank_gap > 0 else "short"
```

**Inclusivity at threshold:** `|rank_gap| < threshold` returns None;
equality `|rank_gap| == threshold` passes (≥ comparison). The Phase 3
unit test enforces.

## 9. Null-baseline comparison requirement (binding; CAMPAIGN_011-derived)

Per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§3 + §8 + §9, the future evidence sprint's verdict doc **must include
a "Null-baseline comparison" section** with explicit margins:

| metric | CAMPAIGN_011 floor | CAMPAIGN_013 must beat to count as "real edge" |
|---|---|---|
| aggregate expectancy R | −0.0024 | by ≥ **+0.0524 R** (→ ≥ 0.05 R) |
| aggregate profit factor | 0.91 | by ≥ **+0.19** (→ ≥ 1.10) |
| aggregate return (4 y) | −0.53 % | meaningfully positive (≥ **+5 %**) |
| `pairs_positive` | 3 / 7 | ≥ **4 / 7** |
| `fold_pass_rate` | 0 / 8 | **100 %** |

"Indistinguishable from null" REJECT band: if CAMPAIGN_013's aggregate
metrics cluster within **± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair**
of CAMPAIGN_011's, classify as **REJECT_INDISTINGUISHABLE_FROM_NULL**.

## 10. Evidence-sprint prerequisites

Before the future
`research-cross-pair-currency-strength-rotation-walk-forward-001`
evidence sprint may begin:

- [ ] Scaffold sprint (`research-cross-pair-currency-strength-rotation-001`)
      committed.
- [ ] `configs/approved_strategies.yaml` still `approved: []`.
- [ ] CAMPAIGN_002 / 010 / 011 / 012 verdicts unchanged.
- [ ] 875-pytest baseline preserved (818 prior + 57 new scaffold tests).
- [ ] Strategy module + config + tests all present and passing.
- [ ] Loops refuse; no `live-loop`.
- [ ] No `backtests/CAMPAIGN_013_*` directory yet.

## 11. Walk-forward requirements (inherited from CAMPAIGN_010 / 011 / 012)

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
| expected fold count | **8** |
| min fold count gate | **≥ 6** |

Per-fold + aggregate gates verbatim from CAMPAIGN_010 §10 /
CAMPAIGN_011 §11 / CAMPAIGN_012 precommit §10. PLUS the binding
null-baseline comparison gate from §9.

## 12. Financing overlay requirements

- **ESTIMATED + `default_stress_rate_source()` (conservative stress) only.**
- **MODELED financing refused at all 4 layers in `src/forex_bot/financing.py`** — no code change permitted.
- Per-rollover cost recorded; pair-flip table required.
- Cross-pair rotation creates **systematic long/short balance** (e.g.
  long EUR_USD often implies short USD_JPY when EUR is strong and
  JPY is weak); expected approximately net-neutral financing impact;
  per-pair recording must still pass the
  `conservative_stress_run_does_not_flip_verdict` gate.

## 13. Portfolio-risk diagnostic requirements

Standard CAMPAIGN_010 / 011 / 012 battery PLUS CAMPAIGN_013-specific
diagnostics:

- **Rank-gap distribution histogram** per pair per fold — how often
  does the gap exceed threshold?
- **Simultaneous-signal frequency** — at how many bars does the
  strategy signal on 2+, 3+, 4+, 5+ pairs concurrently?
- **`MAX_OPEN_POSITIONS_EXCEEDED` rejection rate** per fold per pair
  — expected non-trivial given `max_open_positions = 1` + cross-pair
  concurrent signals. **This is known behavior of C6, NOT a bug.**
  **Do NOT relax `max_open_positions` to "rescue" trade count.**
- **Currency-rank flip rate** — how often does a currency move from
  top-rank to bottom-rank within the lookback window?
- **Pair-direction conflict rate** — sanity check on rank derivation.

8 / 8 standard pipeline sanity checks must still pass.

## 14. Independent verifier status

- **Verifier is capability-locked to CAMPAIGN_002** (`trend_following 0.1.0`).
  Cannot validate `cross_pair_currency_strength_rotation`.
- For a **REJECT** verdict on CAMPAIGN_013: verifier **not required**.
- For a **`RESEARCH_PASS_UNAPPROVED`** verdict: verifier-extension
  sprint
  **`infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`**
  must run **before** any human approval consideration.

## 15. Explicit no-approval statement

- Even a clean PASS verdict produces `RESEARCH_PASS_UNAPPROVED`.
- `configs/approved_strategies.yaml` cannot change as part of any
  research sprint. Adding `cross_pair_currency_strength_rotation`
  requires a deliberate, separate human action per
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).
- A passing CAMPAIGN_013 still has the live-promotion financing
  blocker (MODELED required for live; only ESTIMATED + conservative
  stress is currently authorized).

## 16. Unexpected-PASS protocol (binding for the future evidence sprint)

If the future evidence sprint reports a verdict whose per-fold +
aggregate + financing gates ALL pass AND the null-baseline comparison
margins are met:

1. **Do not silently update STRATEGY_STATUS to `approved`** — that
   would violate this pre-commit.
2. **Do not modify `configs/approved_strategies.yaml`** — that
   requires a separate human approval action.
3. **Write the verdict doc with classification `RESEARCH_PASS_UNAPPROVED`** —
   not `APPROVED`.
4. **Open the suggested verifier-extension follow-up sprint**
   `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`.
5. **Surface for human review** the seven binding artifacts:
   walk-forward result, financing overlay, risk diagnostics
   (including CAMPAIGN_013-specific rank-gap/simultaneous-signal/
   rejection-rate diagnostics), the null-baseline comparison section,
   the data provenance doc, the STRATEGY_APPROVAL_PROCESS.md trail,
   and the verifier readiness.

This is not a recipe to approve. It is a recipe to **escalate cleanly
to human review**.

## 17. Rejection criteria

CAMPAIGN_013's verdict is **REJECT** if any of:

| level | criterion |
|---|---|
| per-fold | any gate from §11 fails on any test fold |
| aggregate | any gate from §11 fails |
| financing | conservative-stress overlay flips a passing verdict |
| null-baseline | metrics within ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair of CAMPAIGN_011 (`REJECT_INDISTINGUISHABLE_FROM_NULL`) |
| no-lookahead | any structural-audit unit test fails |
| pipeline | runner aborts (`BLOCKED`) — including if the runner cannot satisfy the cross-pair integration contract |

## 18. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md), [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md), [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md) (sibling pre-commits — same gate vector)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)

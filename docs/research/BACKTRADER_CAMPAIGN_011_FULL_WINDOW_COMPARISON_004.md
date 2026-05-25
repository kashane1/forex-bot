# Backtrader CAMPAIGN_011 — Phase 4 full-window comparison

**Date:** 2026-05-25
**Branch:** `infra-backtrader-secondary-lane-004-campaign-011`
**Phase:** 4 of `BACKTRADER_CAMPAIGN_011_004_PLAN.md`
**`strategy_evidence: false`**

> The **initial** (pre-fix) Backtrader-lane CAMPAIGN_011 output, run by
> Phase 3 (commit `de110be`), classified by the existing
> `research/backtrader_lane/compare.py` harness with the tight
> CAMPAIGN_011 tolerance bands defined in
> `CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md` §9. The divergence is
> preserved; the Backtrader-lane fix lands in Phase 5. CAMPAIGN_011
> remains REJECT / null diagnostic anchor by design.

## 1. Exact command

```bash
python scripts/compare_backtrader_parity.py \
    --campaign CAMPAIGN_011 \
    --backtrader-results research/backtrader_lane/results/campaign_011_full_window_004/ \
    --bespoke-reference research/lean_parity/campaign_011_h4_bespoke_reference.json \
    --output backtests/diagnostics/backtrader_campaign_011_full_window_004_prefix \
    --trade-count-tolerance-pct 0.0 \
    --expectancy-r-tolerance 0.005 \
    --return-pct-tolerance 0.10 \
    --win-rate-tolerance 0.001
```

## 2. Backtrader artifact path

`research/backtrader_lane/results/campaign_011_full_window_004/backtrader_summary.json`
(gitignored; committed run doc at
`BACKTRADER_CAMPAIGN_011_FULL_WINDOW_RUN_004.md`).

## 3. Bespoke reference path

`research/lean_parity/campaign_011_h4_bespoke_reference.json`
(sha256 `fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78`).

## 4. Pre-fix harness comparison summary

| field | value |
|---|---|
| BT total trades | **2 808** |
| Bespoke total trades | **2 800** |
| Δ | **+8 (≈ +0.29 %)** |
| Overall classification (harness) | **`TOLERABLE_DRIFT`** |

### 4.1 Per-pair classification (harness output)

| instrument | BT trades | bespoke trades | Δ % | classification |
|---|---|---|---|---|
| AUD_USD | 385 | 385 | +0.00 % | `PASS` |
| EUR_USD | 395 | 394 | +0.25 % | `TOLERABLE_DRIFT` |
| GBP_USD | 401 | 400 | +0.25 % | `TOLERABLE_DRIFT` |
| NZD_USD | 401 | 400 | +0.25 % | `TOLERABLE_DRIFT` |
| USD_CAD | 396 | 394 | +0.51 % | `TOLERABLE_DRIFT` |
| USD_CHF | 411 | 409 | +0.49 % | `TOLERABLE_DRIFT` |
| USD_JPY | 419 | 418 | +0.24 % | `TOLERABLE_DRIFT` |

The harness lands at `TOLERABLE_DRIFT` because the per-pair Δ % is
inside the wider band (10 %) but outside the tight band (0 %), and
the harness does not check `expectancy_r` / `return_pct` from the BT
summary out of the box (the BT runner does not emit per-pair
expectancy_r in `backtrader_summary.json`; that's a known
`compare.py` limitation documented in §2 of the comparison harness).

### 4.2 Manual per-pair expectancy-R / return-% / win-rate diff

Derived from the BT trade JSONL and the bespoke reference JSON
(numbers rounded to 4 dp for the bespoke side per the contract):

| instrument | BT trades | bespoke trades | Δ trades | BT win_rate | bespoke win_rate | Δ win_rate | bespoke expectancy_r |
|---|---|---|---|---|---|---|---|
| EUR_USD | 395 | 394 | +1 | 0.4734 | 0.4721 | +0.0013 | -0.0496 |
| GBP_USD | 401 | 400 | +1 | 0.4738 | 0.4750 | -0.0012 | -0.0073 |
| USD_JPY | 419 | 418 | +1 | 0.4940 | 0.4952 | -0.0012 | +0.0004 |
| AUD_USD | 385 | 385 |  0 | 0.4753 | 0.4753 | +0.0000 | -0.0646 |
| USD_CAD | 396 | 394 | +2 | 0.4697 | 0.4721 | -0.0024 | -0.0161 |
| USD_CHF | 411 | 409 | +2 | 0.5061 | 0.5061 | +0.0000 | +0.0503 |
| NZD_USD | 401 | 400 | +1 | 0.4763 | 0.4750 | +0.0013 | -0.0265 |

Three pairs (EUR_USD, GBP_USD, USD_JPY, USD_CAD, USD_CHF, NZD_USD)
breach the contract's win-rate band (abs Δ > `0.0010`); two pairs
hold (AUD_USD exact; one of the others within `0.0010`). **Every
non-AUD_USD pair breaches the contract's exact-trade-count band
(Δ ≥ 1).**

## 5. Divergence classification (this sprint)

| dimension | finding | sprint-plan label |
|---|---|---|
| trade count, exact-match contract | breached on 6 of 7 pairs (+1 to +2 each); +8 overall | **`SIGNAL_RULE_MISMATCH`** (the rule that defines when a signal is first eligible to fire differs between BT and bespoke) |
| harness verdict under wider band | within 10 %; `TOLERABLE_DRIFT` | informational — the contract is tighter |
| expectancy R | not measured by the harness for BT (missing field) | n/a |
| seed derivation | byte-identical (31 unit tests in Phase 1 prove this on 6 known inputs); seed input contains no bar-`t` price data | **not the cause** |
| timestamp alignment | identical for trades 2..N when both sides fire | **not the cause** |
| stop / exit ordering | identical (time stop @ 6, no trailing) | **not the cause** |
| sizing / PnL formula | identical (R formula matches bespoke `engine.py:411-415`; sprint-003 fix carried forward) | **not the cause** |
| **warmup window** | BT honours only R1's `len(df) >= atr_lookback + 2 = 16`; bespoke engine respects `strategy.warmup_bars_required() = 32` (declared in `src/forex_bot/strategies/random_entry_anchor.py:99-101`) | **load-bearing cause** |

The sprint-004 plan's binding classification for this delta is
**`SIGNAL_RULE_MISMATCH`** — the harness lands at TOLERABLE_DRIFT
because the delta is small in percent terms, but under the
CAMPAIGN_011 contract (exact trade-count match required), the rule
about when the strategy first becomes eligible to fire differs
between BT and bespoke. The fix lands in Phase 5.

## 6. Suspected causes (verified)

| candidate cause | rejected / confirmed |
|---|---|
| SHA-256 seed input drift (microsecond precision, ISO format) | **rejected** — Phase 1 unit tests assert byte-identical seed on 6 known timestamps |
| Wrong `master_seed` | **rejected** — frozen at `20260523`, verified by `_assert_frozen(...)` at load |
| BT-lane R formula bug | **rejected** — the R formula already matches bespoke `engine.py:411-415` exactly (sprint-003 fix carried forward) |
| Pair ordering | **rejected** — both sides use the canonical 7-pair order; AUD_USD shows 0-trade Δ |
| Time-stop / adverse-stop ordering | **rejected** — identical to bespoke |
| **Warmup-window off-by-N** | **CONFIRMED** — BT honours R1 (16 bars) but not `warmup_bars_required()=32`. EUR_USD example: BT fires at bar 31 (2020-01-08T22:00:00); bespoke skips bars 0-31 entirely |
| Bespoke-engine bug | **rejected** — the bespoke engine respects the strategy's declared `warmup_bars_required()` per `engine.py:204,220`, which is the correct behaviour |

## 7. Whether any Backtrader-lane bug was found

**Yes.** The BT adapter at
`research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`
implements R1 (`len(df) >= atr_lookback + 2`) but does **not** honour
`warmup_bars_required() = 32` from
`src/forex_bot/strategies/random_entry_anchor.py:99-101`. The fix is
to bump the warmup check to `_bar_count(self) < 33` (matching
bespoke's `for i in range(warmup, len(df))` with `warmup = 32` plus
the +1 for Backtrader's 1-based `len(self)`). Lands in Phase 5.

## 8. Whether any bespoke-engine bug was found

**No.** The bespoke engine correctly reads
`strategy.warmup_bars_required()` and respects it via
`warmup = max(self.strategy.warmup_bars_required(), 5)` at
`src/forex_bot/backtesting/engine.py:204`. The strategy declares
`warmup_bars_required() = 32` with the explicit comment "ATR(14)
needs ≥15 bars; +1 for accessing index -2; small buffer". The
bespoke side is doing exactly what it documents.

## 9. Does this approve CAMPAIGN_011?

**No.** This sprint:

- did not change CAMPAIGN_011 rules,
- did not tune any parameter,
- did not change CAMPAIGN_011's REJECT verdict,
- did not change `configs/approved_strategies.yaml`,
- did not change the bespoke engine,
- did not change the no-RiskEngine bespoke reference JSONs,
- did not enable paper / demo / live.

CAMPAIGN_011 remains REJECT / null diagnostic anchor by design.
`strategy_evidence: false`. Paper / demo / live remain blocked.

## 10. Local generated files NOT committed

| file | location | committed | reason |
|---|---|---|---|
| `comparison_summary.json` (pre-fix) | `backtests/diagnostics/backtrader_campaign_011_full_window_004_prefix/` | **yes** (small, ≤ 4 KB) | committable diagnostic artefact |
| `comparison_summary.md` (pre-fix) | same | **yes** (small) | committable |
| BT raw outputs | `research/backtrader_lane/results/campaign_011_full_window_004/` | **no** | gitignored |
| bespoke trade dump | `backtests/diagnostics/campaign_011_norisk/full_window_trades.jsonl` | **no** | gitignored by sprint 001 of `infra-bespoke-campaign-011-norisk-reference-*` |

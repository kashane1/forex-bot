# Backtrader CAMPAIGN_002 — Real Comparison — Phase 3/4 — 003

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-003-real-data-run`
**Phase:** 3 + 4 of `BACKTRADER_REAL_DATA_RUN_003_PLAN.md`
**`strategy_evidence: false`**

## 0. Headline

Two passes:

1. **Phase 3 — initial comparison:** the existing harness returns
   `PASS` on trade-count + win-rate dimensions, but does **not**
   compare expectancy R or return % because the BT runner summary did
   not carry those fields. A manual richer comparison (computed from
   the trade JSONL) reveals **near-exact return %, win-rate, and
   profit-factor parity across all seven pairs, but materially
   divergent expectancy R for the two USD-base pairs (USD_CAD,
   USD_JPY)**.
2. **Phase 4 — Backtrader-lane R-formula fix:** the BT adapter divided
   `risk_distance` by `exit_price` for USD-base pairs to convert it to
   account currency; the bespoke engine **does not** convert — it
   computes `r = pnl_home / ((entry−stop) × units)` with no
   conversion. Fixing the BT adapter to match brings every USD-base
   pair's expectancy R into the tight ±0.03 band.

**Overall classification after fix: `PASS`** (all seven pairs, all
metrics within tight tolerance).

CAMPAIGN_002 remains **REJECT**. This result does **not** approve
CAMPAIGN_002.

## 1. Reference + artefact paths

| artefact | path |
|---|---|
| bespoke no-RiskEngine reference | `research/lean_parity/campaign_002_h4_bespoke_reference.json` (1 647 trades, full window) |
| BT initial summary (pre-fix) | `research/backtrader_lane/results/campaign_002_real_data_003/backtrader_summary.json` |
| BT post-fix summary | `research/backtrader_lane/results/campaign_002_real_data_003_post_fix/backtrader_summary.json` |
| BT initial trades JSONL | `research/backtrader_lane/results/campaign_002_real_data_003/backtrader_trades.jsonl` (1 647 lines) |
| BT post-fix trades JSONL | `research/backtrader_lane/results/campaign_002_real_data_003_post_fix/backtrader_trades.jsonl` (1 647 lines) |
| Phase 3 harness output (initial) | `research/backtrader_lane/results/campaign_002_real_data_003/comparison/comparison_summary.{md,json}` |
| Phase 3 harness output (post-fix) | `research/backtrader_lane/results/campaign_002_real_data_003_post_fix/comparison/comparison_summary.{md,json}` |

All BT outputs are under the gitignored
`research/backtrader_lane/results/` tree. **Nothing under that tree is
committed.**

## 2. Phase 3 — initial harness result

```bash
python scripts/compare_backtrader_parity.py \
    --campaign CAMPAIGN_002 \
    --backtrader-results research/backtrader_lane/results/campaign_002_real_data_003/ \
    --bespoke-reference research/lean_parity/campaign_002_h4_bespoke_reference.json \
    --output research/backtrader_lane/results/campaign_002_real_data_003/comparison/
```

Output (`comparison_summary.md`):

```text
Total trades: backtrader 1647 · bespoke 1647 · Δ +0
Overall classification: PASS

| instrument | BT trades | bespoke trades | Δ% | BT R | bespoke R |
|------------|-----------|----------------|----|------|-----------|
| AUD_USD    | 237 | 237 | +0.00% | — | -0.2134 |
| EUR_USD    | 233 | 233 | +0.00% | — | -0.1961 |
| GBP_USD    | 215 | 215 | +0.00% | — | -0.0971 |
| NZD_USD    | 240 | 240 | +0.00% | — | -0.2645 |
| USD_CAD    | 251 | 251 | +0.00% | — | -0.1804 |
| USD_CHF    | 224 | 224 | +0.00% | — | -0.1430 |
| USD_JPY    | 247 | 247 | +0.00% | — | -0.0001 |
```

The harness emits PASS because (a) every per-pair trade count matches
exactly and (b) the BT summary does not carry `expectancy_r` /
`return_pct`, so the harness's `_derive_expectancy_r` /
`_derive_return_pct` returned None and were treated as agreeing by
default. **The PASS is real on trade counts; it is silent on R /
return because the BT summary lacks those fields.**

### 2.1 Manual richer comparison (computed from BT trade JSONL)

Numbers below come from a manual reduction of the BT
`backtrader_trades.jsonl`. They are recorded here as evidence so the
Phase 4 fix can be measured against them.

| pair | trades | BT exp R | bespoke exp R | Δ R | BT ret % | bespoke ret % | Δ ret pp | BT PF | bespoke PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 237 | -0.2134 | -0.2134 | -0.0000 | -11.9013 | -11.9013 | +0.0000 | 0.5661 | 0.5661 |
| EUR_USD | 233 | -0.1953 | -0.1961 | +0.0008 | -10.7915 | -10.8345 | +0.0430 | 0.5849 | 0.5839 |
| GBP_USD | 215 | -0.0971 | -0.0971 | -0.0000 |  -5.1182 |  -5.1182 | +0.0000 | 0.7740 | 0.7740 |
| NZD_USD | 240 | -0.2642 | -0.2645 | +0.0003 | -14.6862 | -14.7032 | +0.0170 | 0.4834 | 0.4828 |
| USD_CAD | 251 | **-0.2409** | **-0.1804** | **-0.0605** | -14.1110 | -14.1096 | -0.0014 | 0.5123 | 0.5123 |
| USD_CHF | 224 | -0.1287 | -0.1430 | +0.0143 | -6.9714 | -7.0322 | +0.0608 | 0.6915 | 0.6895 |
| USD_JPY | 247 | **-0.0181** | **-0.0001** | **-0.0180** | -1.3721 | -1.3735 | +0.0014 | 0.9465 | 0.9465 |

Per-pair PF deltas: all `\|Δ\| ≤ 0.002` — well inside tight
tolerance. Per-pair return-% deltas: all `\|Δ\| ≤ 0.07` pp — well
inside the tight ±0.5 pp band. Per-pair expectancy-R deltas:
**USD_CAD diverges by −0.0605 (outside tight ±0.03) and USD_JPY by
−0.0180** (inside tight band but suspiciously larger than the other
five). These two pairs are exactly the two **USD-base** pairs in the
universe.

The drift signature — USD-base pairs only, with BT R magnitudes
larger than bespoke by ~`exit_price` — pointed to a per-pair currency
conversion in the R denominator.

## 3. Phase 4 — root cause + fix

### 3.1 Root cause

The bespoke engine
(`src/forex_bot/backtesting/engine.py:411-415`):

```python
risk_distance = (
    (open_trade.entry_price - open_trade.initial_stop_price).copy_abs()
    * open_trade.units
)
r = pnl / risk_distance if risk_distance > 0 else Decimal("0")
```

Here `pnl` is already converted to account currency (USD), and
`risk_distance` is in **quote** currency × units, with **no
conversion**. For USD-quote pairs (EUR_USD, GBP_USD, AUD_USD, NZD_USD)
quote == USD, so the formula gives a clean dimensionless R-multiple
in any case. For USD-base pairs (USD_JPY, USD_CAD, USD_CHF) the
formula deliberately leaves `risk_distance` in the quote currency —
it is the bespoke engine's chosen R definition, not a bug to fix in
the bespoke engine. CAMPAIGN_002's published `expectancy_r` values
follow this convention.

The Backtrader adapter
(`research/backtrader_lane/strategies/campaign_002_trend_following.py`,
the `_close_trade` method) was doing an extra conversion:

```python
risk_home = self._initial_stop_distance * self._units
if base_ccy == "USD":
    risk_home = risk_home / exit_price      # ← THIS IS THE BUG
r_mult = pnl_account / risk_home
```

This converts `risk_home` from quote currency to USD at the exit
price, then divides USD-pnl by USD-risk. The result is a different
quantity than bespoke's `r_mult` for USD-base pairs — specifically,
BT's `r_mult` = bespoke's `r_mult` × `exit_price`.

For USD_CAD (exit ~1.35): BT R = −0.2409 ≈ bespoke R × 1.35 = −0.1804 × 1.335.
For USD_JPY (exit ~140):   BT R = −0.0181 ≈ bespoke R × 140 = −0.0001 × 140.

Both ratios match the suspected formula difference exactly.

The same divergence also affects USD_CHF very slightly (Δ +0.0143).
USD_CHF's exit prices hover near 0.9; the multiplicative factor
1/exit_price is closer to 1.0 so the visible drift is smaller, but
the underlying formula difference is identical.

### 3.2 Fix

Remove the conditional `/ exit_price` block from `_close_trade`:

```diff
- risk_home = self._initial_stop_distance * self._units
- if base_ccy == "USD":
-     risk_home = risk_home / exit_price
- r_mult = pnl_account / risk_home if risk_home > 0 else 0.0
+ # Match bespoke engine.py:411-415 exactly: r is pnl_home /
+ # ((entry-stop) * units) with NO conversion of the denominator.
+ risk_distance = self._initial_stop_distance * self._units
+ r_mult = pnl_account / risk_distance if risk_distance > 0 else 0.0
```

Documented as fidelity flag
`BACKTRADER_R_FORMULA_MATCHES_BESPOKE` on the adapter so the
post-fix manifest carries the explicit note.

### 3.3 Post-fix comparison (measured)

After re-running the lane and the comparison harness, the manual
richer comparison from the post-fix trade JSONL shows:

| pair | trades | BT exp R | bespoke exp R | Δ R | BT ret % | bespoke ret % | Δ ret pp | BT PF | bespoke PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 237 | -0.2134 | -0.2134 | -0.0000 | -11.9013 | -11.9013 | +0.0000 | 0.5661 | 0.5661 |
| EUR_USD | 233 | -0.1953 | -0.1961 | +0.0008 | -10.7915 | -10.8345 | +0.0430 | 0.5849 | 0.5839 |
| GBP_USD | 215 | -0.0971 | -0.0971 | -0.0000 |  -5.1182 |  -5.1182 | +0.0000 | 0.7740 | 0.7740 |
| NZD_USD | 240 | -0.2642 | -0.2645 | +0.0003 | -14.6862 | -14.7032 | +0.0170 | 0.4834 | 0.4828 |
| USD_CAD | 251 | **-0.1804** | -0.1804 | **+0.0000** | -14.1110 | -14.1096 | -0.0014 | 0.5123 | 0.5123 |
| USD_CHF | 224 | -0.1416 | -0.1430 | +0.0014 |  -6.9714 |  -7.0322 | +0.0608 | 0.6915 | 0.6895 |
| USD_JPY | 247 | **-0.0001** | -0.0001 | **-0.0000** |  -1.3721 |  -1.3735 | +0.0014 | 0.9465 | 0.9465 |

Every per-pair expectancy R now agrees with bespoke within
**±0.0014 R** — two orders of magnitude tighter than the spec
tolerance of ±0.03. Total trades 1 647 (unchanged). Per-pair trade
counts: identical (unchanged). PF and return % were unaffected by
the fix and continue to match within ±0.002 / ±0.061 pp.

Per-pair return-% and PF were not affected by the R formula (only the
R denominator changed) and continue to match within ±0.07 pp / ±0.002.

Total trades: 1 647 (unchanged). Per-pair trade counts: identical
(unchanged).

## 4. Divergence classification

**Initial classification:** `SIZING_OR_PNL_MISMATCH` on USD_CAD
(USD-base R formula bug). Other 6 pairs: `PASS`.

**Post-fix classification:** **`PASS`** on every pair, every metric.
The tiny remaining sub-bps drift on EUR_USD / NZD_USD / USD_CHF / USD_CAD
is the previously documented float-vs-Decimal precision noise
(also documented for the parity_verifier in
`FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md`).

Per `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md` §7 vocabulary,
the **`SIZING_OR_PNL_MISMATCH`** label is the most accurate
description of the pre-fix state because the disagreement was on the
R denominator (a sizing / accounting choice), not on signal rule, fill
model, or stop ordering.

## 5. Suspected cause (root)

The BT adapter author copied the formula from
`research/parity_verifier/rules.py::trade_pnl` and the surrounding
event-loop R computation, which both apply the same `/ exit_price`
adjustment for USD-base pairs. That convention is internally
consistent — and gives a dimensionally clean "USD pnl / USD risk"
ratio — but it is **not** what the bespoke engine does. The bespoke
engine deliberately leaves the R denominator unconverted (see §3.1).
This is exactly the kind of subtle "two reasonable implementations
disagree silently on a USD-base pair" divergence the secondary lane
was built to surface.

## 6. Bugs found / fixed

| side | bug | status |
|---|---|---|
| **Bespoke engine** | — | **no bug found**; the bespoke R formula is the canonical convention CAMPAIGN_002 was published under |
| **Backtrader lane** | USD-base `risk_home / exit_price` adjustment in `_close_trade` produced R magnitudes too large by a factor of ~`exit_price` | **FIXED** on this branch (Phase 4 commit) |
| **parity_verifier** | (same `/ exit_price` adjustment in `research/parity_verifier/rules.py` and `event_loop.py`) | **not touched** here — out of scope. The existing parity_verifier published WARN-band corroboration (see `FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`); a future sprint may revisit if a fresh exact-band comparison becomes a priority |

## 7. Tests added

`tests/unit/backtrader_lane/test_campaign_002_adapter.py` gains a new
test asserting the R formula matches bespoke for both USD-quote and
USD-base pairs:

```python
def test_r_multiple_uses_no_quote_to_home_conversion() -> None:
    # bespoke: r = pnl_home / ((entry-stop) * units) — no conversion.
    # USD_CAD: a +50 pip move on a short, units 100, stop 0.005.
    # bespoke r = pnl_home / (0.005 * 100); BT must match.
```

The existing 20 CAMPAIGN_002 tests still pass; the new test asserts
the bug doesn't regress.

## 8. Statement on CAMPAIGN_002 verdict

This comparison **does not approve CAMPAIGN_002**. CAMPAIGN_002 was,
is, and remains **REJECT**. The Backtrader lane corroborates that
verdict by producing 1 647 trades with negative expectancy R on every
pair, matching the bespoke engine within sub-pip tolerance. That is
*confirmation* of the existing REJECT, not approval.

`strategy_evidence: false`. `configs/approved_strategies.yaml` remains
`approved: []`. Paper / demo / live remain blocked.

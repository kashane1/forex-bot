# Non-time-bar feasibility protocol (diagnostic-only)

**Status:** diagnostic protocol. **No campaign number. No verdict. No approval path.**
**Sprint:** `research-range-volatility-bar-feasibility-001`

---

## 0. Nature of this protocol

This is a **diagnostic feasibility protocol**. It exists to characterise the
*economics and cadence* of range bars and volatility bars across thresholds and
pairs, so a future human decision can tell whether the non-time-bar lane is worth
any further strategy effort after CAMPAIGN_029.

It explicitly is **not**:

- a campaign (no number; this sprint must never create CAMPAIGN_030),
- a train/validation/test protocol (it produces **no** train/validation/test
  verdict and opens **no** test lockbox),
- an approval path (nothing it outputs can add a name to
  `configs/approved_strategies.yaml`),
- a parameter-tuning loop (no threshold is "optimised"; the grid is fixed up front),
- a strategy execution (it computes **no** entry/exit signals, **no** PnL, **no**
  labelled returns). The only "strategy-like" arithmetic it inherits is the
  **cost model** from C029 — half-spread + slippage per side — applied as a
  *geometry* calculation to candidate stop sizes, not to any trade.

Full bars and any per-bar ledgers stay **local / gitignored**. Only compact
summaries, matrices, and docs are committed.

### 0.1 Why the test lockbox is not touched

The test lockbox seals **strategy returns** on `2025-01-01 → 2026-05-20`. This
protocol computes only **market-microstructure geometry** (how often bars form, how
far price overshoots a threshold, what the bid/ask spread is). To be doubly safe the
default diagnostic window is the **C029 train window** `2021-05-27 → 2023-12-31`,
which is entirely outside the lockbox. No sealed data is read, and no returns are
ever computed, so the lockbox semantics are preserved by construction.

## 1. Diagnostic dimensions (fixed grid — no tuning)

### Range bars (close a bar when price moves N pips from the bar open)
- 10 pip
- 15 pip
- 20 pip
- 25 pip
- 30 pip

### Volatility bars — `true_range` (cumulative true range reaches threshold)
- 20 pip
- 30 pip
- 40 pip
- 50 pip

### Volatility bars — `abs_close` (cumulative |close-to-close| reaches threshold)
- 20 pip
- 30 pip
- 40 pip
- 50 pip

### Pairs
- **USD_JPY** — primary (the C029 instrument).
- All seven majors — `EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF,
  NZD_USD` — for cadence/cost feasibility.
- Full strategy evidence is **not** run on any pair. Cross-pair work is strictly
  the diagnostic geometry/cost layer and stays compact.

Pip size follows `forex_bot.data.non_time_bars.pip_size`: `0.01` for JPY-quote
pairs, `0.0001` otherwise.

## 2. Feasibility metrics (per pair × bar_type × threshold)

**Cadence / geometry** (from the existing `non_time_bars` builders):
- bar count (completed bars in window)
- bars per day / per month / per year (normalised by actual elapsed weekday span)
- median wall-clock duration per bar (and p25/p75/mean)
- average M1 rows per bar (`source_count`)
- session distribution (Tokyo / London / overlap / NY / rollover, UTC buckets)
- weekday distribution
- multi-threshold crossing rate (bars whose forming M1 candle crossed the threshold
  more than once — a small-threshold noise flag)
- average overshoot (pips past the threshold at completion)

**Cost / economics** (the new layer this sprint adds, from M1 bid/ask):
- average spread in pips, by pair and by session
- estimated round-trip cost in pips = `full spread + 2 × slippage` (slippage default
  0.2 pip/side, matching C029)
- cost-to-threshold ratio = `round_trip_cost / threshold`
- cost-to-stop-risk ratio = `round_trip_cost / nominal_stop`, where the nominal stop
  is `stop_multiple × threshold` (see §3)
- approximate minimum gross expectancy (per-R) needed to survive cost = the
  cost-to-stop-risk ratio (break-even gross edge per unit risk)
- C029-equivalent cost floor: at 10-pip / 24.05-pip stop, observed
  `cost_to_risk ≈ 0.095`, against an observed best gross edge of `+0.084R` →
  cost-defeated. This anchors the "achievable gross edge" benchmark at **~0.08R** for
  this lab.

## 3. Nominal stop assumptions (geometry, not a strategy)

A non-time-bar breakout/continuation strategy must place a stop somewhere. The
nominal stop is expressed as a multiple of the bar threshold:

- **Range bars:** baseline nominal stop = **2 × threshold** (this reproduces C029,
  where the 10-pip bar gave a ~24-pip i.e. ~2.4× stop). A wider-stop scenario of
  **3–4 × threshold** is also reported.
- **Volatility bars:** report both **1 × threshold** and **2 × threshold** stop
  scenarios (a true_range/abs_close bar of size T is itself a volatility unit, so a
  1× stop is plausible; 2× is the conservative scenario).

These multiples are documented assumptions for a *break-even cost* calculation. They
do not define, optimise, or approve any strategy.

## 4. Decision labels (diagnostic hypotheses — NOT gates)

Each (pair × bar_type × threshold) cell is labelled with exactly one of:

- `FEASIBLE_FOR_STRATEGY_RESEARCH`
- `FEASIBLE_ONLY_WITH_LARGER_STOPS`
- `COST_DOMINATED`
- `TOO_SPARSE`
- `TOO_NOISY`
- `INCONCLUSIVE`

These are **hypotheses about where it is even worth looking**, not approvals and not
gate passes. A `FEASIBLE_*` label means "cost does not by itself kill this cell" — it
does **not** assert an edge exists. Finding an edge still requires an external
thesis and a fresh pre-committed front-gated campaign.

### 4.1 Analyst-set thresholds (documented, not derived)

Cost (evaluated at the baseline stop multiple of §3):
- `cost_to_risk ≤ 0.05` → **cost-feasible**: a modest, historically-plausible gross
  edge (~0.05–0.08R) could survive.
- `0.05 < cost_to_risk ≤ 0.10` → **marginal**: needs an unusually strong gross edge;
  C029 lived here (0.095) and died.
- `cost_to_risk > 0.10` → **cost-dominated** at this stop.

Cadence (bars per year, window-normalised):
- `< 200` bars/year → **too sparse** (cannot accumulate evidence comfortably).
- `200 … 20,000` bars/year → **sane**.
- `> 20,000` bars/year → **very high cadence** (cost is paid per bar; flags toward
  noisy/over-trading).

Noise:
- multi-threshold crossing rate `> 0.10` → **too noisy** (threshold is small relative
  to a single M1 candle's range; bar boundaries are dominated by intra-candle jumps).

### 4.2 Label assignment priority

For each cell, apply in order (first match wins):

1. `bar_count < 30` or no completed bars → `INCONCLUSIVE`.
2. bars/year `< 200` → `TOO_SPARSE`.
3. multi-threshold rate `> 0.10` **or** bars/year `> 20,000` → `TOO_NOISY`.
4. `cost_to_risk(baseline stop) ≤ 0.05` → `FEASIBLE_FOR_STRATEGY_RESEARCH`.
5. `cost_to_risk(baseline) > 0.05` but `cost_to_risk(wider stop)` ≤ 0.05 (range:
   wider = 4×; volatility: wider = 2×) → `FEASIBLE_ONLY_WITH_LARGER_STOPS`.
6. otherwise → `COST_DOMINATED`.

(If multiple conditions could apply, the priority order resolves ties: data
sufficiency first, then sparsity, then noise, then cost.)

## 5. Outputs (compact, committed)

Under `research/non_time_bar_feasibility/`:
- `feasibility_summary.json` — top-level run metadata + per-cell summary index
- `feasibility_matrix.csv` — one row per (pair, bar_type, threshold): cadence + cost
  + label (the human-scannable matrix)
- `pair_threshold_summary.json` — nested per-pair → per-threshold detail
- `cost_floor_summary.json` — per (pair, bar_type, threshold) cost floor + break-even
  gross edge + C029 comparison
- `non_time_bar_feasibility_report.md` — human-readable narrative
- `feasibility_manifest.json` — provenance (window, grid, code version, no-secrets)

Local-only / gitignored: full generated bars, M1 caches, any per-bar CSVs.

## 6. Reuse, not duplication

The bar geometry comes from the existing, tested
`forex_bot.data.non_time_bars` builders (`stream_range_bars`,
`stream_volatility_bars`). This protocol adds only the **pure economics /
classification layer** (`forex_bot.research.non_time_bar_feasibility`) plus a thin
driver script. No bar-builder logic is re-implemented.

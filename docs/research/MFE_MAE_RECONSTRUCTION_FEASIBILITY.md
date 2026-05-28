# MFE/MAE Reconstruction — Feasibility & Design

**Date:** 2026-05-28 · **Sprint:** `infra-trade-lifecycle-feature-capture-and-stop-diagnostics-001`
**Status:** design complete · real reconstruction **BLOCKED_LOCAL_DATA** in this checkout.

Diagnostic only. Reconstructing per-bar excursion does **not** rerun any
strategy, change any verdict, tune any parameter, or approve anything.

## Question

Can we reconstruct each C022 trade's per-bar path — and thus its maximum
favorable excursion (MFE) and maximum adverse excursion (MAE) in R units —
from data already materialized locally, *without* rerunning the frozen strategy?

## 1. Do the C022 trade artifacts carry enough to anchor a reconstruction?

The committed per-pair CSVs
(`backtests/CAMPAIGN_022_h4_h1_pullback_resolution/{train,validation}/base/*_trades.csv`)
carry every field needed to *anchor* a path join:

| needed field | column | present |
|---|---|---|
| instrument | `instrument` | ✅ |
| side | `side` | ✅ |
| entry time | `entry_time` (ISO, tz-aware UTC) | ✅ |
| exit time | `exit_time` (ISO, tz-aware UTC) | ✅ |
| entry price | `entry_price` | ✅ |
| initial stop | `stop_price` | ✅ |
| execution timeframe | M15 (campaign-fixed; not per-row but known) | ✅ (constant) |

So the **anchor data is sufficient**: for each trade we know the instrument,
direction, the entry→stop risk distance (R unit), and the `[entry_time,
exit_time]` window to walk. What is *missing* is the per-bar price path itself —
that lives in the candle store, not the trade CSV. (No MFE/MAE column exists;
`protective_stop_arm_mfe_r` is only populated when a protective stop armed and
is therefore not a general MFE.)

## 2. Can local materialized M15 candles be joined safely by timestamp?

C022 executed on materialized `m1_derived` M15 candles from a **local research
Postgres** (`localhost/forex_bot`, source `H4M1`/`m1_materialized`), per
`CAMPAIGN_022_TRAIN_VALIDATION_RESULT.md`. The join is therefore well-defined:
for a trade on instrument *X* over `[entry_time, exit_time]`, load completed M15
candles for *X* in that window and walk them in order.

**Availability in this checkout (2026-05-28):**

- `FOREX_BOT_RESEARCH_DATABASE_URL` is **unset**.
- Default `postgresql://localhost/forex_bot` refuses the connection
  (`fe_sendauth: no password supplied`) — no credentials configured here.
- `data/bot.sqlite3` exists but holds **0 candle rows** (empty operational DB).

→ **Per-bar reconstruction is BLOCKED_LOCAL_DATA in this environment.** The
design and code below are complete and unit-tested against synthetic candles;
they will run unchanged once a populated materialized M15 store is reachable.

## 3. Path-reconstruction rules (design)

Implemented in `src/forex_bot/research/mfe_mae.py` (`compute_mfe_mae`):

1. **Window** — use only candles with `entry_time < bar.timestamp <= exit_time`.
   Bars at/before entry and strictly after exit are dropped — **no lookahead**
   past the realized exit.
2. **R unit** — `risk = |entry_price − initial_stop_price|`. Favorable and
   adverse excursions are expressed as multiples of `risk`. The hard stop sits at
   exactly `−1R` by construction.
3. **Per bar** —
   - long: `fav = (high − entry)/risk`, `adv = (low − entry)/risk`
   - short: `fav = (entry − low)/risk`, `adv = (entry − high)/risk`
   - `MFE_r = max(fav)`, `MAE_r = min(adv)` over the window.
4. **Threshold flags** — `reached_+0.25R / +0.5R / +1.0R` (MFE crossings) and
   `touched_−0.5R / −0.9R` (MAE crossings).
5. **Ordering vs stop** — track the first bar index that crosses each favorable
   threshold and the first bar that touches the stop (`adv ≤ −1R`). A threshold
   counts as reached *before* the stop only if its bar strictly precedes the
   stop bar.
6. **Intrabar assumption** — when one bar touches both a favorable threshold and
   the stop, order is unknowable. Default `intrabar="adverse_first"` assumes the
   **stop happened first** (conservative: never overstates a hypothetical edge).
7. **Bid/ask** — `Bar.high`/`Bar.low` accept whatever prices the caller supplies;
   the reconstruction script should pass bid for long-exit/short-favorable and
   ask for short-stop sides if bid/ask M15 is available, else mid (documented in
   the script). Core geometry is price-source agnostic.

## 4. Implementation status

- `src/forex_bot/research/mfe_mae.py` — `Bar`, `MfeMaeResult`, `compute_mfe_mae`.
  Pure, deterministic, no I/O. Returns an explicit `status`
  (`OK` / `NO_BARS` / `ZERO_RISK` / `BAD_SIDE`).
- `tests/unit/test_mfe_mae.py` — 11 synthetic-candle tests covering: long MFE/MAE,
  short MFE/MAE, stop-before-profit, profit-before-drawdown, same-bar intrabar
  ordering (both assumptions), no-lookahead-past-exit, drop-bars-at/before-entry,
  empty-window, zero-risk, bad-side, and JPY-scale risk units.

## 5. How to run the real reconstruction locally (Phase 5)

When a populated materialized M15 store is reachable:

```bash
export FOREX_BOT_RESEARCH_DATABASE_URL=postgresql://<user>:<pass>@localhost/forex_bot
python scripts/reconstruct_mfe_mae_for_campaign_trades.py \
    --campaign-dir backtests/CAMPAIGN_022_h4_h1_pullback_resolution \
    --campaign-id CAMPAIGN_022
```

It will emit a **compact summary** (`c022_mfe_mae_summary.json` +
`CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md`) — never a bulky per-trade dump. If
the store is unreachable it writes a `BLOCKED_LOCAL_DATA` status and exits
cleanly without fabricating any excursion numbers.

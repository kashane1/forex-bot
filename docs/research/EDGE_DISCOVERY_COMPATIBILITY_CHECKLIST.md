# EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST

**Status:** process doc (binding). A pass/fail checklist a future campaign must
satisfy **before it may claim "edge-discovery compatible"** — i.e. before the
lab (`research/edge_discovery/`) can re-screen the campaign's own artifacts with
all five diagnostics. Diagnostic/governance only — approves nothing, opens no
test lockbox.

> Companion: [`FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`](FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md)
> (the emission list, items 1–12), [`EDGE_DISCOVERY_PROTOCOL.md`](EDGE_DISCOVERY_PROTOCOL.md),
> [`PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md`](PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md).

---

Copy this block per campaign, fill it in, attach the artifacts. A campaign is
"edge-discovery compatible" only when **every** box is `[x]`. Any `[ ]` names a
gap the campaign must close (or explicitly document as out-of-scope with a
reason).

```
Campaign: <CAMPAIGN_0NN — one-line strategy>
Precommitted rule filed before any run? [ ]   (must be yes)

A. LEDGERS PRESENT (items 1–3, 8)
  [ ] Signal ledger     — one row/triggered signal: instrument, signal_time_utc,
                          side, timeframe, feature columns
  [ ] Trade ledger      — canonical schema readable by real_data.load_campaign_trades:
                          instrument, side, units, entry_time, exit_time,
                          entry_price, exit_price, stop_price, pnl, r_multiple,
                          bars_held, spread_paid_pips, exit_reason, fill_timing
  [ ] Filter-stage / signal-funnel ledger — trigger + one boolean pass column per
                          filter + per-signal value proxy (log_return / r_multiple)
  [ ] Candidate registry + matrix result table — one row/variant (metric + label)
                          + per-pair breakdown per candidate

B. METADATA PRESENT (items 4–7, 9–12)
  [ ] Pair / side / session metadata on the ledgers
  [ ] Timeframe column explicit on signal + trade ledgers
  [ ] Hold-duration (bars_held) per trade
  [ ] Spread / cost fields (spread_paid_pips + per-cell spread/ATR diagnostics)
  [ ] Split-window metadata (train / validation / test tag per row; never sample test)
  [ ] Null-benchmark compatibility fields (instrument, side, entry_time_utc,
                          bars_held, derivable session/weekday) + C011 baseline ref
  [ ] Reproducibility manifest (commit hash, data path + dedupe policy, date span,
                          precommitted params, strategy_evidence:false where applicable)
  [ ] Random-seed metadata pinned + logged for every stochastic step

C. LAB DIAGNOSTICS RUN ON THE CAMPAIGN'S OWN ARTIFACTS
  [ ] cost_feasibility — spread/ATR per pair/timeframe/session; flag is COST_FEASIBLE
                          on the cell actually traded
  [ ] windows.compute_forward_returns — forward-return information at the traded horizon
  [ ] matched_null_baseline — strategy beats the *structure-matched* null (≥ ABOVE,
                          ideally BEATS) on the modes matching the thesis structure
  [ ] filter_ablation — every retained filter is FILTER_ADDS_EDGE (not sample-only)
  [ ] matrix_sanity — ROBUST_MATRIX_SIGNAL (NOT LIKELY_SELECTION_NOISE / FRAGILE_*),
                          pair-holdout and time-block-holdout do not sign-flip

D. SIZE / SAFETY
  [ ] Ledgers compact (per-trade/per-signal, not per-bar); no raw candle dumps
  [ ] No .env / credentials / DB files / bulky artifacts committed
  [ ] Timestamps UTC; readable with no broker round-trip
  [ ] No test-lockbox sampling anywhere in the screen

E. DECISION COUPLING
  [ ] Pre-registered kill-conditions stated before runs (e.g. recency, forking-path,
                          conditioning narrowness, selection-noise)
  [ ] Verdict words confined to campaign gate machinery (the lab emits none)
```

## How this was validated

The `research-edge-discovery-front-gate-idea-selection-001` sprint exercised
section C on *its own* in-memory ledgers end-to-end (cost-feasibility →
forward-returns → six matched-null modes → filter-ablation → matrix-sanity +
pair/time-block holdout) and confirmed the section-A/B emissions are exactly what
those diagnostics consume. A future campaign that fills this checklist is
re-screenable without the C025/C026 gap (rolled-up metrics only, no per-signal
ledger) that motivated `FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`.

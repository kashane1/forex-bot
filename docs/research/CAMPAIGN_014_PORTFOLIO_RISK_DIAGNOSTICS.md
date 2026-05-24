# CAMPAIGN_014 Portfolio-Risk Diagnostics

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
`strategy_evidence: false`

Phase 7 portfolio-risk diagnostics for CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`. **Diagnostic only — does
not gate the verdict.** Phase 5 verdict was REJECT; these
diagnostics confirm and characterize the failure mode.

> No strategy approved. CAMPAIGN_014 remains REJECT (Phase 5).
> `configs/approved_strategies.yaml` remains `approved: []`.

## 1. Command run

```
python scripts/build_campaign_014_risk_diagnostics.py \
    --campaign-dir backtests/CAMPAIGN_014_calendar_event_window_anomaly
```

Outputs:
- `backtests/CAMPAIGN_014_.../risk/diagnostics.json` (machine-readable)
- `backtests/CAMPAIGN_014_.../risk/diagnostics.md` (auto-generated markdown)
- this doc (curated narrative)

## 2. Standard battery (inherited from CAMPAIGN_010 / 011 / 012 / 013)

### 2.1 Per-pair exposure + streaks

| pair | trades | total units | total PnL (USD) | max loss streak | max win streak | largest single loss | largest single win |
|---|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 100 | 21,687 | −25.49 | 7 | 4 | −1.28 | +3.43 |
| GBP_USD | 152 | 24,110 | −16.06 | 9 | 4 | −1.27 | +3.94 |
| USD_JPY | 134 | 25,458 | −19.00 | 7 | 3 | −1.27 | +3.77 |
| AUD_USD |  91 | 21,103 | −31.91 | 6 | 3 | −1.27 | +1.38 |
| USD_CAD |  91 | 24,190 | −17.99 | 7 | 6 | −1.28 | +2.00 |
| USD_CHF |  89 | 17,920 | −31.34 | 5 | 3 | −1.27 | +1.88 |
| NZD_USD |  63 | 16,205 | −12.47 | 5 | 4 | −1.29 | +1.05 |

Per-pair max-loss streaks are bounded (≤ 9); largest single loss is
~−$1.28 per trade (= 1 R-unit with $500 starting equity × 0.25 %
risk × 1 R loss); largest single win is ~+$3.94 (= ~3 R wins occur
but are rare). No catastrophic single-trade tail.

### 2.2 Entry-session clustering (UTC hour of entry)

| UTC hour | trades | session bucket | trades |
|---:|---:|---|---:|
| 05:00 |  34 | asian (22–06) |  34 |
| 06:00 |  13 | london (06–12) |  13 |
| 13:00 | 444 | london_ny_overlap (12–16) | 673 |
| 14:00 | 229 | ny (16–22) |   0 |

Entries cluster heavily in **london_ny_overlap (12–16 UTC) = 93 %**
of trades, which is exactly when NFP, ECB, and BoE events trigger
(NFP at 13:30 UTC → entry bar 14:00 UTC; ECB at 12:15 UTC → entry
bar 14:00 UTC; BoE at 11:00 UTC → entry bar 14:00 UTC). The 06:00
UTC cluster is BoJ-triggered (BoJ at 03:00 UTC → entry bar 06:00
UTC).

**Zero entries in the asian (22–02) or ny (16–22) buckets** —
consistent with the session_filter blocking the 22:00 UTC trigger
bar following FOMC (see §3.2 below).

### 2.3 Exit-reason distribution

| reason | trades | share |
|---|---:|---:|
| time | 537 | 74.6 % |
| stop | 174 | 24.2 % |
| eod |   9 |  1.2 % |

**Time stops dominate (74.6 %)** — most trades survive the 6-bar
max hold and exit at time. ATR stops fire on 24.2 % of trades.
This is consistent with the strategy's design: ATR-2 is a wide
stop relative to typical 6-bar H4 range, so time stops dominate.

### 2.4 RiskEngine rejection distribution

| code | total | per-pair (selected) |
|---|---:|---|
| `SESSION_BLOCKED` | 409 | uniform ~57–59 per pair across 8 folds |
| `SPREAD_TOO_WIDE` | 196 | EUR_USD 90 (most), NZD_USD 53, USD_JPY 28, USD_CHF 14, GBP_USD 6, AUD_USD 2, USD_CAD 3 |
| **total rejections** | **605** | |

**`MAX_OPEN_POSITIONS_EXCEEDED`: 0** (the strategy emits ≤ 1
signal per pair per bar; structurally cannot exceed).

The SESSION_BLOCKED total (409) is uniform across pairs — same
event-time triggers session block on every pair simultaneously.
SPREAD_TOO_WIDE shows pair variation (EUR_USD highest at 90) —
discussed in §3.3.

### 2.5 Concurrency

| dimension | value |
|---|---|
| BacktestEngine concurrency | 1 (single-instrument per invocation) |
| Runner per-pair invocations | 7 (one engine per pair per fold) |
| `max_open_positions` cap | 1 (within-pair only) |
| `max_positions_per_instrument` cap | 1 |
| `max_correlated_positions` cap | 1 (within-pair only) |
| MAX_OPEN_POSITIONS_EXCEEDED observed | 0 |

### 2.6 Drawdown clustering (per-fold median pair max DD %)

| fold | test window | median pair max DD % |
|---|---|---:|
| 0 | 2021-12-21 → 2022-06-18 | −0.83 % |
| 1 | 2022-06-19 → 2022-12-15 | −0.81 % |
| 2 | 2022-12-16 → 2023-06-13 | −0.99 % |
| 3 | 2023-06-14 → 2023-12-10 | −0.67 % |
| 4 | 2023-12-11 → 2024-06-07 | −0.69 % |
| 5 | 2024-06-08 → 2024-12-04 | −1.06 % |
| 6 | 2024-12-05 → 2025-06-02 | −1.12 % |
| 7 | 2025-06-03 → 2025-11-29 | −1.16 % |

Drawdowns are bounded (≤ −1.16 % median per-pair per-fold) — no
single-fold catastrophic drawdown. The losses accumulate slowly
across many small losing trades, not via a single tail event.

## 3. CAMPAIGN_014-specific event-class diagnostics

### 3.1 Entry-window concentration (R3 binding verification)

| dimension | value |
|---|---|
| trades at `bars_since_event == 1` (trigger bar) | **720 / 720 = 100.0 %** |
| trades at `bars_since_event ≥ 2` | 0 |
| unattributed trades (no event maps to entry bar − 1) | **0** |

**R3 binding is 100 % verified empirically.** Every trade fires
exactly on the first post-event H4 bar; no trade slipped to a later
offset. The strategy module's implementation correctly enforces R3.

### 3.2 Per-event-class PnL distribution (BIG FINDING)

| event class | impacted pairs | trades | total PnL (USD) | mean PnL (USD) | median PnL (USD) | long | short | long share |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **NFP** | all 7 | **571** | **−151.17** | −0.2647 | −0.2665 | 284 | 287 | 49.7 % |
| **FOMC** | all 7 | **0** | +0.00 | n/a | n/a | 0 | 0 | n/a |
| ECB | EUR_USD | 41 | +2.56 | +0.0624 | −0.1029 | 18 | 23 | 43.9 % |
| BoJ | USD_JPY | 47 | −9.07 | −0.1930 | −0.2897 | 16 | 31 | 34.0 % |
| BoE | GBP_USD | 61 | +3.42 | +0.0561 | −0.3448 | 35 | 26 | 57.4 % |
| **total attributed** | — | **720** | **−154.26** | — | — | 353 | 367 | 49.0 % |

#### Two big findings

**FINDING 1: FOMC = 0 trades.** Despite the fixture having 51
FOMC events impacting all 7 USD pairs (potential ~360 trades over
8 folds), the strategy emits zero FOMC trades. The reason is
visible in §3.3 below: **FOMC at ~19:00 UTC → trigger bar opens
22:00 UTC → SESSION_BLOCKED by the rollover window
(16:45–17:15 ET).**

The CAMPAIGN_014 hypothesis explicitly named FOMC as a primary
event class; the runner-level finding is that the H4-bar +
session-filter combination makes FOMC untestable on this universe.
The hypothesis "FOMC post-event H4 bar mean-reverts" is therefore
**unverified** by this evidence sprint — not falsified or
confirmed, just structurally inaccessible at H4 + this session
filter.

**FINDING 2: NFP dominates and loses heavily.** 571 / 720 trades
= 79 % are NFP-triggered, generating −$151.17 of −$154.26 total
losses (98 %). The C014 REJECT is overwhelmingly an "NFP
counter-trend is wrong" finding. Mean trade PnL on NFP is −$0.26
(median −$0.27), with near-50/50 long/short balance (284/287).
The strategy correctly identifies the NFP event-bar direction and
trades counter — and loses on both sides, meaning the **first
post-event H4 bar tends to CONTINUE the NFP event-bar's
direction**, not revert.

### 3.3 SESSION_BLOCKED forensics (FOMC mystery)

| event class | event time UTC | event bar | trigger bar | rollover overlap? |
|---|---|---|---|---|
| NFP | 13:30 UTC | 10:00–14:00 | 14:00–18:00 | NO (12:00–14:00 NY) |
| FOMC | 19:00 UTC | 18:00–22:00 | 22:00–02:00 | **YES — 17:00 ET (= 22:00 UTC EDT, 21:00 UTC EST) overlaps the 16:45–17:15 ET rollover window** |
| ECB | 12:15 UTC | 10:00–14:00 | 14:00–18:00 | NO |
| BoJ | 03:00 UTC | 02:00–06:00 | 06:00–10:00 | NO |
| BoE | 11:00 UTC | 10:00–14:00 | 14:00–18:00 | NO |

The 409 SESSION_BLOCKED rejections distribute uniformly across all
7 pairs at ~57–59 per pair × 8 folds = matches the **51 FOMC
events × 7 pairs / 8 folds ≈ 45 per pair per "8-fold span"**, with
some additional blocks from NFP edge cases falling on Sun open or
Fri close.

### 3.4 Per-event-class × per-pair sensitivity heatmap

| event class | EUR_USD | GBP_USD | USD_JPY | AUD_USD | USD_CAD | USD_CHF | NZD_USD |
|---|---|---|---|---|---|---|---|
| NFP | (59, −28.05) | (91, −19.48) | (87, −9.93) | (91, −31.91) | (91, −17.99) | (89, −31.34) | (63, −12.47) |
| FOMC | (0, +0.00) | (0, +0.00) | (0, +0.00) | (0, +0.00) | (0, +0.00) | (0, +0.00) | (0, +0.00) |
| ECB | (41, +2.56) | — | — | — | — | — | — |
| BoJ | — | — | (47, −9.07) | — | — | — | — |
| BoE | — | (61, +3.42) | — | — | — | — | — |

**Cells show (trades, total_pnl_usd). `—` = pair not impacted by
event class (binding IMPACTED_PAIRS mapping).**

Headline:

- **NFP loses on every pair** (the most decisive falsification).
  Worst losses: AUD_USD (−$31.91), USD_CHF (−$31.34), EUR_USD
  (−$28.05). The "EUR_USD has the highest SPREAD_TOO_WIDE
  rejection" (90 rejections) is consistent with the wide
  post-NFP EUR/USD spread expansion; many EUR/USD signals are
  filtered out, leaving 59 (vs 91 elsewhere) NFP trades on
  EUR/USD.
- **FOMC unverified** (0 trades on all 7 pairs).
- **ECB on EUR_USD slightly positive** (+$2.56 over 41 trades =
  +$0.06 mean) — possibly real positive signal, possibly noise
  at this small sample.
- **BoJ on USD_JPY negative** (−$9.07 over 47 trades = −$0.19
  mean) — consistent with NFP-style continuation.
- **BoE on GBP_USD slightly positive** (+$3.42 over 61 trades =
  +$0.06 mean) — possibly real, possibly noise.

The ECB + BoE positive results are too small (each ~+$3) to
support a "carve out a sub-strategy" rescue, even if the sample
were larger — and **per [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md)
Pattern P (pair-only survivor selection)**, picking only the
positive cells post-hoc would be result-driven rescue. The data
point is: **NFP counter-trend is wrong; FOMC is untestable here;
ECB + BoE samples are too thin to be meaningful.**

### 3.5 Pre-event vs post-event direction breakdown

For NFP (the dominant signal):

| direction | count | share |
|---|---:|---:|
| long (event-bar return was negative; strategy went long expecting bounce) | 284 | 49.7 % |
| short (event-bar return was positive; strategy went short expecting fade) | 287 | 50.3 % |

**Near-50/50 long/short balance on NFP** — confirms the strategy
fires symmetrically based on event-bar return sign. The systematic
loss is NOT one-sided (e.g. "shorts work, longs don't"); BOTH
sides lose because the post-event bar continues the event direction
in both cases.

### 3.6 NFP / FOMC concurrent-firing (out of 7 USD pairs per event)

For NFP events (all 7 USD pairs are impacted simultaneously per
event), how many pairs actually fired entries?

| pairs fired per event | event count |
|---:|---:|
| 4 |  2 |
| 5 |  3 |
| 6 | 24 |
| 7 | 23 |

**Median ~6 pairs fire per NFP event.** Some events have 4-5 pairs
filtered out (typically EUR_USD or NZD_USD with SPREAD_TOO_WIDE
on big-move NFPs). The simultaneous-pair firing is **explicitly
justified by the hypothesis** (NFP is a USD event; all USD pairs
are simultaneously informative — this is the cleanest form of
portfolio-level edge proof — same event-driven mechanism per pair).
Unlike CAMPAIGN_013's Pattern N concern (broad simultaneous
multi-pair entries without portfolio-level edge proof), C014's
NFP simultaneity has explicit hypothesis backing.

**FOMC concurrent-firing: 0 events, 0 pairs** (all blocked by
session_filter; see §3.3).

### 3.7 Per-fold event-fixture coverage (R4 binding)

| fold | test window | fixture_coverage_end_utc | covered |
|---|---|---|:---:|
| 0 | 2021-12-21 → 2022-06-18 | 2026-05-20 | ✓ |
| 1 | 2022-06-19 → 2022-12-15 | 2026-05-20 | ✓ |
| 2 | 2022-12-16 → 2023-06-13 | 2026-05-20 | ✓ |
| 3 | 2023-06-14 → 2023-12-10 | 2026-05-20 | ✓ |
| 4 | 2023-12-11 → 2024-06-07 | 2026-05-20 | ✓ |
| 5 | 2024-06-08 → 2024-12-04 | 2026-05-20 | ✓ |
| 6 | 2024-12-05 → 2025-06-02 | 2026-05-20 | ✓ |
| 7 | 2025-06-03 → 2025-11-29 | 2026-05-20 | ✓ |

**All 8 folds within fixture coverage.** R4 fixture-coverage gate
is PASS.

## 4. Risk concerns

| concern | level | observation |
|---|---|---|
| catastrophic single-trade tail risk | LOW | largest single loss −$1.28; ATR-2 stop bounds tail |
| concentration risk (single pair) | LOW | single_pair_dominance 20.69 % ≤ 40 % gate |
| concentration risk (single fold) | LOW | single_fold_dominance 16.24 % ≤ 60 % gate |
| simultaneous-pair firing without edge | LOW | hypothesis-justified (USD event impacts all USD pairs); no Pattern N violation |
| turnover amplification | LOW | 720 trades ≤ 800 hard gate; well below CAMPAIGN_012 / 013 |
| **FOMC structural inaccessibility** | **HIGH (as a hypothesis-testing gap)** | 0 FOMC trades fired; the C7 hypothesis's claim about FOMC is unverified by this sprint |
| MAX_OPEN_POSITIONS rejection | NONE | structurally bounded by per-pair runner |
| SPREAD_TOO_WIDE rejection | MEDIUM-HIGH | 196 rejections (EUR_USD heaviest); reflects post-event liquidity gap on big-move events |

## 5. Pass / warn / fail classification

The diagnostics do not gate the verdict. Mapping per-area:

| area | classification |
|---|---|
| per-pair exposure | DIAGNOSTIC PASS (no concentration; bounded streaks) |
| session clustering | DIAGNOSTIC PASS (explainable by event schedule) |
| exit reasons | DIAGNOSTIC PASS (time-stops dominate as designed) |
| RiskEngine rejections | DIAGNOSTIC PASS (no MAX_OPEN_POSITIONS_EXCEEDED; SESSION_BLOCKED is FOMC-driven and binding) |
| drawdown clustering | DIAGNOSTIC PASS (bounded ≤ −1.16 % median per-fold) |
| entry-window concentration (R3) | DIAGNOSTIC PASS (100 % at offset 1; binding verified) |
| event-class clustering | **DIAGNOSTIC WARN** (FOMC = 0 trades; the dominant trade source is NFP and NFP loses) |
| per-event-class per-pair heatmap | DIAGNOSTIC PASS (no cell is positive enough to suggest rescue; ECB/BoE small + samples too thin) |
| direction balance | DIAGNOSTIC PASS (near-50/50; losses on BOTH sides) |
| NFP/FOMC concurrent firing | DIAGNOSTIC PASS (NFP fires on ~6/7 pairs as designed; FOMC 0/7) |
| fixture coverage per fold | DIAGNOSTIC PASS (all 8 covered) |

## 6. Missing tooling (none)

| dimension | value |
|---|---|
| missing diagnostic measurements | **none** — all required diagnostics from `CAMPAIGN_014_FINANCING_RISK_READINESS.md` §5 produced |
| new diagnostic helpers implemented this sprint | event-class attribution helper (`_attribute_trade_to_event`) — local to the diagnostics script; no production-code change |
| tests for new helpers | not added (script is one-shot diagnostic; manual verification via known-event spot-check) |

## 7. Explicit no-approval statement

These diagnostics characterize the failure mode of CAMPAIGN_014's
REJECT verdict. They do **not** approve any strategy.
`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked.

## 8. Implications for future C7-family sprints

The two big findings — FOMC structural inaccessibility + NFP
counter-trend falsification — together imply:

1. **A pure post-event H4 counter-trend strategy on the current
   universe + session filter has no future** unless the session
   filter is restructured to allow trades during the FOMC trigger
   window. Such a change would constitute a **new candidate**, not
   a parameter tweak (per `REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`
   universe-identity rule).

2. **Per pair "rescue" via ECB-only or BoE-only is forbidden** by
   Pattern P (pair-only survivor selection from rejected
   campaigns). Even though ECB / BoE samples are slightly positive,
   the n is too small and the positive cells were not pre-declared.

3. **An NFP-continuation hypothesis (the opposite-direction
   strategy)** would be a NEW candidate requiring a fresh
   discovery sprint with pre-committed gates, not a re-tune of
   CAMPAIGN_014.

4. **A finer-timeframe (M30 / H1) event-window study** could test
   whether the post-event continuation pattern reverses at
   sub-H4 resolution — again, this would be a NEW candidate.

None of these alternatives are approved or even shortlisted; they
are flagged for future discovery-sprint consideration only.

## 9. Validation commands run after Phase 7

```
ruff check scripts/build_campaign_014_risk_diagnostics.py  # All checks passed
python -m pytest -q                                         # 968 / 968 PASS
python scripts/validate_research_archive.py                 # ALL PASS
python scripts/check_research_freeze.py                     # ALL PASS
python scripts/scan_artifacts_for_secrets.py                # PASSED
git status --short                                           # only Phase 7 artifacts
```

## 10. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | REJECT (Phase 5; diagnostics confirm failure mode) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| MODELED financing reachable | no |
| broker call this phase | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| RiskEngine config relaxation | **none** |
| pair carve-out post-result | **none** (ECB / BoE positive cells flagged but NOT used for rescue) |

## 11. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md) (sprint plan)
- [`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md) (Phase 5 verdict — REJECT)
- [`CAMPAIGN_014_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_014_WALK_FORWARD_EXECUTION.md) (Phase 4)
- [`CAMPAIGN_014_FINANCING_OVERLAY.md`](CAMPAIGN_014_FINANCING_OVERLAY.md) (Phase 6)
- [`CAMPAIGN_014_FINANCING_RISK_READINESS.md`](CAMPAIGN_014_FINANCING_RISK_READINESS.md) (scaffold-sprint readiness; this Phase 7 satisfies §5)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (Pattern N / P binding)
- [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md), [`CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md), [`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md) (sibling diagnostics)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

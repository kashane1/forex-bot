# CAMPAIGN_014 Evidence Summary

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
`strategy_evidence: false`

One-page evidence summary for **CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`** (the C7 Calendar-Event
Window Anomaly candidate).

## Headline

> **`REJECT` (direction-of-trade falsification).** 6 of 8 inherited
> aggregate gates fail; materially WORSE than CAMPAIGN_011 null
> baseline on every PnL-direction axis (OUTSIDE the
> indistinguishability band on the WORSE side). Turnover budget
> INTACT (720 trades ≤ 800; 1,240 raw signals ≤ 1,500); fixture-
> coverage gate PASS on all 8 folds. The REJECT is NOT
> turnover-amplification (uniquely among C012 / C013 / C014); it is
> a direction-of-trade failure — the post-event H4 bar tends to
> CONTINUE the event-bar's direction, not REVERT.
>
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / 010 / 011 / 012 / 013 remain REJECT and untouched.
> Paper / demo / live remain blocked.

## Headline numbers

| metric | CAMPAIGN_014 | CAMPAIGN_011 (null floor) | gate |
|---|---:|---:|---|
| fold count | 8 | 8 | ≥ 6 |
| fold pass rate | **0 / 8 = 0 %** | 0 / 8 | = 100 % required |
| total trades | **720** | 1,177 | ≥ 200 (and turnover gate ≤ 800) |
| total raw signals | **1,240** | n/a | ≤ 1,500 |
| aggregate expectancy R | **−0.14774** | −0.0024 | ≥ 0.05 |
| aggregate profit factor | **0.00** | 0.91 | ≥ 1.10 |
| aggregate return % (4 y) | **−30.8516 %** | −0.53 % | meaningfully positive |
| pairs positive | **0 / 7** | 3 / 7 | ≥ 4 / 7 |
| single_fold_dominance % | 16.24 % | 40.1 % | ≤ 60 % |
| single_pair_dominance % | 20.69 % | 36.5 % | ≤ 40 % |
| financing cashflow (stress) USD | **−10.64** | −24.38 | (LOWEST of any real candidate) |
| financing missing-rate events | 0 | 0 | = 0 |
| fixture-coverage gate (all 8 folds) | **PASS** | n/a | required |
| `MAX_OPEN_POSITIONS_EXCEEDED` | **0** | 0 | n/a (per-pair runner) |

6 of 8 aggregate gates FAIL: `fold_pass_rate_eq_100pct`,
`expectancy_r_ge_0p05`, `profit_factor_ge_1p10`,
`pairs_positive_ge_4_of_7` (and the per-fold equivalents on all 8
folds). 4 gates PASS: `fold_count_ge_6`, `trade_count_ge_200`,
`single_fold_dominance_le_60pct`, `single_pair_dominance_le_40pct`.
**Both turnover gates PASS** (`total_trades_le_800`,
`total_raw_signals_le_1500`).

## Null-baseline interpretation

CAMPAIGN_014's results diverge from CAMPAIGN_011 on every binding
axis **in the worse direction**:

| metric | C011 ± band | C014 | inside band? |
|---|---|---:|:---:|
| expectancy R | [−0.0074, +0.0026] | **−0.14774** | NO (0.145 R BELOW band) |
| profit factor | [0.81, 1.01] | **0.00** | NO (0.81 BELOW band) |
| return % (4 y) | [−2.53, +1.47] | **−30.85** | NO (28.3 pp BELOW band) |
| pairs positive | [2, 4] | **0** | NO (2 BELOW band) |

**5 of 6 meaningful-improvement margins REGRESS relative to null.**
Classification: **REJECT (direction-of-trade falsification)** — not
`REJECT_INDISTINGUISHABLE_FROM_NULL` (that would require being
WITHIN the band).

## Per-pair vs CAMPAIGN_011

| pair | CAMPAIGN_011 null | CAMPAIGN_014 | C014 − C011 |
|---|---:|---:|---:|
| EUR_USD | −0.0091 R | −0.20302 R | **−0.194 R worse** |
| GBP_USD | +0.0019 R | −0.08371 R | **−0.086 R worse** |
| USD_JPY | +0.0000 R | −0.00081 R | ≈ tied (random-walk floor) |
| AUD_USD | −0.0207 R | −0.27873 R | **−0.258 R worse** |
| USD_CAD | −0.0162 R | −0.11643 R | **−0.100 R worse** |
| USD_CHF | +0.0033 R | −0.30908 R | **−0.312 R worse** |
| NZD_USD | −0.0737 R | −0.15504 R | **−0.081 R worse** |

Every pair is worse than the CAMPAIGN_011 null (USD_JPY tied at
random-walk floor). All 4 pairs that were ≥ 0 in CAMPAIGN_011
(GBP, JPY, CHF, "near-zero") turned negative in CAMPAIGN_014.

## Per-event-class breakdown (CAMPAIGN_014-specific)

| event class | impacted pairs | trades | total PnL (USD) | mean PnL | long / short | finding |
|---|---|---:|---:|---:|---|---|
| **NFP** | all 7 | **571** | **−151.17** | −0.265 | 284 / 287 | **counter-trend hypothesis FALSIFIED** |
| **FOMC** | all 7 | **0** | +0.00 | n/a | 0 / 0 | **STRUCTURALLY UNTESTABLE** (SESSION_BLOCKED) |
| ECB | EUR_USD | 41 | +2.56 | +0.062 | 18 / 23 | slightly + but n too small |
| BoJ | USD_JPY | 47 | −9.07 | −0.193 | 16 / 31 | NFP-style continuation |
| BoE | GBP_USD | 61 | +3.42 | +0.056 | 35 / 26 | slightly + but n too small |
| **total attributed** | — | **720** | **−154.26** | — | 353 / 367 | — |

**Two findings of independent research value:**

1. **FOMC = 0 trades.** All 51 FOMC events SESSION_BLOCKED. FOMC
   at ~19:00 UTC → event bar 18:00-22:00 UTC → trigger bar 22:00
   UTC = rollover window (16:45-17:15 ET overlaps 22:00 UTC EDT).
   The C7 hypothesis's claim about FOMC is structurally
   untestable on this universe + session filter.
2. **NFP dominates and loses.** 571 / 720 trades (79 %) NFP-
   triggered, generating −$151.17 (98 % of total losses). Near-
   50/50 long/short balance (284 / 287) → losses on BOTH sides →
   first post-event H4 bar CONTINUES the NFP event-bar's
   direction, does not REVERT.

## Comparison across all 5 real candidates + null

| dimension | C010 (session) | **C011 (null)** | C012 (regime) | C013 (cross-pair) | **C014 (calendar event)** |
|---|---:|---:|---:|---:|---:|
| total trades | 1,103 | 1,177 | 3,726 | 7,940 | **720** |
| aggregate expectancy R | −0.0850 | −0.0024 | −0.0521 | −0.0564 | **−0.14774** |
| aggregate profit factor | 0.74 | 0.91 | 0.034 | 0.000 | **0.00** |
| aggregate return % | −22.6 | −0.53 | −43.52 | −113.36 | **−30.85** |
| pairs positive | 1 / 7 | 3 / 7 | 1 / 7 | 1 / 7 | **0 / 7** |
| inherited verdict | REJECT | REJECT (null) | REJECT | REJECT | **REJECT** |
| meaningful improvement over null? | NO | (= null) | NO | NO | **NO** |
| indistinguishable from null? | NO (worse) | (= null) | NO (much worse) | NO (much worse) | **NO (much worse)** |
| turnover amplification (Pattern O / M)? | borderline | n/a | YES (3.2 × null) | YES (6.7 × null) | **NO (0.61 × null)** |
| direction-of-trade failure? | YES | n/a | YES | YES | **YES** |
| catastrophic single-fold/single-pair? | NO | NO | NO | NO | **NO** |

**CAMPAIGN_014 is the LOWEST-turnover real candidate (720 trades),
yet has the MOST-NEGATIVE per-trade expectancy (−0.148 R).** The
design correctly avoided Pattern M / N / O / Q (cost-insensitive
signal); it failed because the hypothesis itself was wrong.

## Financing impact (does not change verdict)

| dimension | value |
|---|---:|
| rate source | conservative_stress (ESTIMATED) |
| cashflow_home_stress_total | **−$10.64** |
| pair-flips under financing | **0** (every pair already negative) |
| MODELED status | REFUSED (4 layers intact) |
| pre-financing verdict | REJECT |
| post-financing verdict | REJECT (unchanged) |

CAMPAIGN_014 has the **LOWEST absolute financing cost** of any
real candidate (−$10.64), consistent with the predicted "$5–15 USD
total drag" from the scaffold sprint's readiness doc.

## Risk diagnostics (do not change verdict)

| dimension | value |
|---|---:|
| `MAX_OPEN_POSITIONS_EXCEEDED` | 0 |
| `SESSION_BLOCKED` | 409 (FOMC-driven) |
| `SPREAD_TOO_WIDE` | 196 (EUR_USD heaviest at 90) |
| time-stop exits | 537 / 720 = 74.6 % |
| ATR-stop exits | 174 / 720 = 24.2 % |
| EOD exits | 9 / 720 = 1.2 % |
| largest single loss | −$1.28 (≈ 1 R bound) |
| largest single win | +$3.94 (≈ 3 R) |
| max loss streak (per-pair) | 9 |
| median per-fold per-pair max DD | ≤ −1.16 % |
| entry-window concentration | **100 % at bars_since_event = 1** (R3 binding verified) |
| NFP concurrent-firing histogram (out of 7 pairs) | 4: 2 events · 5: 3 · 6: 24 · 7: 23 (median 6/7; hypothesis-justified) |
| concentration: single_pair_dominance | 20.69 % ≤ 40 % gate ✓ |
| concentration: single_fold_dominance | 16.24 % ≤ 60 % gate ✓ |

## Verifier status

Capability-locked to CAMPAIGN_002 / `trend_following`. **NOT
REQUIRED for REJECT verdict** (matches CAMPAIGN_010 / 011 / 012 /
013 precedent). Future
`infra-free-local-parity-verifier-calendar-event-window-anomaly-001`
sprint is the natural extension if any future C7-family candidate
ever reaches `RESEARCH_PASS_UNAPPROVED` (which CAMPAIGN_014 did
not). Not scheduled.

## Fixture date-verification audit (Phase 0)

PARTIAL — PROCEED WITH EXPLICIT CAVEAT (per
[`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md)):

- NFP: **100 % verified** procedurally
- FOMC: **100 % verified** against official Fed.gov calendar
- BoJ: 91 % verified for 2025-2026 (1 post-coverage drift)
- ECB: not WebFetch-verifiable
- BoE: not WebFetch-verifiable (403)

For REJECT verdict, the audit caveat is moot (independent
corroboration not required for REJECT).

## Six-evidence-ladder status

| item | name | status |
|---|---|---|
| 1 | data provenance | **COMPLETE** (Phase 1; byte-identical to CAMPAIGN_010/011/012/013) |
| 2 | walk-forward verdict | **COMPLETE — REJECT** (Phase 5) |
| 3 | financing overlay | **COMPLETE** (ESTIMATED + conservative stress; impact −$10.64; verdict unchanged) |
| 4 | risk diagnostics | **COMPLETE** (standard + C7-specific event-class clustering) |
| 5 | independent verifier | **NOT REQUIRED for REJECT** |
| 6 | deliberate human approval | **MOOT for REJECT** |

## Approval state (unchanged after this sprint)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| **CAMPAIGN_014** | **REJECT (this sprint)** |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| MODELED financing reachable | no |
| QuantConnect / LEAN | retired |

## Cross-links

- [`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md) (Phase 5 verdict)
- [`CAMPAIGN_014_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_014_WALK_FORWARD_EXECUTION.md) (Phase 4 execution)
- [`CAMPAIGN_014_WALK_FORWARD_PLAN.md`](CAMPAIGN_014_WALK_FORWARD_PLAN.md) (Phase 2 plan)
- [`CAMPAIGN_014_DATA_PROVENANCE.md`](CAMPAIGN_014_DATA_PROVENANCE.md) (Phase 1 provenance)
- [`CAMPAIGN_014_FINANCING_OVERLAY.md`](CAMPAIGN_014_FINANCING_OVERLAY.md) (Phase 6)
- [`CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md) (Phase 7)
- [`CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md) (Phase 8)
- [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md) (Phase 0 audit)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)

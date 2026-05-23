# CAMPAIGN_010 — Rejection Closeout

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-002`
`strategy_evidence: false`

Formal closeout note for the CAMPAIGN_010 research candidate
(`session_breakout 0.1.0-c010`) after its **REJECT** verdict in
the `research-asian-london-session-breakout-walk-forward-001`
evidence sprint. **This document does not change CAMPAIGN_010's
verdict.** It records what the rejection means for future
discovery work, and codifies which parts of the session-breakout
family are off-limits for immediate retuning.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked. This is the
> design-sprint companion to the evidence-sprint verdict — not a
> new verdict and not a partial vindication.

## 1. Why CAMPAIGN_010 was rejected (cited from prior evidence)

The complete evidence is in
[`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md);
the verbatim metrics are reproduced here only for closeout
purposes (no new evidence is added).

| dimension | value |
|---|---|
| protocol | rolling walk-forward, 540 / 180 / 180 / 180 days, frozen parameters |
| universe | 7-pair OANDA practice H4 (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD) |
| folds executed | 8 |
| total trades | 2,791 |
| `fold_pass_rate` | **0 / 8 = 0 %** (gate 100 %) |
| `aggregate_expectancy_R` | **−0.0408 R** (gate ≥ 0.05) |
| `aggregate_profit_factor` | **0.04** (gate ≥ 1.10) |
| `aggregate_return_pct` | **−36.56 %** over 4 years out-of-sample |
| `pairs_positive` | **1 / 7** (USD_CHF only; gate ≥ 4 / 7) |
| financing overlay impact | **worsens** REJECT — USD_CHF flips +→− under conservative-stress |
| single-pair dominance | 24.1 % (≤ 40 % gate) — PASS |
| single-fold dominance | 30.3 % (≤ 60 % gate) — PASS |
| classification | not BLOCKED, not INCONCLUSIVE — REJECT |
| relevance to approval | candidate cannot enter `configs/approved_strategies.yaml` |

The five failing aggregate gates are decisive. Re-running the
candidate cannot change them; tweaking parameters could *fit* a
new set of gates, which is precisely the curve-fitting pattern
the freeze refuses.

## 2. What "rejected" means here (clarifying language)

- **Rejected, not blocked.** The evidence pipeline ran end-to-end
  in 7.9 s and produced 2,791 clean trades; the strategy failed
  on the merits, not on infrastructure.
- **Rejected, not inconclusive.** The aggregate trade count
  (2,791) and the per-fold trade counts (each ≥ 265) clear the
  pre-committed gates by a wide margin; the negative expectancy
  is directional, not statistical noise.
- **Rejected directionally.** The strategy's hypothesis (London
  open continues through the Asian range break) is falsified by
  out-of-sample data on this universe under frozen parameters.
- **Rejected without verifier corroboration.** The free / local
  verifier is capability-locked to CAMPAIGN_002; it did not run
  for CAMPAIGN_010. This matters only for a hypothetical PASS —
  not for a REJECT.

## 3. Parts of the session-breakout family that are now OFF-LIMITS

This is the explicit "do not parameter-tweak" list for the
session-breakout family. Every item below was frozen by
[`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
§5, evaluated by the evidence sprint, and would be re-tunable
only as a curve-fit to CAMPAIGN_010's losing trades.

| component | the frozen / observed value | why off-limits to retune |
|---|---|---|
| Asian session window (UTC) | `[22, 6)` (wraps midnight) | The session window was frozen; tweaking it to "skip the days that lost" is the canonical filter-set-tuning anti-pattern. |
| London session window (UTC) | `[6, 12)` | Same. |
| Asian-range minimum (`min_asian_range_atr_fraction`) | `0.30` | Tweaking the floor to exclude the low-range days that lost would be result-driven filter selection. |
| ATR lookback / stop multiple | `14` / `2.0` | The stop is not a hidden variable; raising it to escape stop-pierces would be curve-fitting. |
| Max bars in trade | `6` (≈ 1 trading day) | The strategy was time-stop dominated (75.5 %). Extending the holding window to "let winners run" is the textbook "let losers run too" anti-pattern. |
| Trailing stop | `None` in v1 | Adding a trailing stop in response to CAMPAIGN_010's results is rule-driven by losing trades, which §12 of the protocol forbids. |
| Pair selection | All 7 pairs in the universe | Dropping the losing pairs (e.g. AUD_USD, USD_CAD) to leave only USD_CHF would be implicit per-pair tuning. The aggregate `pairs_positive` gate (≥ 4 / 7) specifically blocks that. |
| Long-only / short-only filters | None | Adding a directional filter to skip the side that lost more (shorts contributed −$121, longs −$61) is identical filter-set-tuning. |
| Spread / ATR filter | `max_spread_to_atr_pct = 8 %`, per-pair max-spread pips | Loosening the spread cap to trade more low-quality bars would worsen the result; tightening it to skip bars that happened to lose is filter-tuning. |
| `risk.risk_per_trade_pct` / `max_positions_per_instrument` / `max_open_positions` | `0.25 %` / `1` / `1` | Risk sizing is not a hidden edge variable. Increasing risk to "make the wins bigger" multiplies losses too. |

## 4. Legitimate future research vs illegitimate "same idea, new knobs"

| pattern | classification |
|---|---|
| "Try `min_asian_range_atr_fraction = 0.50` because 0.30 lost." | **Illegitimate** — direct knob-tweak of a rejected parameter. Result-driven. |
| "Try `asian_session_hours_utc = (20, 4)` because (22, 6) lost." | **Illegitimate** — same family, different window. The strategy's edge hypothesis is unchanged. |
| "Add a per-pair `min_atr_pips` floor to skip NZD_USD." | **Illegitimate** — implicit per-pair tuning. |
| "Add a daily-volatility regime gate (only trade when daily ATR > 60-day median) on top of session_breakout." | **Borderline** — the new gate is a meaningful structural addition, but it inherits the rejected family. Would still need a **new candidate id**, a new pre-commit, and a fresh distinctness scoring; would NOT inherit any CAMPAIGN_010 results as motivation for the gate value. |
| "Build a fundamentally different family that happens to use session-of-day as one input." | **Potentially legitimate** if and only if the family scores ≥ 3 of 6 on the distinctness rubric against **CAMPAIGN_010**, not just against the older rejected families. The fact that CAMPAIGN_010 used session-of-day raises the distinctness bar here. |
| "Random-entry diagnostic anchor on the same H4 universe." | **Legitimate** — distinct family (null model), zero parameters that could be tuned, and explicitly authorized by the protocol §4. |
| "Carry-aware long-only overlay (C2 from prior shortlist)." | **Legitimate but blocked on MODELED financing.** Still C2; this CAMPAIGN_010 rejection does not affect its blocker. |
| "Daily-ATR percentile regime switcher (C3)." | **Borderline-legitimate** — its hypothesis is "trend persistence depends on prior-day volatility regime"; the entry rule is "prior-H4 high/low close" which is not the same as Donchian-20 (CAMPAIGN_002) or the session-breakout entry (CAMPAIGN_010). Distinctness vs CAMPAIGN_010 must be specifically scored. |
| "Volatility-expansion non-directional straddle (C4)." | **Legitimate but requires engine work** (paired-entry support). The CAMPAIGN_010 rejection does not change this. |

## 5. Cooldown rule for the session-breakout family

**Cooldown rule (binding for this discovery sprint and any
follow-up scaffold sprint authorized here):** No
session_breakout variant — under any name, version, or
parameter set — should be considered as a "next preferred
candidate" unless a future human authorizer **explicitly**
authorizes a new hypothesis that is materially different in
structure (not just in knobs).

Specifically, a future session-breakout-shaped proposal is
disqualified at the shortlist stage if:

- It re-uses any of CAMPAIGN_010's frozen parameters as
  motivation for its own parameter values (i.e. "we set X to Y
  because CAMPAIGN_010 used X = Z and lost"), or
- Its primary entry signal still resolves to "close of bar `t`
  vs high/low of session-window-defined prior bar `t−1`", or
- It claims distinctness from CAMPAIGN_010 only on the basis of
  a different session window / threshold / stop multiple, or
- It is motivated by a per-pair / per-fold pattern from
  CAMPAIGN_010's committed trade artifacts (`backtests/CAMPAIGN_010_session_breakout/folds/...`),
  or
- It is motivated by CAMPAIGN_010's fold-6 marginal positive
  result (`+$1.73 net of financing`, `pairs_positive 3 / 7`)
  as "the rule almost works".

This cooldown rule does not require committee approval — it is a
single binary check on any future shortlist proposal.

## 6. How rejected evidence should be used

| usage | classification |
|---|---|
| Citing CAMPAIGN_010 as a **rejected family** in a new candidate's distinctness scoring | **Legitimate.** Every new candidate must score ≥ 3 of 6 distinctness vs the now-5 rejected families (CAMPAIGN_002, CAMPAIGN_004, CAMPAIGN_007, CAMPAIGN_008/009, **CAMPAIGN_010**). |
| Citing CAMPAIGN_010 as proof "trend / breakout entries lose on H4 majors after costs" | **Legitimate.** Consistent with CAMPAIGN_002, CAMPAIGN_004, CAMPAIGN_007, and the CAMPAIGN_005 random benchmark. |
| Using CAMPAIGN_010's per-pair expectancies to design a per-pair filter for a new candidate | **Illegitimate.** This is the "filter-set tuning to a prior campaign's losing trades" §12 disqualifier. |
| Using CAMPAIGN_010's per-fold dominance numbers to size a new candidate's fold count | **Illegitimate.** Fold structure is set by the harness + the design's window/step values, not by a rejected campaign's results. |
| Using CAMPAIGN_010's fold-6 marginal positive expectancy to motivate a new "session-aware" regime switch | **Illegitimate.** Result-driven filter selection; falls under §12. |
| Using CAMPAIGN_010's risk-engine rejection profile (414 SPREAD_TOO_WIDE, 770 SPREAD_TO_ATR) as cost-of-trade context | **Legitimate** as general infrastructure context. **Illegitimate** if it motivates a candidate-specific spread filter tweak. |

## 7. No campaign verdict changes

This document changes no verdict:

- CAMPAIGN_010 stays **REJECT**.
- The strategy-status registry row for `session_breakout
  0.1.0-c010` stays `rejected`.
- `configs/approved_strategies.yaml` stays `approved: []`.
- The artifact tree under
  `backtests/CAMPAIGN_010_session_breakout/` is untouched.
- The CAMPAIGN_010 docs
  ([`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md),
  [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md),
  [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md),
  [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md),
  [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md))
  are untouched.

## 8. Cross-links

- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_010_EVIDENCE_SUMMARY.md`](CAMPAIGN_010_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §12 (disqualifying overfitting patterns)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
  (this sprint's general anti-overfit guardrails across all
  rejected families)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

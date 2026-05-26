# CAMPAIGN_011 — Null-Baseline Interpretation

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-003`
`strategy_evidence: false`

> **NUMERIC FLOOR SUPERSEDED (2026-05-26).** §1 verbatim metrics are
> **pre-fix / LIKELY_CONTAMINATED**. For null-band centres use the
> deduped canonical rollup:
> [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
> and [`CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md`](CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md).
> Comparison **protocol** in §2–§9 below remains binding.

Phase 1 formalization of how CAMPAIGN_011 (`random_entry_anchor
0.1.0-c011` — the C5 null-model anchor) should be used as a
falsifiability floor when judging future real candidates. **This
document does not approve any strategy.** It binds future
discovery / scaffold / evidence sprints to a concrete
null-baseline comparison protocol.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. CAMPAIGN_011 remains REJECT (null-model
> anchor). `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_011 is a null model — it is NOT a
> trading candidate. It is a measurement instrument.**

## 1. CAMPAIGN_011 result summary (verbatim — **SUPERSEDED NUMBERS**)

> **Canonical deduped floor (2026-05-26):** 1,180 trades,
> aggregate expectancy **−0.0029 R**, return **−0.68 %**, PF **0.89**,
> 3/7 pairs positive, 0/8 fold pass. See
> [`CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE.md).

Cited from
[`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
**(pre-fix; superseded for numeric use)**
and [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md):

| dimension | value | interpretation |
|---|---|---|
| `WalkForwardResults.overall_verdict` | **REJECT** | expected null-model outcome |
| `fold_count` | 8 | matches CAMPAIGN_010's plan exactly |
| `fold_pass_rate` | **0 / 8** | gate requires 100 %; no fold passes |
| `total_trades` | 1,177 | rich sample |
| `aggregate_expectancy_r` | **−0.0024 R** | ≈ 0; null-model signature within 0.0024 |
| `aggregate_profit_factor` | **0.91** | ≈ 1; within 0.09 |
| `aggregate_return_pct` | **−0.53 %** over 4 years | essentially zero |
| `pairs_positive` | **3 / 7** | GBP_USD, USD_JPY ≈ 0, USD_CHF; close to uniform-noise expectation of 3.5 |
| `single_pair_dominance_pct` | 36.5 % (≤ 40 % gate) | structural PASS |
| `single_fold_dominance_pct` | 40.1 % (≤ 60 % gate) | structural PASS |
| USD_JPY expectancy | **+0.0000** to 4 dp | textbook random-walk signature |
| long-share | 51.8 % (610 / 1,177) | within 50 ± binomial 3σ |
| financing | `ESTIMATED` + conservative stress; MODELED refused | `cashflow_home_stress_total = −$24.38`; per-trade cost −$0.023/event |
| financing impact on verdict | strictly worsens; USD_JPY flips +→− | `pairs_positive → 2/7` post-financing |
| risk diagnostics | per-pair distribution near-uniform (ratio max/min = 1.65 vs CAMPAIGN_010's 12.0); session diffuse across all 4 UTC buckets; 79 % time-stop exit; 8/8 pipeline sanity checks pass | all consistent with random null model |
| seed | `master_seed = 20260523` (frozen; no optimization) | reproducible exactly |

## 2. The null-baseline comparison floor (binding)

Every future real candidate's evidence sprint must report its
metrics **alongside** CAMPAIGN_011's verbatim. A passing
candidate must beat CAMPAIGN_011 by a *meaningful margin* on the
PnL-direction dimensions; merely beating CAMPAIGN_011 within
noise is not evidence of an edge.

### 2.1 The floor (CAMPAIGN_011 numbers; do NOT relax)

| metric | CAMPAIGN_011 floor | future real candidate must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 R | by **≥ +0.05 R** → reach ≥ 0.05 R (CAMPAIGN_010-inherited aggregate gate) |
| aggregate profit factor | 0.91 | by **≥ +0.19** → reach ≥ 1.10 (aggregate gate) |
| aggregate return % over ~4 years | −0.53 % | meaningfully positive (e.g. ≥ +5 % aggregate, sign of an edge after costs) |
| `pairs_positive` | 3 / 7 | **≥ 4 / 7** (CAMPAIGN_010-inherited aggregate gate) |
| `fold_pass_rate` | 0 / 8 | **100 %** (strict-pass; CAMPAIGN_010-inherited aggregate gate) |
| worst per-pair expectancy R | −0.0737 R (NZD_USD) | none worse than CAMPAIGN_011's worst by a wide margin (informational only — pair-level pass is the per-fold gate's job) |
| post-financing expectancy R | ≈ −0.018 R | post-financing positive expectancy with conservative-stress source |

### 2.2 Beating CAMPAIGN_011 is necessary but not sufficient

Even a candidate that beats every CAMPAIGN_011 number by a
meaningful margin must still:

1. **Pass every per-fold gate verbatim** from the candidate's
   pre-commit checklist (which inherits CAMPAIGN_010's §10
   gate vector — `expectancy_R ≥ 0.05`, `profit_factor ≥ 1.10`,
   `pairs_positive ≥ 4 / 7`, `trade_count ≥ 30`,
   `single_pair_dominance ≤ 60 %` on every test fold).
2. **Pass every aggregate gate** (the eight listed in
   [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
   §11; inherited from CAMPAIGN_010 §10).
3. **Pass the financing overlay** under
   `default_stress_rate_source()` (ESTIMATED + conservative
   stress; MODELED still refused at four layers).
4. **Pass the portfolio-risk diagnostics** (concurrency,
   per-pair exposure, drawdown clustering — none of which can
   indicate engine misuse).
5. **Survive independent corroboration** if the verifier-extension
   sprint runs for that family (item 5 of the six-evidence
   ladder; required for paper-promotion consideration).
6. **Earn a deliberate human-approval action** per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
   (item 6 of the six-evidence ladder; the only path to
   `configs/approved_strategies.yaml`).

## 3. "Meaningful improvement over null" — quantitative definition

A candidate is **meaningfully above null** on a metric if and
only if its observed value beats CAMPAIGN_011's observed value
by **at least** the corresponding margin below. These margins
are *additional* to the inherited pass gates from CAMPAIGN_010 §10.

| metric | "meaningful improvement" margin over CAMPAIGN_011 |
|---|---|
| aggregate expectancy R | ≥ +0.0529 R (i.e. reach the 0.05 R gate, beating deduped −0.0029 by 0.0529; pre-fix centre was −0.0024) |
| aggregate profit factor | ≥ +0.19 (reach the 1.10 gate, beating 0.91 by 0.19) |
| aggregate return % (4 years) | ≥ +5.5 percentage points (reach ≥ +5 %, beating −0.53 % by ~5.5 pp) |
| `pairs_positive` | ≥ +1 pair (reach 4/7, beating 3/7 by 1) |
| `fold_pass_rate` | 100 % vs 0 % — full margin |
| per-fold consistency | no single fold contributes ≥ 60 % of aggregate (CAMPAIGN_011 was 40 %; CAMPAIGN_010 was 30 %; the gate is ≤ 60 %) |

If a candidate's headline numbers cluster within
**±0.005 R expectancy / ±0.10 PF / ±2 percentage points return /
±1 pair** of CAMPAIGN_011's, the candidate is **indistinguishable
from random within statistical noise** — it has demonstrated no
edge, even if a single gate happens to pass by luck. The future
evidence-sprint's verdict doc must explicitly call this out.

## 4. Robust pair-distribution requirement

CAMPAIGN_011 produced 3/7 pairs positive with no single pair
dominating (single_pair_dominance 36.5 % < 40 % gate). A real
candidate cannot satisfy `pairs_positive ≥ 4/7` by having one
pair carry the whole result; the inherited
`single_pair_dominance ≤ 40 %` aggregate gate already prevents
that, but the comparison framing matters:

- "4 / 7 pairs positive, single_pair_dominance 38 %" → meets
  both gates; **legitimate edge claim**.
- "4 / 7 pairs positive, single_pair_dominance 55 %" → fails
  the dominance gate; **REJECT** even if pairs_positive passes.
- "3 / 7 pairs positive, aggregate expectancy +0.07 R driven
  by USD_JPY contribution alone" → fails `pairs_positive`;
  **REJECT** even if expectancy beats the floor.

## 5. Single-fold robustness requirement

CAMPAIGN_011's single_fold_dominance was 40.1 % (close to the
60 % gate's allowance). A real candidate's `fold_pass_rate =
100 %` claim must be backed by **per-fold consistency**, not
one breakout fold:

- "8 / 8 folds pass; per-fold expectancy R range [+0.06, +0.18]"
  → **legitimate**.
- "8 / 8 folds pass; per-fold expectancy R range [+0.01,
  +0.45]" with one massive fold → **suspicious**; the candidate
  may be passing the strict gate but the variance is concerning;
  the evidence-sprint verdict doc must flag this.
- "7 / 8 folds pass" → **automatic REJECT** under the strict-pass
  100 % rule.

## 6. Survival of financing stress

CAMPAIGN_011's financing overlay strictly worsened the result;
USD_JPY (marginally +ve pre-financing) flipped to −ve under
conservative stress. A real candidate's report must show:

- Pre-financing `aggregate_expectancy_R` ≥ 0.05 R (gate).
- Post-financing `aggregate_expectancy_R` **still ≥ 0.05 R**
  (the same gate evaluated after the overlay — the inherited
  CAMPAIGN_010 §10 gate is `expectancy_R_net_of_stress_financing`).
- `pairs_positive` does not collapse below 4/7 under stress
  (if a real candidate's positive expectancy comes from one
  pair that the conservative-stress source then flips, that is
  a CAMPAIGN_011-style failure, not an edge).

## 7. What NOT to do (binding anti-overfit rules)

Per
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
+ this null-baseline interpretation:

| pattern | classification |
|---|---|
| **Tune the random seed.** "Try `master_seed = N+1` to find a luckier random." | **Disqualified.** CAMPAIGN_011's seed is frozen; sweeps are forbidden. Any seed change constitutes a NEW candidate. |
| **Use CAMPAIGN_011 as a trading candidate.** Add `random_entry_anchor` to `configs/approved_strategies.yaml`. | **Structurally impossible.** Null model by design; no approval path exists. |
| **Lower future gates so real candidates look better against the floor.** "If a candidate's expectancy is +0.03 R, treat it as a pass because it beats −0.0024." | **Disqualified.** The CAMPAIGN_010-inherited gate is ≥ 0.05 R; that is the binding number. Beating CAMPAIGN_011 by 0.03 R is necessary but not sufficient. |
| **Treat merely beating random as approval.** "Candidate beat CAMPAIGN_011 → promote." | **Disqualified.** Beating CAMPAIGN_011 is item 0 of an unwritten ladder; the six-evidence ladder still applies. |
| **Pick a candidate because it would have beat CAMPAIGN_011 on certain folds.** | **Disqualified.** Same as pattern G (result-driven family selection) from §12 of the protocol. |
| **Cite CAMPAIGN_011's per-pair / per-fold sub-metrics to justify a per-pair / per-fold filter in a new candidate.** | **Disqualified.** Same as pattern B (filter-set tuning to losing trades) from §12 — applied here to null-model output instead of CAMPAIGN_002 trades. |
| **Re-run CAMPAIGN_011 with a "smarter" entry_probability to manufacture a different baseline.** | **Disqualified.** The entry probability is frozen at 0.05 per the pre-commit; changing it would constitute a new candidate, not a baseline update. |

## 8. Use of CAMPAIGN_011 in future evidence-sprint reports

Every future evidence sprint's `<CAMPAIGN_NN>_WALK_FORWARD_RESULT.md`
must include a **"Null-baseline comparison"** section reporting:

- Side-by-side table: CAMPAIGN_011's eight aggregate metrics vs
  the candidate's eight aggregate metrics.
- Side-by-side per-pair expectancy R table.
- A binary "meaningful improvement over null?" verdict for each
  of the six metrics in §3 above.
- An explicit statement of whether the candidate is
  *statistically indistinguishable from random* under the
  ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair criteria in §3.

If a candidate is **indistinguishable from random** under these
criteria, the verdict doc must classify it as
**REJECT (indistinguishable from null)** — separately from
plain REJECT (negative expectancy directionally). This is a
diagnostic distinction; both are REJECT verdicts as far as the
registry is concerned.

## 9. Use of CAMPAIGN_011 in future scaffold-sprint pre-commits

Every future scaffold sprint's `<CAMPAIGN_NN>_PRECOMMIT_CHECKLIST.md`
must include a **"Null-baseline reference"** section that:

- Cites CAMPAIGN_011's eight aggregate metrics verbatim
  (from this doc's §1 table).
- Explicitly inherits the six "meaningful improvement margins"
  from §3 above.
- Restates the binding rule that beating CAMPAIGN_011 is
  necessary but not sufficient.
- Restates that CAMPAIGN_011 is a measurement instrument, not
  a trading candidate.

## 10. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **CAMPAIGN_011 remains REJECT (null-model anchor)** (untouched).
- **Paper / demo / live remain blocked.**
- No strategy code edited this phase.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 11. Cross-links

- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_011_EVIDENCE_SUMMARY.md`](CAMPAIGN_011_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md)
- [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  §10 (the gate vector both CAMPAIGN_010 and CAMPAIGN_011 inherit)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)

# CAMPAIGN_025 — interpretation & prior-campaign comparison

The C025 train matrix is a **REJECT**. This memo interprets *why* and compares the
result to prior failed approaches. Results are poor; this memo says so plainly.

---

## Did C025 change the evidence picture?

**No.** Moving the breakout trigger to M5 with HTF confluence did not produce a
positive, robust edge across any of 16 coherent designs. The dominant, decisive
finding is a **cost-structure result**, not a signal-quality result.

## Comparison to prior baselines

| reference | what it was | C025 vs it |
|---|---|---|
| **C011 deduped null** (−0.0029R) | random-entry anchored null | every C025 candidate sits **below** the null (best −0.077R); the strategy is worse than random-entry-with-the-same-exits after cost |
| **C020** (H4/M15 MTF confluence pullback) | REJECT, train gate fail | C025 shares the MTF-confluence + `next_bar_open` discipline but executes on M5; same end state (REJECT), now with a clear cost mechanism |
| **C021** (M15 LTF MTF confluence) | REJECT (train −0.017R) | C021 was mildly negative on M15; C025 is **much more** negative on M5 (−0.08 to −0.18R), i.e. dropping to M5 made it worse, consistent with higher relative spread cost |
| **C024** (abandoned pullback-family "NOT_READY") | never built | unrelated; C025 reused only the *number's successor* — see numbering convention |
| broad H4 campaigns (C002/C012/C013/C015–017) | REJECT / null | C025 confirms the broad-seven-pair "no universal edge" lesson at a finer timeframe |

## Mechanism: what actually happened

- **Did M5 improve signal quality?** No. The funnel is healthy (964k bars → 21.6k
  gated signals → 5.7k entries) but gross edge is thin and **net** edge is negative.
- **Did the Donchian trigger help or worsen turnover?** It produced *more*, *smaller*
  trades. On M5 that is harmful: faster candidates (scalps, Donchian-12) are the
  **worst** (−0.17 to −0.18R) — textbook turnover amplification.
- **Did HTF confluence filter enough noise?** It filtered a lot (H4 80% pass, H1 72%,
  breakout 12%) but not enough to overcome cost; gating quality ≠ cost survival.
- **Is spread/ATR the structural problem?** **Yes — this is the headline.** Mean
  spread/ATR ≈ 0.45–0.50: the bid/ask spread is ~half the per-bar M5 ATR, so every
  round trip pays ~0.4–1.0 pip into a move whose natural scale is ~1.8 pips. M5 is
  structurally cost-hostile for this trigger.
- **Did profit targets help?** No — fixed 2R/3R capped winners while stops and cost
  persisted; target candidates were no better than time-only.
- **Did trailing stops help?** Marginally less-bad (008/009 trend runners are the
  least-negative) by letting a few winners run and amortizing cost over longer
  holds, but still firmly negative.
- **Did channel exits help?** No — they exit late (3602 channel exits for 010) and
  stayed negative.
- **Did the matrix show robustness or fragility?** It showed **robust badness**: all
  16 negative, monotone with turnover. There is no fragile-but-promising corner —
  the family is uniformly unprofitable after cost.
- **Any pair stand out?** Only USD_JPY is weakly non-negative on a few candidates
  (+0.02 to +0.04R), but it fails 2× cost stress. Not materially strong.
- **Longs vs shorts?** Symmetric and both negative (~−0.12R each on baseline).
- **Does time stop / stop / target dominate exits?** Stops + time stops dominate;
  targets/channel exits do not change the verdict.
- **Is this just another turnover-amplification failure?** **Yes**, with an explicit,
  measured cost mechanism (spread/ATR), which is the most useful thing this sprint
  produced.

## What evidence would justify each next step

- **Immediate rejection (current):** all candidates negative, below null, cost
  mechanism understood. → adopt.
- **Single-pair follow-up:** would require a pair that is **materially** positive
  **and** cost-robust (survives 2× stress) on train; USD_JPY does not qualify. So
  **not** justified now.
- **Backtrader parity:** only worth building if something passed train/validation.
  Nothing did. → **defer/reject parity** (see readiness doc).
- **Test lockbox:** absolutely not — train gate failed; lockbox stays closed.

## Recommendation (no approval, no paper/demo/live)

Reject the C025 M5-Donchian-breakout family on the train-matrix evidence. The
reusable lesson is quantitative: **M5 execution for spread-paying majors is
defeated by a spread/ATR ratio near 0.5**; any future M5 idea must either target a
much larger per-trade move (higher ATR multiple / longer holds) or a materially
lower spread regime, and must clear a cost-stress gate *before* signal design.

# C022 / C023 / USD_JPY Microstructure — Full Thread Closeout

**Date:** 2026-05-28 · **Type:** research closeout. Approves nothing, changes no verdict,
tunes nothing, creates no campaign, claims no edge.

> This memo closes the **entire** C022/C023 pullback-resolution → USD_JPY
> microstructure-confirmation → USD_JPY post-entry trade-management thread. It changes
> no verdict (C022 stays REJECT, C023 stays scaffold-only), creates no CAMPAIGN_024,
> executes no C023, and approves nothing. It records the final decision: **no further
> mining of this family**.

## 1. C022 / C023 pullback-resolution family

- **CAMPAIGN_022 REJECT** — realized expectancy −0.1402R; cost-free baseline still −0.0732R.
- **Stop geometry did not rescue it** — all ATR-multiple stops (1.5×–3.0×) and
  time-invalidation variants stayed in a tight negative band; time-exit winners rarely
  approach the stop (4.7% touch −0.9R); 45.9% of stop-outs never reach +0.25R.
- **Winner/loser structural features did not separate** — H4 regime, H1 pullback, and
  M15 reclaim features all at AUC ≈ 0.50; strongest stable signal-quality effect 0.044,
  below the 0.05 floor.
- **C023 ADX22 not executed and not supported** — H4 ADX does not separate winners from
  losers (AUC 0.515/0.501; flat quintile win-rates).
- **Family RETIRED** — `RETIRED_UNLESS_NEW_EXTERNAL_THESIS`. Reopening requires all of:
  a new external market-structure thesis, a materially different trigger, independent
  out-of-sample evidence, and not merely threshold changes.

## 2. USD_JPY microstructure entry diagnostic

- **306 USD_JPY C022 base trades** (train 133, validation 173; near-flat mean R −0.0005).
- **No live M15 detector had material/stable separation** — best stable live effect
  |AUC−0.5| = 0.016, below the 0.05 floor; the old EMA20-reclaim baseline is itself
  inert/unstable (AUC 0.539/0.486); `liquidity_sweep` was direction-unstable.
- **C024 NOT_READY** — no live entry primitive separates winners or beats the baseline.
- **Entry lane CLOSED** as an entry-alpha path. The only above-floor separation was
  **post-entry** (retest-hold AUC 0.611/0.552; trap) — not usable to gate an entry.

## 3. USD_JPY post-entry trade-management diagnostic

- **Post-entry signals described outcomes but did not produce useful management.**
  EXIT-type events (early_reclaim_failure, early_adverse_expansion, no_continuation,
  trap) stably flag higher hard-stop / lower win rates among still-open trades — but
  also flag a meaningful minority (~20–33%) of eventual winners.
- **All early-exit counterfactuals reduced expectancy** — five predeclared next-bar-open
  exit rules each lost −0.065 to −0.134R on **both** splits. Flagged trades often recover
  before the stop, so early-exiting locks in avoidable losses and cuts winners — even
  under optimistic, cost-free mid marks.
- **Trade-management lane CLOSED** — `NOT_READY`. The separation is largely
  tautological / already-priced; the strongest separators are hindsight-only.

## 4. Final decision

- **No more C022/C023/USD_JPY microstructure mining.** Both the entry layer and the
  post-entry management layer are closed; acting on the post-entry signals is
  demonstrably net-negative.
- **No C024 from this family.** C024 remains `NOT_READY` and uncreated.
- **No C023 execution.** Remains scaffold-only / deferred.
- **No strategy approval.** `configs/approved_strategies.yaml` remains `approved: []`;
  paper/demo/live remain blocked.

## 5. What was learned

- **Generic confluence / reclaim signals are not predictive enough.** The H4→H1→M15
  pullback-reclaim thesis carries no winner/loser information at the univariate level,
  and stronger M15 confirmation primitives (impulse, swing-break, sweep+displacement,
  range-expansion) did not recover it on USD_JPY.
- **Stop placement was not the primary bottleneck.** Stop/time/ADX variants and a
  cost-free baseline all stay negative — the failure is entry-edge, not mechanics.
- **Post-entry descriptive signals can be misleading.** Events that *separate* winners
  from losers after the fact (retest-hold/trap) do **not** translate into a profitable
  management rule — conditioning and acting on them removes recovery optionality and
  cuts winners, reducing expectancy.
- **Single-pair USD_JPY focus improved interpretability but did not reveal edge.**
  Narrowing removed confounds and sped iteration, and made the null result cleaner —
  but USD_JPY (near-flat, "less bad") had no hidden edge in this family.
- **Future research needs a genuinely new source of edge, not parameter changes.** More
  indicator combinations, thresholds, stop models, or confirmation overlays on the same
  entry are not warranted. The next lane must change *what is detected* or *where the
  edge comes from* (see the roadmap doc).

## 6. Hard rules upheld

No CAMPAIGN_024 created; no C023 execution; no C022 retune; no verdict changed; no
historical metric rewritten; no strategy approved (`approved: []`); no paper/demo/live;
no broker/executor/order/live changes; no OANDA calls. USD_JPY is **not** presented as
proven edge, and no post-entry diagnostic is a tradable rule.

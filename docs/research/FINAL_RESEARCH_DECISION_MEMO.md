# Final Research Decision Memo

**Date:** 2026-05-22
**Branch:** `research-freeze-no-go`
**Scope:** forex-bot strategy research, CAMPAIGN_001 → CAMPAIGN_009 and
Research Marathon 001.

> ## Current status: NO APPROVED TRADING STRATEGY.
>
> No strategy is approved for paper, demo, or live trading. The repo is
> frozen as a research / backtesting platform. Every order-capable and
> signal-emitting loop is blocked by an empty approved-strategy registry.

---

## 1. Executive summary

Across nine backtest campaigns and one structured four-campaign research
marathon, the project tested **five distinct strategy families** on real
OANDA practice data (six major FX pairs, H4, 2020–2026):

- trend-following (EMA + Donchian breakout),
- ADX-filtered trend-following,
- volatility breakout (ATR-compression),
- pullback-continuation,
- regime-filtered range mean-reversion (two exit variants).

**Not one earned even PAPER-TRADE-ONLY status under its own
pre-committed gates.** Four families produced negative expectancy on
real data. The fifth — regime-filtered mean reversion — showed a real
but unconfirmed validation-era signal, failed its train-split gate
(CAMPAIGN_008), and the focused follow-up built to rescue it
(CAMPAIGN_009) failed the same gate by a wider margin, falsifying the
rescue hypothesis.

The disciplined conclusion is **NO-GO**. This memo freezes the research.
A repo-level guard (an empty `configs/approved_strategies.yaml`) now
refuses to start any paper, demo, or live loop. Backtesting and research
remain fully available.

**Current status: NO APPROVED TRADING STRATEGY.**

## 2. Campaigns and verdicts

| campaign | hypothesis / family | data | verdict |
|---|---|---|---|
| CAMPAIGN_001 | trend_following baseline (harness validation) | **synthetic** | Not evidence — synthetic candles; superseded by 002 |
| CAMPAIGN_002 | trend_following baseline | real OANDA H4/H1 | **REJECT** — −0.085 R, PF 0.75, −1.02% |
| CAMPAIGN_003 | trend_following + ADX-14 > 25 gate | real OANDA H4 | **REJECT** — −0.071 R, PF 0.77, −0.63% |
| CAMPAIGN_004 | volatility_breakout (ATR compression) | real OANDA H4 | **REJECT** — −0.163 R, PF 0.63, −1.40% |
| CAMPAIGN_005 | benchmarks & diagnostics | real OANDA H4 | Diagnostic — random entry −0.095 R; efficiency ratio 0.24 |
| CAMPAIGN_006 | D1 daily trend | real OANDA D1 | **REJECT** — no valid result (D1 infrastructure incompatibility) |
| CAMPAIGN_007 | H4 pullback-continuation | real OANDA H4 | **REJECT** — screening fail (train −0.164 R, validation −0.166 R) |
| CAMPAIGN_008 | H4 range mean-reversion | real OANDA H4 | **REJECT** — screening fail by one gate (train −0.017 R; validation +0.172 R) |
| CAMPAIGN_009 | mean-reversion + midline-target exit | real OANDA H4 | **REJECT** — screening fail (train −0.062 R; validation +0.170 R) |
| Research Marathon 001 | campaigns 005–008 as a disciplined ladder | — | **NO-GO** |

Test-window discipline held throughout: the 2025–2026 reported test
window was a sealed lockbox, opened only when a screening gate passed.
For CAMPAIGN_007/008/009 it was never opened — the screening gate failed
and per pre-commit the lockbox stayed sealed.

## 3. Why no strategy is approved for paper / demo / live

1. **No strategy passed its own pre-committed gates.** Every campaign
   fixed its pass/fail criteria in a committed pre-commit *before*
   running. None cleared them. Gates were never relaxed after the fact.
2. **Four entry families are negative on real data.** Trend, ADX-trend,
   breakout, and pullback all produced negative expectancy on real
   2020–2026 H4 majors — and CAMPAIGN_005 showed they are *not better
   than random entry* (−0.095 R) once real spreads are paid.
3. **The one near-miss was not confirmed.** Mean reversion's
   validation-era signal never survived an independent train split
   (CAMPAIGN_008 and CAMPAIGN_009 both failed it).
4. **Financing is unmodeled in-engine** — a hard, unconditional
   live-promotion blocker independent of any backtest figure.
5. **The honest base rate.** A USD-500 retail account trading six
   majors, having tested five families with no confirmed edge, has no
   demonstrated edge. Promoting anything would be wishful, not evidence.

## 4. What evidence was strongest

The strongest *positive* signal in the entire project was
**regime-filtered mean reversion on the validation split (2023–2024)**:
CAMPAIGN_008 returned +0.172 R, profit factor 1.29, 6 of 6 pairs
positive, and survived 2× cost stress; CAMPAIGN_009 reproduced it
(+0.170 R). It is the only direction that beat the CAMPAIGN_005
random-entry benchmark on every split it was measured on, and it is
consistent with the CAMPAIGN_005 diagnostic that H4 majors were
choppy / range-bound (efficiency ratio 0.24) across the period.

That is genuinely the best evidence the project produced — and it was
**still not enough**: a single positive split is not a strategy.

## 5. What failed repeatedly

- **Trend / breakout / pullback entries.** Four families, four negative
  results on real data. The 2020–2026 H4 majors did not trend cleanly
  enough for a breakout/continuation entry to overcome costs.
- **The train split.** Both mean-reversion campaigns died on the train
  split (2020–2022): −0.017 R, then −0.062 R. The validation-era edge
  did not generalise backwards in time under either exit rule.
- **Costs.** CAMPAIGN_005 established that real spreads erase the thin
  edges these entries showed in gross terms.

## 6. Retire the Donchian / breakout / trend family

The trend-following (EMA + Donchian), ADX-trend, and volatility-breakout
families should be **retired** as live candidates:

- Three separate campaigns (002, 003, 004) — plus pullback (007) —
  produced negative expectancy on real data.
- CAMPAIGN_005 showed these entries are statistically indistinguishable
  from random once spreads are paid.
- ADX filtering (003) and a compression filter (004) were the obvious
  improvements; both still rejected.

Retiring them does not mean deleting the code — it stays as research
history and as benchmark baselines. It means **no further trend /
breakout / pullback campaign is run, and none of them is a promotion
candidate.** Resurrecting any of them requires a genuinely new thesis
and a fresh human decision, not another parameter pass.

## 7. Mean reversion: interesting, unapproved

Regime-filtered mean reversion is the one direction worth remembering:

- It is the only family with a real, cost-survivable, broad
  (6/6 pairs) positive split.
- It is consistent with the measured market regime (choppy H4 majors).

But it is **unapproved**, and stays so, because:

- It has failed an independent train-split gate **twice** (008, 009).
- A single positive validation split is overfitting-prone evidence, not
  a confirmed edge.
- Its fat-tailed loss risk (a range breaking into a trend) is real.

Any revisit requires a **fresh, human-approved thesis** — not a tweak
of c008/c009, not a relaxed gate.

## 8. Why CAMPAIGN_009 falsified the midline-exit rescue hypothesis

CAMPAIGN_008's only failing gate was train expectancy (−0.017 R). The
hypothesised cause: the backtest engine had no midline-target exit, so
reversion trades exited on a coarse 40-bar time stop instead of at the
mean. CAMPAIGN_009 added exactly that one rule and re-screened under
fresh, stricter pre-committed gates.

**It made the train split worse, not better:** −0.017 R → −0.062 R.
The exit-reason breakdown shows why — the midline `target` exit banked
reverting trades at +1.18 R each, whereas CAMPAIGN_008's `time`-stop
winners had averaged +1.89 R. The midline target **caps the upside**,
and the forgone upside outweighs the losers the early exit rescues.

The hypothesis is falsified: c008's flat train split was *not* an
artifact of the time stop. Two independent, separately pre-committed
campaigns now agree that mean reversion's validation-era signal does not
generalise to the train era under either exit rule.

## 9. Known infrastructure blockers

These are independent of any strategy choice and block live promotion
unconditionally:

1. **Financing / swap is unmodeled in-engine.** Only a conservative
   stress overlay exists. Accurate historical financing cannot be
   sourced from the current stack. Hard live blocker.
2. **D1 (daily) backtesting is invalid.** D1 candles close at the
   17:00 NY rollover; the engine's intraday fill / session / spread
   assumptions are wrong for them (CAMPAIGN_006). D1 cannot be tested
   until next-bar-open fills and a non-rollover spread reference exist.
3. **No live dry-run.** Backtest fills approximate broker behaviour;
   there has been no demo-account dry run of any candidate.

## 10. Recommended next human decision points

None of these is authorized by this memo. Each is a deliberate human
choice; see `docs/research/FUTURE_RESEARCH_BACKLOG.md` for detail.

1. **Decline further strategy research.** The honest base-rate reading
   — five families, no confirmed edge — is reasonable grounds to stop.
2. **Invest in infrastructure, not strategies.** Build the financing
   model and valid D1 support so that *any* future research is sound.
   This is the highest-value work and carries no overfitting risk.
3. **If — and only if — a genuinely new mean-reversion thesis exists**,
   authorize it as a fresh campaign with a new pre-commit. Not a tweak
   of c008/c009.
4. **Lean parity** for one historical rejected campaign, to validate
   the backtest engine against an independent implementation.

Until a human makes one of these calls and explicitly approves a
strategy in `configs/approved_strategies.yaml`, the repo stays frozen.

## 11. References

- Strategy registry & status: `docs/research/STRATEGY_STATUS.md`
- Evidence index (all reports): `docs/research/EVIDENCE_INDEX.md`
- Future research backlog: `docs/research/FUTURE_RESEARCH_BACKLOG.md`
- Marathon close-out: `docs/research/RESEARCH_MARATHON_001_NO_GO.md`
- Approved-strategy registry: `configs/approved_strategies.yaml` (empty)

# Forex-Bot Research — Lessons Learned & Failure Taxonomy 001

**Sprint:** `strategy-search-pause-after-usdjpy-macro-context-001` · **Phase 3**
**Status:** retrospective documentation. No verdict change, no approval, no strategy.

This captures the durable lessons from a long, honest research program that ended in
`PAUSE_STRATEGY_RESEARCH` — so a future restart does not repeat the same mistakes or
re-learn the same nulls. The headline: **the process worked**; the diagnostics repeatedly
killed plausible-looking leads before they became false confidence.

---

## 1. Engineering lessons

- **A machine-enforced freeze/approval gate is the single most valuable artifact.**
  `configs/approved_strategies.yaml` (+ `check_research_freeze.py` /
  `validate_research_archive.py`) made "no strategy is approved" a *checked invariant*, not
  a promise. Every sprint could move fast precisely because the gate could not be silently
  weakened.
- **Read-only by construction beats read-only by intention.** Connecting to the research DB
  with `read_only = True`, hard-refusing reads past the TEST lockbox date, and gitignoring
  bulky/secret artifacts removed whole classes of accident.
- **Pure, unit-tested feature modules pay off.** Causality (no-lookahead) unit tests on
  every feature module caught the difference between decision-time features and labels
  before any analysis depended on it.
- **Deterministic, resumable scripts + compact committed summaries** (JSON manifests, not
  raw dumps) kept the repo reviewable and the artifacts auditable.

## 2. Data lessons

- **Spread/bid-ask data is essential and changes conclusions.** Mid-only backtests would
  have over-stated every edge; the measured ~1.6–1.7 pip active spread (and 5–10 pip
  rollover) is what actually killed the thin leads.
- **Single-cycle history is a hard ceiling for regime work.** 2021–2025 contained one
  monotonic rate cycle, making "rate regime" collinear with the train/val split —
  *non-identifiable*. Regime theses need multi-cycle data.
- **Missing legs matter.** The US–JP rate differential could not be built (no JP rate leg
  in the cache); using US rates alone is a proxy, not the differential.
- **Know your publication lag.** Slow macro features must be joined as-of with an explicit
  lag; "today's daily value" is not available intraday today.

## 3. Backtesting-realism lessons

- **Fixed-horizon exits with no stop are not a strategy.** The London lead looked positive
  only because it held through unbounded adverse excursions to a fixed horizon. The moment
  a realistic intrabar protective stop was added, it went −3 to −8 pips.
- **Cost must be varied, not assumed.** A single optimistic cost hides fragility; the
  conservative cost (p90 spread + higher slippage) flipped a "positive" cell negative.
- **Entry-fill realism matters.** Level-fill on a breakout is optimistic; real stop entries
  slip.

## 4. Stop-loss / MFE-MAE lessons

- **"Wider stops fix it" is usually false.** Post-entry early-exit counterfactuals *reduced*
  expectancy (−0.065 to −0.134R): flagged trades often recover before the stop, so cutting
  them loses winners. Stop/exit tweaks are not a rescue for an absent entry edge.
- **MFE:MAE after arbitrary entry < 1 is a red flag.** USD/JPY showed slightly
  adverse-skewed excursions — there is no free favorable asymmetry to harvest.
- **An oracle that picks the better of MFE/MAE is not tradable.** Hindsight excursion math
  flatters everything; only a live, side-committed rule counts.

## 5. Entry-signal lessons

- **Indicator-confluence entries sit at AUC ≈ 0.50.** Across the whole C0xx program and the
  C022/C023 feature-separation study, the structural entry features (EMA reclaim, ADX,
  pullback depth, RSI, MTF confluence) did not separate winners from losers.
- **Direction is the hard part and it stayed null.** Continuation ≈ reversion ≈ 0.49 across
  sessions, hours, vol regimes, and macro regimes. Magnitude/timing is sometimes
  predictable; *direction* was not.

## 6. Pair-specific lessons

- **Specializing to one "less-bad" pair did not reveal a hidden edge.** USD/JPY was chosen
  to cut confounds and speed iteration; the entry-edge null generalized to it. Single-pair
  focus is only justified by a *new mechanism*, not by "it was almost flat."

## 7. Macro / context lessons

- **Slow macro context is the *right* framing** (no latency edge vs institutions) — but on
  this data it carried **no actionable tradeability conditioning**: raw spread flat across
  all macro cells, whipsaw ~0.50 everywhere, event windows only mechanically vol-elevated
  (direction-blind, time-of-day-redundant).
- **A no-trade filter is the highest-value, lowest-overfit macro output** — but here the
  existing session/rollover spread filter already dominates; macro added nothing.

## 8. Overfitting / multiple-testing lessons

- **Post-hoc cell selection needs a haircut.** The London lead was 1 of 12 session×horizon
  cells; a Bonferroni ×12 haircut removed its significance. Always count the searches.
- **"Both splits positive" is necessary but not sufficient.** The London lead was positive
  on train and validation yet still a 2022/2024 trend-regime artifact — a *year* breakdown
  exposed it.
- **Lock the definition before re-analysis.** Writing the locked-definition doc *before*
  the confirmation run prevented drift into "find the cut that works."

## 9. What would have fooled us without the diagnostics

These all looked promising and were each killed by a specific check:

- **The no-stop London lead** (+2.2/+6.1 pips both splits) — killed by the intrabar-stop
  test + conservative cost + Bonferroni haircut + year breakdown.
- **Post-entry "predictive" management signals** — descriptively real, but the
  counterfactual showed acting on them *reduced* expectancy.
- **USD/JPY "near-flat / less-bad" hints** — flatness is not edge; generalized to null.
- **ADX threshold variants (20 → 22)** — `h4_adx_at_entry` does not separate winners from
  losers, so the gate change had no basis.
- **"Widen the stop" assumptions** — the data showed early exits and stops do not rescue a
  missing entry edge.
- **Post-event volatility elevation** — real but mechanical and direction-blind; not an edge.

## 10. Process improvements for any future restart

1. **Precommit the hypothesis and the cost/stop/haircut model *before* the run** — every
   time, in a locked-definition doc.
2. **Always run: realistic stop + conservative cost + multiple-testing haircut + year/half
   split + (for context features) latency-independence** as a standard falsification panel.
3. **Count every cell searched** and carry the count into the significance haircut.
4. **Separate "effect exists" from "tradable edge exists"** explicitly in every result doc.
5. **Require a mechanism** stated before coding — no mechanism, no campaign.
6. **Treat new data as the unlock**, not new parameter combinations on old data.
7. **Keep the TEST window sealed** until a fully-precommitted campaign earns one final look.
8. **Prefer no-trade filters** as the first, safest use of any context signal.

See `STRATEGY_RESEARCH_RESTART_CRITERIA.md` for the gates these lessons imply.

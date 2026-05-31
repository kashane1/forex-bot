# CAMPAIGN_015 Entry-Bar Stop Semantics Audit

**Date:** 2026-05-26
**Sprint:** `infra-backtrader-campaign-015-riskengine-and-fill-parity-001`

> Docs-only audit. Does **not** approve any strategy or change bespoke engine.

## 1 · What does CAMPAIGN_015 precommit say about `same_bar_adverse_stop_wins`?

From `docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md` §4 Exit:

> If a single bar both touches the stop and the time-stop boundary
> ambiguously, the **adverse stop wins** (`same_bar_adverse_stop_wins = true`).

Frozen parameter table lists `same_bar_adverse_stop_wins = true` as a binding
ambiguity rule. The text is scoped to **exit** ambiguity (stop vs time-stop on
the same bar), not explicitly to the **entry fill bar**.

## 2 · What does bespoke BacktestEngine currently do on an entry bar?

`BacktestEngine` (`src/forex_bot/backtesting/engine.py`):

1. Signal fires on bar N.
2. With `fill_timing = next_bar_open`, entry opens on bar N+1 at bid/ask open.
3. Position is opened; **no same-bar adverse stop check** runs on N+1.
4. Stop/time exits are evaluated starting on subsequent bars in the per-bar loop.

So on the entry bar itself, bespoke **does not** reject or immediately stop out
when the bar range touches the stop.

## 3 · What does Backtrader parity mode now do?

| mode | entry bar behaviour |
|---|---|
| `backtrader_default` (legacy BT) | After fill at N+1 open, if bar range touches stop → immediate `stop_same_bar` exit / rejection |
| `bespoke_current_no_entry_bar_stop` (parity) | Entry accepted; stop checked from bar N+2 onward (via `_try_exit`) |

Later-bar adverse stop precedence is unchanged on both sides.

## 4 · Does current bespoke behaviour appear inconsistent with precommit?

**Partially ambiguous.**

- Precommit `same_bar_adverse_stop_wins = true` reads like a general OHLC
  ambiguity rule and is mirrored in BT adapter docs as applying on the entry bar.
- Bespoke engine implements the rule only for **post-entry** exit bars (and
  stop-vs-time ambiguity), **not** on the entry fill bar.
- Signal-diff first divergence (fold 0 / EUR_USD) is direct evidence of this gap.

## 5 · What would change if bespoke applied same_bar_adverse_stop on entry?

Trades whose entry bar range touches the stop would be rejected or immediately
stopped out. Expect:

- Lower trade count vs current bespoke rehydrate (164 baseline)
- Different expectancy / fold pass rates
- Full CAMPAIGN_015 evidence rerun required (`config_hash` / artifact regeneration)

Magnitude unknown without rerun; signal-diff cell trace showed entry-bar
mismatches were a minority of cell-level divergences but non-zero.

## 6 · Should this be corrected now?

**No — defer to a separate engine-correction sprint.**

This sprint reproduces **current** bespoke behaviour in BT for parity verification.
Changing bespoke fill semantics would invalidate existing CAMPAIGN_015 evidence and
is out of scope for an infrastructure sprint.

## 7 · Recommendation

**Leave current bespoke behaviour as canonical for existing CAMPAIGN_015 evidence**
and document the entry-bar gap explicitly.

Open a **future `infra-bespoke-fill-model-correction-001` sprint** if the team
decides precommit intent requires entry-bar adverse stop on `next_bar_open` fills.
That sprint would:

1. Patch `BacktestEngine` entry-bar handling (with tests)
2. Reconcile precommit wording
3. Rerun frozen CAMPAIGN_015 from scratch (new evidence path)

Until then, BT fold-window comparisons should use
`--entry-bar-stop-policy bespoke_current_no_entry_bar_stop` when matching bespoke.

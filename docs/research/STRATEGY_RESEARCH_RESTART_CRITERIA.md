# Strategy-Research Restart Criteria

**Sprint:** `strategy-search-pause-after-usdjpy-macro-context-001` · **Phase 4**
**Status:** governance document. Standing decision is `PAUSE_STRATEGY_RESEARCH`. This
defines the **strict bar** for restarting strategy research. No verdict change, no
approval, no campaign.

> Restarting strategy research is a deliberate, gated action — never a default and never
> justified by "the last result was almost flat" or "let me try one more parameter."

---

## 1. A restart requires AT LEAST ONE of the following (necessary triggers)

1. **A genuinely external thesis with a documented mechanism and objective rules.** Written
   down *before* coding: the economic / market-structure reason it should work, and an
   unambiguous, codable entry/exit/risk specification. (Internal indicator permutations do
   not qualify.)
2. **A new external data source** that materially changes what is testable, e.g.:
   - a verified **JP rate leg** (to build a real US–JP differential),
   - a **multi-cycle history** (so a rate/macro regime is *identifiable*, not collinear
     with one period),
   - verified **BOJ / CPI / economic-event calendar** data,
   - **options / implied-volatility** data,
   - **order-flow or a credible order-flow proxy**,
   - any other **non-price** source not already exhausted.
3. **A public/academic strategy specification that is structurally different** from every
   failed lane (trend / pullback / ADX / MTF-confluence / microstructure / compression /
   slow-macro-context). Different *decision variable*, not different thresholds.
4. **A known market-microstructure or macro mechanism with a slow, non-latency edge** that
   this project can actually capture (no speed competition with institutions).
5. **A process change that demonstrably reduces multiple-testing / threshold-mining risk**
   (e.g. a pre-registration + out-of-sample protocol stronger than what already failed),
   *paired with* one of triggers 1–4 — a process change alone does not create an edge.

A restart proposal must name which trigger(s) it satisfies and cite the evidence.

## 2. A restart additionally requires (gating conditions, ALL)

Even with a valid trigger, the new work must commit up front to:

- a **precommitted hypothesis + cost/stop/multiple-testing model** (locked-definition doc
  written before any run);
- the **standard falsification panel**: realistic intrabar stop + conservative cost +
  multiple-testing haircut + year/half-split robustness + (for context features)
  latency-independence;
- **train/validation support without touching TEST**; the TEST lockbox opens only once, for
  a fully-precommitted campaign;
- **structural distinctness** from the retired/closed families;
- explicit separation of **"effect exists" vs "tradable edge exists."**

## 3. What is INSUFFICIENT to restart (explicitly rejected)

None of the following, alone or combined, justifies a restart or a new campaign:

- ❌ "Try ADX 25." (or any indicator threshold change)
- ❌ "Use M5 instead of M15." (or any timeframe swap without a new mechanism)
- ❌ "Add one more filter."
- ❌ "Change the stop to 2.5 ATR." (or any stop/exit retune as a rescue)
- ❌ "Focus on only one pair" — without a new, pair-specific mechanism.
- ❌ "The last result was almost flat / less-bad." (flatness is not edge)
- ❌ "The chart looks like it should work." (visual pattern-matching)
- ❌ "Re-run the rejected campaign with relaxed gates." (gates are bright lines)
- ❌ "Mine the same data along a new slicing." (multiple-testing by another name)
- ❌ "The no-stop version was positive." (no-stop is not a tradable configuration)

## 4. Relationship to the campaign-numbering / approval gates

- A restart does **not** create a campaign by itself. It first produces a **precommit
  design** (separate sprint), which only then — if it passes the falsification panel on
  train/validation — earns a single sealed-TEST confirmation.
- `CAMPAIGN_024` (or any new number) is created only **after** a restart trigger is met
  **and** a precommit design exists. Until then, **no C024**.
- Approval (`configs/approved_strategies.yaml`) remains a deliberate, reviewed human action
  requiring the full existing gate chain; it is never a research output.

## 5. Default until a trigger is met

`PAUSE_STRATEGY_RESEARCH`. The infrastructure is preserved (see the pause memo §4) and
ready for the day a valid trigger arrives. Until then, the only sanctioned work is
non-strategy (see `NEXT_ACTION_OPTIONS_AFTER_STRATEGY_SEARCH_PAUSE.md`): data acquisition,
external thesis sourcing, or engineering/infrastructure — none of which is strategy mining.

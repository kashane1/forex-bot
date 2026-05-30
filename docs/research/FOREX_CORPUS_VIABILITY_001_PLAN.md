# Forex Corpus Viability & Market Selection 001 — Plan

**Branch:** `research-forex-corpus-viability-and-market-selection-001`
**Type:** Project-level strategic review. Docs-only. No strategy, no
campaign, no execution, no broker calls.
**Date:** 2026-05-29.

## Why this sprint exists

The forex-bot research program has accumulated a large evidence base
(C001–C031, the C1 factor studies, the non-time-bar lane, the
edge-discovery front gate, the financing/cost audits, and multiple
strategy-search pause memos). The accumulated outcome is unambiguous:

- Traditional H4 strategies (trend, breakout, mean-reversion, pullback)
  have repeatedly failed.
- M15 / lower-timeframe confluence has shown no tradable edge.
- The non-time-bar lane (range/volatility bars) was retired after C029,
  H16, and H03.
- C1 (M1/HTF confluence mean-reversion) was validated as a *genuine
  factor* but failed the front gate because the effect is smaller than
  realistic execution cost — it is catalogued as real-but-not-tradable.
- No strategy is approved; the approved-strategy registry is empty;
  paper/demo/live loops refuse to start.

The project is **no longer primarily blocked by code or campaign
infrastructure.** The remaining question is strategic, not tactical:

> Are we searching the right market, data source, instruments, and
> timeframe at all?

This sprint is a viability assessment — not a strategy sprint.

## Questions this sprint must answer

1. Is the current seven-major OANDA FX corpus still worth
   strategy-search effort?
2. Are the observed failures mostly caused by strategy *ideas* or by
   structural *market/cost* constraints?
3. Would other instruments or data sources provide a better search
   space?
4. What should the next research direction be?

## Hard rules (inherited from the freeze)

- Do **not** create CAMPAIGN_032 or any campaign.
- Do **not** implement any strategy or backtest a new idea.
- Do **not** run train/validation/test evidence.
- Do **not** modify executor/broker behavior.
- Do **not** approve any strategy; do not edit approved strategies
  except to confirm they remain empty.
- Do **not** enable paper/demo/live.
- Do **not** call OANDA APIs or use credentials.
- Do **not** make trading recommendations.
- Do **not** revive or re-tune failed ideas.

## Phase 0 truth audit — current project state

Confirmed by inspection on this branch (clean, from `origin/main`):

- **Approval registry** (`configs/approved_strategies.yaml`): **empty**
  (0 bytes). `forex_bot.approval` fails closed; every paper/demo/live
  loop refuses. Verified against `tests/unit/test_approved_strategies.py`
  (`test_committed_registry_exists_and_is_empty`).
- **Freeze guard** (`scripts/check_research_freeze.py`): enforces
  registry-empty, loops-guarded, no `live: true` in committed configs,
  `STRATEGY_STATUS.md` still asserts NO-GO/FREEZE, and manifest
  artifacts exist.
- **Status of record** (`STRATEGY_STATUS.md`): "Overall: NO-GO. No
  strategy is approved." Last updated at C031 NO_SCAFFOLD.

### Rejected / closed work reviewed

| Item | Verdict | Dominant cause |
|------|---------|----------------|
| C001–C003, C006 trend following | REJECT | no edge / cost-defeated |
| C004, C015, C017 volatility breakout | REJECT | no edge after cost |
| C007, C022, C023, C024 pullback | REJECT/RETIRED | no entry edge |
| C008, C009, C012, C013 mean-reversion | REJECT | cost-defeated; exit pathology |
| C010, C016 portfolio / cross-sectional | REJECT | walk-forward negative |
| C014 event/calendar | REJECT | no edge after cost |
| C018, C019 exit hypotheses | REJECT | no exit edge |
| C020, C021, C025, C026 confluence (MTF/LTF/Donchian) | REJECT | cost gradient, no edge |
| C027 H4 filtered z-score reversion | REJECT_TRAIN_GATE | wafer-thin, forking-path |
| C028 relative-value spread | NO_SCAFFOLD | selection noise |
| **C029 USD_JPY range-bar MTF breakout** | REJECT_TRAIN_GATE | gross +0.084R, net −0.019R (cost-defeated) |
| C031 vol-managed TSMOM | NO_SCAFFOLD | within-null; financing ≈4× spread |
| **H16 overshoot-exhaustion fade** | FAIL_FRONT_GATE | reversion ≈0.50, null-indistinguishable |
| **H03 thin-move fade** | FAIL_FRONT_GATE | weak tilt, cost-defeated, null-internal |
| **C1 factor validation** | GENUINE FACTOR | real M1/HTF confluence mean-reversion |
| **C1 high-vol front gate** | FAIL_FRONT_GATE | net-negative after cost on all 3 pairs |

(C005 = benchmarks/reference; C011 = deduped null baseline/reference;
C030 intentionally unused.)

### Supporting evidence reviewed

- **Feasibility studies**: non-time-bar feasibility (cost-feasibility is
  threshold-specific; 25–30 pip range / 50-pip vol bars are
  cost-feasible on all pairs, but cost-feasible ≠ edge).
- **Financing / cost studies**: `COST_SPREAD_SLIPPAGE_FINANCING_AUDIT_RESULT.md`,
  `CARRY_AND_FINANCING_READINESS_MEMO.md`, `FINANCING_MODEL_STATUS.md`,
  `CAMPAIGN_002_FINANCING_RETROSPECTIVE.md`.
- **Non-time-bar lane decision**: `NON_TIME_BAR_LANE_FINAL_DECISION.md`
  (directional/microstructure non-time-bar search retired on this
  corpus; infra kept).
- **Strategy pause docs**: `BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md`,
  `FINAL_RESEARCH_DECISION_MEMO.md`,
  `STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT.md`,
  `BROAD_STRATEGY_PAUSE_AND_ROADMAP_001_SUMMARY.md`.
- **Approved strategy registry**: empty (confirmed).

## Deliverables (one per phase)

| Phase | Document |
|-------|----------|
| 0 | `FOREX_CORPUS_VIABILITY_001_PLAN.md` (this file) |
| 1 | `FOREX_RESEARCH_EVIDENCE_INVENTORY.md` |
| 2 | `FOREX_STRUCTURAL_COST_CONSTRAINTS.md` |
| 3 | `OANDA_SEVEN_MAJOR_CORPUS_VIABILITY_DECISION.md` |
| 4 | `ALTERNATIVE_MARKET_AND_DATA_SOURCE_COMPARISON.md` |
| 5 | `FUTURE_RESEARCH_OPTIONS_AFTER_FOREX_CORPUS_REVIEW.md` |
| 6 | `NEXT_MARKET_SELECTION_DECISION.md` |
| 7 | `NEXT_PROMPT_AFTER_FOREX_CORPUS_VIABILITY_REVIEW.md` |
| 8 | `FOREX_CORPUS_VIABILITY_AND_MARKET_SELECTION_001_SUMMARY.md` |

(The plan and summary use different filename bases by design — the plan
is keyed to this review, the summary to the full "market selection"
branch name. The research-archive validator checks manifest/campaign/
evidence-index/credential consistency, not PLAN/SUMMARY filename
pairing, so no companion stub files are required.)

## Method

Evidence-only. Every claim is grounded in an existing committed
artifact. No new numbers are produced, no data is fetched, no code that
emits orders is touched. Each phase is committed separately. The sprint
ends with a validation pass (pytest / ruff / freeze / archive / secret
scan / git status).

## Success criteria

A clear strategic decision about whether to keep searching the current
OANDA seven-major FX corpus or redirect to a different market/data
source — without creating a strategy, a campaign, or any trading
activity, and with the freeze left fully intact.

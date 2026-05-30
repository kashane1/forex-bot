# Multi-Market Front-Gate Framework

**Purpose:** generalize the existing edge-discovery front gate so the
*same* disciplined pipeline applies to any instrument/asset class — FX
majors, FX crosses, futures, metals, crypto. This is a **process design**
document; it builds no strategy and runs no evidence. Its job is to make
"can this market produce a tradable edge?" answerable the same trustworthy
way everywhere, so no new market gets a weaker bar than the seven majors
did.

## Design principle

> **Any action a market can take to earn a campaign, every other market
> must take too.** One gate, one evidence bar, instrument-specific cost
> models — no bespoke shortcuts per asset class.

The current gate (the import-isolated lab at `research/edge_discovery/`)
already implements the core checks — **matched-null benchmark**,
**filter-ablation**, **multiple-comparison correction**, and
**cost-feasibility**. Generalization = (a) an instrument-agnostic
*registration* interface (candle source + cost model + calendar), and
(b) explicit stage gates with required evidence, below.

## What "generalizing" requires (per asset class)

Each instrument registers three things; the rest of the pipeline is shared:

1. **Candle/source adapter** — lookahead-free, parity-checked bars in the
   common schema (FX bid/ask H4+M1; futures continuous-roll; crypto 24/7;
   metals as FX or futures).
2. **Instrument-specific cost model** — spread/slippage + the right
   carry model: FX swap (daily rollover), futures basis/roll, crypto
   perpetual funding (or none for spot), metals lease/storage, equities
   margin+dividends. **Never reuse another instrument's costs.**
3. **Calendar/session model** — FX 24×5 with weekend gap; futures
   session + roll dates; crypto 24/7 no gap; equities exchange hours +
   corporate actions.

Asset-class-specific cautions the gate must encode: continuous-contract
**roll artifacts** (futures), **survivorship/look-ahead** in universes
(equities/crypto alts), **structural breaks** (e.g. EUR_CHF 2015), and
**tick-count "volume" is a proxy** in spot FX (real volume only in
futures/crypto).

---

## The five stages and their required evidence

A market/idea advances only by clearing each stage in order. Earlier
stages are cheap and reversible; later stages are expensive and gated by
committed pre-registration. **Stages 1–3 are research and run under the
freeze; Stage 4 needs a pre-commit; Stage 5 needs a human approval.**

### Stage 1 — Discovery (cheap, exploratory)
- **What:** characterize the instrument and surface *candidate* effects
  (cost atlas, session/vol structure, autocorrelation, cross-sectional
  dispersion, regime structure). No pre-registration; exploratory by
  design.
- **Required evidence to pass:** a documented, lookahead-free dataset
  with an instrument-specific cost model; a written list of *candidate*
  effects with a falsifiable mechanism each. **Not** a performance claim.
- **Fails if:** data is not lookahead-free/parity-checked, or no
  mechanism can be articulated (pure data-mining).

### Stage 2 — Factor validation (is the effect real?)
- **What:** test whether a candidate effect is statistically real and
  *instrument-specific* — not a restatement of a generic property.
- **Required evidence:** beats a **matched null** (structure-matched
  random baseline) on the chosen response; survives **filter-ablation**
  (each filter adds value, not a forking path); survives
  **multiple-comparison correction** (not best-of-N noise); ideally
  replicates across ≥2 independent instruments/regimes.
- **Outcome:** `GENUINE_FACTOR` (real, may still be untradable) vs
  `WITHIN_NULL` / `SELECTION_NOISE`. *Gross* effect only — cost is
  Stage 3. (C1 reached `GENUINE_FACTOR` here.)

### Stage 3 — Front-gate screen (is it tradable on this market?)
- **What:** a **pre-registered, frozen-threshold** screen of whether the
  validated factor survives realistic execution cost on this instrument.
- **Required evidence:** pre-committed thresholds *before* any
  conditioned number; **cost-feasibility** — net of instrument-specific
  spread + slippage + financing the effect is positive on the primary
  instruments and at a cost-stress multiple; stability across years/
  sessions; generalization to a held-out instrument. No re-tuning to
  the result.
- **Outcome:** `PASS_FRONT_GATE` (earns a Stage-4 scaffold) vs
  `FAIL_FRONT_GATE`. The whole seven-major programme (C1, H16, H03,
  C026/C029/C031) **failed here on cost** — this is the decisive gate.

### Stage 4 — Campaign (pre-registered backtest evidence)
- **What:** a numbered campaign with a committed pre-commit: train →
  validation, with a sealed test lockbox opened **only** if the
  train/validation gates pass.
- **Required evidence:** committed pre-commit (universe, params,
  gates frozen); independent backtest **parity**; matched-null and
  anti-overfit classification; financing modeled; walk-forward with
  per-fold gates; deduped/contamination-safe inputs. **No parameter
  tuning after seeing results.**
- **Outcome:** `REJECT_*` or a passing train/validation that *may* open
  the test lockbox. **Out of scope this sprint — no campaign is created.**

### Stage 5 — Promotion (human approval to a loop)
- **What:** a deliberate human decision to add an entry to
  `configs/approved_strategies.yaml` for a single loop mode.
- **Required evidence:** a passing campaign report as `evidence_report`;
  `FinancingTreatment.MODELED` (observed-rate reconciliation), no
  lookahead, costs modeled, OOS≈IS, parameter sensitivity acceptable,
  drawdown within policy; execution-realism promotion blockers cleared;
  explicit human sign-off. Live additionally requires the config-layer
  live gates.
- **Outcome:** registry entry (paper → demo → live, separately).
  **Out of scope this sprint — nothing is approved; registry stays
  empty; loops refuse.**

---

## Stage summary

| Stage | Question | Pre-registration? | Freeze status | This sprint |
|-------|----------|-------------------|---------------|-------------|
| 1 Discovery | What candidate effects exist? | no | research | design only |
| 2 Factor validation | Is the effect real & specific? | no | research | design only |
| 3 Front-gate screen | Does it survive cost here? | **yes (frozen thresholds)** | research | design only |
| 4 Campaign | Does pre-registered backtest hold? | **yes (pre-commit)** | needs pre-commit | **not run** |
| 5 Promotion | Human-approved to trade? | n/a | needs human approval | **not done** |

## How a new market enters the framework

1. Register adapter + cost model + calendar (Stage-1 prerequisite).
2. Run Stage 1 discovery → documented dataset + candidate list.
3. Run Stage 2 factor validation → `GENUINE_FACTOR` or stop.
4. Run Stage 3 front-gate screen (pre-registered) → `PASS` or stop.
5. Only a `PASS` justifies proposing a Stage-4 campaign (separate,
   pre-committed, human-initiated sprint).

This framework is the contract the data-expansion sprints feed into: a
new market is "ready" when it can be registered (adapter + cost model +
calendar) and run through Stages 1–3 — which is exactly what the non-USD
cross expansion (`NEXT_DATA_EXPANSION_DECISION.md`) prepares.

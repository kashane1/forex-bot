# Free / Local Independent Verifier — Plan

**Date:** 2026-05-22 · **Branch:** `infra-retire-quantconnect-lean-001`
**Supersedes (for the parity path):** `LEAN_PARITY_DESIGN.md`,
`LEAN_PARITY_EXECUTION_GUIDE.md`, `LEAN_PARITY_LOCAL_STATUS.md`
(retained as historical).

Replacement for the QuantConnect/LEAN parity path. The replacement is
**fully local, free, deterministic, no cloud, no API, no broker
credentials**. It does not change strategy rules. It does not change
CAMPAIGN_002 parameters. It does not approve a strategy.

> `strategy_evidence: false`. This plan describes verification of the
> *measurement instrument* (the bespoke backtest engine), not of any
> strategy. **CAMPAIGN_002 remains REJECT** regardless of any verifier
> outcome. `configs/approved_strategies.yaml` remains empty. Paper /
> demo / live remain blocked.

## 1. Purpose

Provide independent-engine corroboration for the bespoke backtest
engine on the CAMPAIGN_002 H4 `trend_following` baseline. The bespoke
engine is internally reproducible — the custom-engine reproduction
matches the committed CAMPAIGN_002 report exactly (1,032 trades, zero
per-pair deltas), and the no-RiskEngine reference (1,647 trades)
isolates the strategy + engine mechanics. What is missing is **proof
that the engine itself is not the source of the REJECT** — an
independent implementation that consumes the same data and produces
comparable trade outcomes within tolerance.

The QuantConnect/LEAN path was the prior plan for this; that path is
retired (see `QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`). This plan
defines the replacement.

## 2. Non-goals

- **Not a new strategy.** No new entry / exit / sizing rule, no new
  parameter, no new family.
- **Not a CAMPAIGN_002 re-run.** CAMPAIGN_002 is REJECT and stays
  REJECT.
- **Not strategy approval.** Even a full verifier PASS approves
  nothing.
- **Not a tuning loop.** No knob is turned to improve numbers.
- **Not a live / paper / demo trigger.** This plan does not touch any
  order-capable loop and does not modify
  `configs/approved_strategies.yaml`.
- **Not a replacement for LEAN parity tolerances.** The tolerances and
  divergence taxonomy from `LEAN_PARITY_COMPARISON_METHOD.md` carry
  over; this plan re-uses them.
- **Not a cloud / API / broker tool.** No QuantConnect, no LEAN, no
  brokerage connection, no API authentication.

## 3. Safety constraints

The verifier and the implementing sprint must satisfy **all** of the
following, on every phase, on every commit:

1. `configs/approved_strategies.yaml` stays empty (`approved: []`).
2. CAMPAIGN_002 stays REJECT. No campaign re-runs.
3. Paper / demo / live loops keep refusing before broker construction.
4. No broker credential is read, prompted-for, written, or echoed.
5. No `.env` is committed; no `*.sqlite3` is committed; no large
   regenerable CSV is committed.
6. No new external dependency is added unless explicitly approved in
   its own phase (see §4 candidate approaches).
7. The bespoke engine code is **not modified** to match the verifier.
   If the verifier disagrees, that is a finding to localize, not a
   signal to tune the bespoke engine.
8. The CAMPAIGN_002 rules in
   `research/lean_parity/campaign_002_h4_spec.md` and
   `docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md` are **not
   modified** by the verifier work. The verifier reads them; it does
   not change them.
9. The freeze checker, archive validator, and secret scanner must
   pass on every commit.
10. No reference to "create a QuantConnect account" / `lean login` /
    `lean init` / `lean backtest` may be added to any new doc.

## 4. Candidate approaches

Four candidates were considered. Each is described with the case for
and against, and a feasibility verdict given this repo's dependencies
and conventions.

### 4a. Minimal independent event-loop verifier *(recommended)*

A standalone Python module + script in `research/parity_verifier/`,
implementing the CAMPAIGN_002 rules on its own from scratch — its own
EMA / ATR / Donchian, its own bar loop, its own stop/trailing logic,
its own sizing — using only the **existing** repo dependencies
(`pandas`, `numpy`, `pydantic`, `pyyaml`). The verifier consumes the
seven-pair H4 candle CSVs the bespoke engine exported and the
CAMPAIGN_002 frozen parameter set, and emits a trade list + per-pair
summary in the same shape as the no-RiskEngine bespoke reference.

**Pros**
- No new dependency. Repo's `pandas` / `numpy` are sufficient.
- Fully local, fully deterministic.
- Code path is genuinely independent — every indicator, every
  comparator, every fill rule is written separately from the bespoke
  engine. A bug shared between the two would have to be *re-invented*,
  which is much weaker than a bug *copied*.
- Reuses the existing comparison framing: same no-RiskEngine bespoke
  reference, same divergence taxonomy, same tolerances.
- Simple to audit. A reviewer can read the verifier in one sitting.

**Cons**
- The verifier is small enough to be wrong in the same direction the
  bespoke engine is wrong, by analytical coincidence (e.g. both using
  the same EMA seed convention because both are "the obvious"
  convention). Independence is by construction, not by being a famous
  third-party library.
- Requires careful naming + module separation so that no bespoke
  engine code is silently imported.

### 4b. Vectorized pandas verifier

A second-implementation verifier that processes candles vectorized
(pandas `rolling`, `ewm`, `shift`) rather than bar-by-bar. Strategies
with path-dependent exits (trailing stops, time stops, intra-bar
priority) are awkward to vectorize and historically a place where
vectorized and event-loop engines diverge.

**Pros**
- Independent style of computation — different bug surface than an
  event loop.
- Fast.

**Cons**
- CAMPAIGN_002 has **trailing stops**, **time stops**, and a precise
  intra-bar exit precedence. Vectorizing those faithfully is harder
  than writing an event loop. A vectorized verifier that approximates
  the precedence is *less* useful, not more — its divergences from
  the bespoke engine cannot be cleanly classified.
- Increases the chance the verifier is "wrong differently" from the
  bespoke engine — a divergence then carries less signal.

**Verdict:** not recommended as the primary verifier. May be added as
a **secondary sanity check** on indicator series alone (EMA, ATR,
Donchian) if the primary verifier's indicator outputs ever look
suspicious — see 4d.

### 4c. Third-party-library feasibility review (`backtesting.py` / `vectorbt` / `backtrader`)

Use an established backtest library as the independent engine.

| library | dependency-safe? | suitability |
|---|---|---|
| `backtesting.py` | **No** — not currently a repo dependency. Permissive AGPL/GPL-adjacent license requires review before adding. Single-asset focus; awkward to drive seven pairs from one config. | Marginal. |
| `vectorbt` | **No** — not a repo dependency. Vectorized core; same trailing-stop / time-stop concerns as 4b. Heavy-weight install (numba, etc.). | Poor fit for this strategy. |
| `backtrader` | **No** — not a repo dependency. Event-loop, multi-asset, mature. Stagnant upstream, but functional. | Plausible, but introduces a large dependency for a one-time use. |

**Pros**
- A famous library is more likely to be "independently wrong" than a
  small in-tree verifier.

**Cons**
- All three require **adding a new dependency** — out of scope for
  this branch unless explicitly approved.
- Adapter code from CAMPAIGN_002 rules → library primitives is itself
  a parity surface; mismatches between the adapter and the bespoke
  rules are easy to introduce and hard to spot.
- License review (especially `backtesting.py`'s AGPL stance) is a
  separate decision the user must make before adopting.

**Verdict:** **not** the primary verifier on this branch. Listed for
completeness so the decision is on the record. If the user later
prefers a third-party library, `backtrader` is the most plausible
candidate and would require its own opt-in sprint.

### 4d. Fixture-level rule verifier

Small `pytest`-style verifier that pins **just the indicator outputs**
(EMA, ATR, Donchian) and a few **trade-rule fixtures** (e.g. "given
this bar sequence and this state, the entry / exit / stop is X").

**Pros**
- Smallest possible scope. Easy to write, easy to audit.
- Catches indicator-definition mismatches and rule-edge-case
  mismatches.

**Cons**
- Does not produce a trade list or per-pair summary; cannot
  corroborate the bespoke engine end-to-end.
- Only useful as a **layer below** the primary verifier — to localize
  divergences the primary verifier surfaces.

**Verdict:** keep as a **supporting** artifact, not the primary
verifier.

## 5. Recommended approach

**4a — the minimal independent event-loop verifier**, with **4d as a
supporting fixture-level rule verifier** that the primary depends on.

Rationale:
- It is the only approach that introduces **no new dependency** and
  produces a **full trade list + per-pair summary** comparable to the
  bespoke no-RiskEngine reference.
- It re-uses the inputs already prepared by the LEAN sprints (the
  seven-pair H4 exports and the no-RiskEngine bespoke reference) and
  the existing comparison framing (tolerances, divergence taxonomy).
- It is auditable end-to-end in one sitting — every operation that
  could diverge from the bespoke engine is in plain sight.
- 4b and 4c remain available as later, opt-in upgrades; this plan does
  not foreclose them.

## 6. Why this provides useful independent evidence even though it is not LEAN

A common worry: "if the verifier is also in-tree Python, isn't it just
a second copy of the same bespoke engine?" The verifier has structural
features that make it genuinely independent without being LEAN:

1. **Separate module tree.** It lives in a separate package
   (`research/parity_verifier/`), imports nothing from
   `src/forex_bot/`, and re-implements every primitive (indicators,
   bar loop, stops, sizing). A reviewer can grep for forbidden imports
   to confirm.
2. **Different control flow.** Even within an event loop, the
   verifier may make choices the bespoke engine does not (e.g. ordering
   of intra-bar checks, position-state representation). Each such
   choice is a place a bug in the bespoke engine could surface as a
   divergence.
3. **Re-derived indicator definitions.** The verifier's EMA / ATR /
   Donchian are coded against the canonical mathematical definition,
   not by copying the bespoke implementation. The fixture-level rule
   verifier (4d) pins those re-derivations.
4. **Independent input wiring.** The verifier reads the **CSVs**
   (the same export bundle the LEAN algorithm would have read), not
   the bespoke engine's in-memory candle bars. Any silent transform
   the bespoke engine does that the CSV pipeline does not is a
   divergence the verifier will surface.
5. **Independent output wiring.** The verifier writes its own trade
   list and per-pair summary; the comparison harness reads two files
   that were written by separate code paths.

A divergence between the verifier and the bespoke engine is therefore
**informative**: it points either to a bespoke-engine discrepancy (to
document, never to tune away) or to a verifier-implementation bug (to
fix on the verifier side and re-run). A full PASS is **independent
corroboration**: two engines built from the spec, never sharing code,
agree on the numbers.

This is not as strong as corroboration by a famous third-party
backtester. It is much stronger than the current state (no
independent corroboration at all) and strictly cheaper / safer / more
local than the retired LEAN path.

## 7. Inputs

The verifier consumes the following inputs, all already prepared by
the LEAN sprints. None is created or modified by this plan.

| input | path | committed? | source |
|---|---|---|---|
| OANDA H4 research SQLite | `data/oanda_h4_research.sqlite3` | no (gitignored) | rehydrated locally; reproducible from `scripts/oanda_h4_data_rehydrate.py` |
| Seven-pair H4 candle CSVs | `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv` | no (gitignored) | regenerable from `EXPORT_MANIFEST.md` |
| CAMPAIGN_002 frozen parameter / rule set | `research/lean_parity/campaign_002_h4_spec.md` and `docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md` | yes | frozen by CAMPAIGN_002 |
| Bespoke no-RiskEngine reference | `research/lean_parity/campaign_002_h4_bespoke_reference.json` (1,647 trades) | yes | written by the LEAN sprints |
| Bespoke with-RiskEngine reference | `backtests/diagnostics/custom_campaign_002_h4_parity.md` (1,032 trades, exact match to committed report) | yes | written by the LEAN sprints |

The verifier compares its own output against the **no-RiskEngine**
reference (1,647 trades) — the bespoke RiskEngine is bespoke-only and
out of scope for the verifier, exactly as it was for the LEAN
algorithm. See `CAMPAIGN_002_LEAN_MAPPING_SPEC.md` §0.

## 8. Outputs

| output | path (proposed) | format | purpose |
|---|---|---|---|
| Independent trade list | `research/parity_verifier/results/campaign_002_h4/trades.csv` | one row per trade: instrument, entry_ts, entry_price, side, exit_ts, exit_price, exit_reason, R, return_pct | the verifier's view of the trades CAMPAIGN_002 would have taken |
| Per-pair summary | `research/parity_verifier/results/campaign_002_h4/parity_summary.json` | same shape as the LEAN `parity_summary.json` (pairs list with instrument, trades, expectancy_r, return_pct) | compatible with `scripts/compare_lean_campaign_002_parity.py` or its successor |
| Comparison report | `docs/research/PARITY_VERIFIER_CAMPAIGN_002_RESULT.md` | human-readable | per-pair OK/WARN/FAIL, overall verdict, divergence classification |
| Verifier implementation notes | `docs/research/PARITY_VERIFIER_IMPLEMENTATION_NOTES.md` | human-readable | exactly which conventions the verifier picks (e.g. EMA seed, ATR Wilder vs SMA), where it differs from the bespoke engine by design, and where any approximation lives |

`trades.csv` and `parity_summary.json` are written under `research/`
and are **regenerable**; whether they are committed depends on size
(probably JSON yes, CSV no — finalized in the implementation sprint).

## 9. Divergence taxonomy

A verifier divergence is classified under exactly one of the following
buckets (extended from the LEAN-era taxonomy in
`LEAN_PARITY_COMPARISON_METHOD.md`):

1. **Data mismatch.** The verifier and the bespoke engine consumed
   different candles (different rows, different OHLC, different
   timestamps).
2. **Timestamp / session mismatch.** Same candles, different
   timezone / session-boundary / Sunday-open handling.
3. **Indicator mismatch.** EMA / ATR / Donchian / ADX series differ on
   identical input (seed convention, recurrence formula, warmup
   length).
4. **Entry / exit rule mismatch.** Indicator series agree, but the
   rule that turns them into a signal differs (e.g. equality vs
   strict-inequality, prior-bar vs current-bar reference).
5. **Spread / slippage / fill mismatch.** Same signal bar, different
   fill price (signal-bar-close vs next-bar-open, spread modeling,
   slippage adders).
6. **Stop / trailing mismatch.** Same entry, different stop ladder or
   trailing rule (initial stop placement, trailing trigger, intra-bar
   priority of stop vs target).
7. **Sizing / PnL mismatch.** Same trade, different size or
   PnL-conversion (pip value, instrument quote-currency conversion,
   risk-per-trade interpretation).
8. **Unknown.** A divergence the implementer cannot yet localize.
   Open as an explicit finding; do not close until classified.

A divergence is always a **finding to localize**, never a result to
accept or hide. A divergence traced to a verifier-implementation bug
is fixed on the verifier side and the run repeated. A divergence
traced to a real bespoke-engine discrepancy is documented as an
engine finding and **never tuned away**.

The tolerance ranges from `LEAN_PARITY_COMPARISON_METHOD.md`
(trade count ±5% / ±15%, expectancy ±0.03 / ±0.10 R, return ±0.5 pp /
±2.0 pp) carry over unchanged. The pass / fail rules carry over.

## 10. Guardrails

1. **No tuning.** No parameter on either side is changed in service
   of better numbers. If the verifier disagrees with the bespoke
   engine, neither side is "tuned to match" — the disagreement is
   classified and resolved on its merits.
2. **No strategy approval.** Even a clean PASS approves nothing.
   `configs/approved_strategies.yaml` is not edited by this work.
3. **No campaign run.** This work does not register a new campaign,
   does not produce a strategy verdict, and is not listed under
   `campaigns` in `EVIDENCE_MANIFEST.json`. Its outputs are
   `diagnostic_artifacts` only — `strategy_evidence: false`.
4. **No paper / demo / live enablement.** No loop is unblocked, no
   broker construction is reached, no broker credential is read.
5. **No change to CAMPAIGN_002 rules.** The spec docs (`campaign_002_h4_spec.md`,
   `CAMPAIGN_002_LEAN_MAPPING_SPEC.md`) are read-only inputs.
6. **No change to the bespoke engine to "make it match" the verifier.**
   If the verifier surfaces a real bespoke-engine discrepancy, that is
   documented as an engine finding and the next step is a separate
   sprint that proposes a fix on its own merits — not a silent code
   edit during the verifier work.
7. **No new external dependency** without an explicit phase that
   reviews license, scope, and removal path. The recommended approach
   uses only repo-existing dependencies.
8. **No commit of regenerable bulk data.** SQLite stores, candle CSVs,
   verifier trade CSVs above a small size threshold stay gitignored
   and are regenerable from manifests.
9. **No credential of any kind** is read, prompted-for, written, or
   committed. The freeze checker, archive validator, and secret
   scanner must pass on every commit.
10. **No reopening of the QuantConnect / LEAN path** without explicit
    user approval. The retirement decision stands.

## 11. Proposed phased implementation sprint

A separate sprint, on its own branch (suggested name
`infra-free-local-parity-verifier-001`), with the following phases.
This plan does **not** start that sprint; it only defines what it
would look like.

- **Phase 0 — baseline.** Re-run pytest, ruff, archive validator,
  freeze checker, secret scanner. Confirm
  `configs/approved_strategies.yaml` is empty and paper / demo / live
  refuse. Confirm SQLite store + candle CSVs are locally present (or
  regenerable from manifest). Commit only if anything changed.
- **Phase 1 — verifier scaffold.** Create the
  `research/parity_verifier/` package skeleton: `__init__.py`, a
  pyproject-aware import boundary (it must not import from
  `src/forex_bot/`), unit-test scaffold. No business logic yet. Add
  a CI-friendly lint rule that forbids `forex_bot` imports from
  inside the verifier package. Commit.
- **Phase 2 — fixture-level rule verifier (4d).** Implement and pin
  EMA / ATR / Donchian fixtures. Bar-sequence fixtures for: entry,
  exit at target, exit at stop, trailing stop trigger, time stop,
  intra-bar priority. All fixtures live in
  `tests/research/parity_verifier/` and run under pytest. Commit.
- **Phase 3 — single-pair event loop.** Implement the verifier event
  loop for one pair (suggest `EUR_USD` — the largest, cleanest tape).
  Read the CSV, produce a trade list. Write `trades.csv` and a
  one-pair `parity_summary.json`. Compare against the no-RiskEngine
  reference; expect a divergence iteration. Document classifications
  in `PARITY_VERIFIER_IMPLEMENTATION_NOTES.md`. Commit.
- **Phase 4 — seven-pair generalization.** Extend Phase 3 to all
  seven pairs. Produce the full `parity_summary.json`. Run the
  comparison; classify any divergences. Commit.
- **Phase 5 — comparison harness wiring.** Either reuse
  `scripts/compare_lean_campaign_002_parity.py` (renaming may be
  appropriate) or write a verifier-specific comparison script. Either
  way, the comparison-report doc
  `PARITY_VERIFIER_CAMPAIGN_002_RESULT.md` is generated by the
  script. Commit.
- **Phase 6 — divergence resolution.** Classify each remaining
  divergence. Verifier-side bugs are fixed and the run repeated.
  Bespoke-side discrepancies are documented as engine findings (no
  code edit). Commit per finding.
- **Phase 7 — final validation & summary.** Re-run all validators,
  refresh `EVIDENCE_INDEX.md` and `EVIDENCE_MANIFEST.json` to list the
  verifier artifacts under `diagnostic_artifacts` (each carrying
  `strategy_evidence: false`), and write the sprint summary. Commit.

At every phase: freeze checker, archive validator, secret scanner
must pass. At no phase does the sprint touch
`configs/approved_strategies.yaml`, the bespoke engine, the
CAMPAIGN_002 rules, or any broker credential.

## 12. What success and failure look like

- **Verifier PASS.** Two engines (bespoke and the in-tree verifier),
  built from the same spec without sharing code, agree on the trade
  count, expectancy, and return per pair within tolerance. **This
  does not approve a strategy.** It says only "the bespoke engine
  measured CAMPAIGN_002 consistently with an independent
  implementation." The strategy it measured is still REJECT.
- **Verifier WARN.** Drift inside the review band. Classify and
  resolve before relying on the comparison; a WARN is not a clean
  parity.
- **Verifier FAIL.** Drift outside tolerance, a missing pair, or
  malformed output. Classify under the taxonomy and resolve. Never
  tune to remove a FAIL.

In all three cases: no strategy approval, no campaign change,
CAMPAIGN_002 stays REJECT, freeze stays intact.

## 13. What this plan does NOT do

- It does **not** start the implementation. It is documentation only.
- It does **not** touch the bespoke engine, the campaign reports,
  `configs/approved_strategies.yaml`, the loop refusal code, the
  broker code, or `EVIDENCE_MANIFEST.json`'s `campaigns` list.
- It does **not** add a dependency.
- It does **not** create the `research/parity_verifier/` package
  (Phase 1 of the implementation sprint will).
- It does **not** reopen QuantConnect / LEAN. The retirement stands.

## 14. Cross-links

- Retirement decision: `QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`
- Bespoke no-RiskEngine reference data shape:
  `research/lean_parity/campaign_002_h4_bespoke_reference.json`
- Tolerances + taxonomy (inherited):
  `LEAN_PARITY_COMPARISON_METHOD.md`
- CAMPAIGN_002 mapping spec: `CAMPAIGN_002_LEAN_MAPPING_SPEC.md`
- Frozen CAMPAIGN_002 rules: `research/lean_parity/campaign_002_h4_spec.md`
- Approved-strategy registry (must stay empty):
  `configs/approved_strategies.yaml`
- Evidence index: `EVIDENCE_INDEX.md`

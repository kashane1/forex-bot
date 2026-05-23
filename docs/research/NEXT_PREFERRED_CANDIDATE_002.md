# Next Preferred Candidate (Sprint 002)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-002`
`strategy_evidence: false`

Phase 3 selection of the **next preferred candidate** for a
future scaffold sprint, following the Phase 2 reassessment in
[`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md).
**This selection is not an approval and does not become an
approval through any subsequent sprint without a deliberate
human action.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked. **The
> selected candidate is a diagnostic anchor, not a paper
> candidate.** It cannot be approved by design; that is the
> point.

## 1. Selected candidate (one-line)

**C5 — H4 random-entry diagnostic anchor**, to be implemented
under campaign label **`CAMPAIGN_011`** with strategy
**`random_entry_anchor 0.1.0-c011`**.

| field | value |
|---|---|
| candidate id (from prior shortlist) | **C5** |
| candidate role | **diagnostic anchor / null model** (NOT a paper candidate) |
| proposed strategy id | `random_entry_anchor` |
| proposed strategy version | `0.1.0-c011` |
| proposed campaign label | `CAMPAIGN_011` |
| proposed future scaffold branch | `research-random-entry-diagnostic-anchor-001` |
| proposed future evidence branch | `research-random-entry-diagnostic-anchor-walk-forward-001` |
| timeframe | H4 (matches every prior H4 family + the 7-pair universe) |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (matches CAMPAIGN_010) |
| data source | `data/campaign_002.sqlite3` (gitignored symlink — same as CAMPAIGN_010) |
| financing posture | ESTIMATED + conservative stress (matches CAMPAIGN_010); MODELED refused |
| risk-engine mode | backtest (matches CAMPAIGN_010) |
| approval path | **none — null model by design** |

## 2. Why C5, not C2 / C3 / C4

Summary from Phase 2's scoring table; the decisive factors:

| factor | C2 | C3 | C4 | **C5 (selected)** |
|---|:---:|:---:|:---:|:---:|
| zero MODELED-financing dependency | ✗ | ✓ | ✓ | ✓ |
| zero engine-code change | ✓ | ✓ | ✗ | ✓ |
| zero D1-aggregation work | ✓ | ✗ | ✓ | ✓ |
| zero tunable parameters | ✗ | ✗ | ✗ | **✓** |
| zero overfit risk (structurally) | low | medium-high | medium | **none** |
| validates the evidence pipeline as designed | weak | medium | medium | **strong** |
| establishes a falsifiability bar for every future candidate | no | no | no | **yes** |
| recoverable if "wrong" | medium (long block on MODELED) | medium | high (engine commitment) | **low (REJECT is the expected output)** |

C2 / C3 / C4 are not abandoned — they are deferred behind
infrastructure work or behind the falsifiability anchor (see
[`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)
§8.4 for the recommended ordering). C5 is **the lowest-risk,
highest-pipeline-validation next step** after three consecutive
directional REJECTs.

## 3. Why C5 is not CAMPAIGN_002-like

| dimension | CAMPAIGN_002 (`trend_following 0.1.0`) | **C5 (`random_entry_anchor 0.1.0-c011`)** | distinct? |
|---:|---|---|:---:|
| 1 theoretical bucket | momentum / trend continuation | **null model (no theoretical edge)** | ✓ |
| 2 primary entry signal | EMA-50 vs EMA-200 + Donchian-20 break in trend direction | **deterministic-seed coin flip per H4 bar where the position slot is free** | ✓ |
| 3 primary exit signal | ATR-2.0× trailing stop + N-bar time stop | ATR-stop + fixed bar-count time stop (deterministic, no trail in v1) | ≈ (both use ATR-stop family — the *only* dimension that overlaps) |
| 4 timeframe / universe | H4 / 7 majors | H4 / 7 majors | ≈ (deliberately matched so the comparison is on the strategy, not the universe) |
| 5 data inputs | EMA inputs + Donchian high/low + ATR | **only the H4 bar timestamp (as deterministic seed input) + ATR for stop sizing** | ✓ |
| 6 failure-mode hypothesis | "CAMPAIGN_002 lost because the EMA + Donchian entry has no edge after costs" | **"random entry has no edge by construction — measuring how much it loses by sets the falsifiability bar"** | ✓ |

**Score: 4 of 6 distinctness** vs CAMPAIGN_002. The two ≈
dimensions (exit signal flavour, timeframe / universe) are
**deliberately matched** so the comparison is a clean
isolation of the entry signal. Both random and trend share the
same engine, the same RiskEngine gates, the same cost model;
they differ on the entry mechanic, which is the variable under
study.

Note: distinctness scoring is exempted by the protocol for null
models per §4; C5's "score" here is informational only. The
selection is not blocked by the ≥ 3-of-6 threshold even if it
were enforced (4 / 6 > 3 / 6).

## 4. Why C5 is not CAMPAIGN_010-like

| dimension | CAMPAIGN_010 (`session_breakout 0.1.0-c010`) | **C5 (`random_entry_anchor 0.1.0-c011`)** | distinct? |
|---:|---|---|:---:|
| 1 theoretical bucket | liquidity-flow continuation (London-open) | **null model** | ✓ |
| 2 primary entry signal | London-bar close penetrating prior Asian-bar high/low | **deterministic-seed coin flip; no session, no prior-bar reference** | ✓ |
| 3 primary exit signal | ATR-2.0× stop + 6-bar time stop | ATR-stop + N-bar time stop (parameters chosen to match CAMPAIGN_010's exit so the *entry comparison* is clean) | ≈ |
| 4 timeframe / universe | H4 / 7 pairs | H4 / 7 pairs | ≈ (deliberately matched) |
| 5 data inputs | bar-of-day / hour-of-day + ATR + prior-bar OHLC | **bar timestamp (as deterministic seed) + ATR (for stop sizing)** | ✓ |
| 6 failure-mode hypothesis | "London-open continuation has no edge net of costs" | **"any entry will lose at the random-baseline rate net of costs unless a specific edge survives"** | ✓ |

**Score: 4 of 6 distinctness** vs CAMPAIGN_010. Same pattern as
§3 — exit flavour and timeframe / universe are matched
deliberately; the comparison isolates the entry signal.

C5 does not use:
- The session windows (`asian_session_hours_utc`, `london_session_hours_utc`)
- The Asian-range gate (`min_asian_range_atr_fraction`)
- The London-close vs prior-Asian-high/low entry mechanic
- Any of the CAMPAIGN_010 frozen parameters except `atr_lookback`
  and `atr_stop_multiple` (used identically by **every** prior
  H4 candidate and which are not a tunable variable in C5 — see §5)

## 5. Why this is not parameter tuning

The §12 / §2.A–§2.G disqualifiers in
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
applied to C5:

| pattern | C5 status |
|---|---|
| Test-window leakage in design | clean — no 2020–2026 statistic motivates any C5 parameter. |
| Filter-set tuning to a prior campaign's losing trades | clean — no filter is conditioned on prior campaign output; the only filter is the same spread-filter every prior strategy has (`spread_filter.max_spread_pips`, `max_spread_to_atr_pct`). |
| Parameter range overlap with rejected campaigns | **acknowledged and explicitly addressed.** C5 reuses `atr_lookback = 14` and `atr_stop_multiple = 2.0` from CAMPAIGN_010 / CAMPAIGN_002 / CAMPAIGN_004 deliberately, so that the entry comparison is clean. These are not "tuned" values — they are the project's standard exit-sizing constants. The whole point of the random anchor is that the *only* variable is the entry signal; matching everything else is a feature. |
| Implicit per-pair tuning | clean — single parameter set across all 7 pairs (no per-pair overrides at all). |
| "Pick the best fold" | clean — the seed sequence is committed in the pre-commit *before* any backtest; the same seed produces the same trades, deterministically. |
| Rejection-criterion drift | clean — the gates inherited from CAMPAIGN_010's protocol are kept; C5 is *expected* to REJECT them. |
| Result-driven family selection | clean — C5 is selected from the protocol §4 whitelist on structural grounds (null model), not on its prospective backtest result. |

The protocol's distinct treatment of null models (§4: "Allowed
only as a diagnostic comparison anchor for the preferred
candidate") is structural protection against the tuning concern
— a strategy with no parameters can't be tuned.

The **random seed sequence** is the only "knob" on C5, and it is
fixed in the pre-commit per:

- one master seed (e.g. `RANDOM_SEED_MASTER = 20260523`),
- per-pair derived seeds (e.g. `seed_for(pair) = sha256(master + pair)`),
- 20 seed runs (same as CAMPAIGN_005) for statistical stability,
- committed to the pre-commit YAML before any backtest.

## 6. Compatibility checks

| requirement | status |
|---|:---:|
| compatible with current 7-pair H4 OANDA practice data | ✓ |
| compatible with the bespoke `BacktestEngine` (single-instrument, single-position) | ✓ |
| compatible with the walk-forward harness (`research/walk_forward/`) | ✓ |
| compatible with the financing overlay (`research/financing/`) | ✓ |
| compatible with the existing risk-engine `mode='backtest'` | ✓ |
| compatible with `parameter_mode = "frozen"` (only authorized mode) | ✓ |
| requires MODELED financing? | no |
| requires D1 aggregation? | no |
| requires engine paired-entry support? | no |
| requires new external dependency? | no |
| requires new broker / data fetch? | no |
| requires new credentials? | no |
| requires verifier extension before scaffold? | no — verifier extension is optional and reusable (see §11) |

C5 has **zero blockers**. It can be implemented under the
existing engine, evaluated under the existing harness, overlaid
under the existing financing calculator, and diagnosed under
the existing risk-engine — with no infrastructure work.

## 7. What makes the future scaffold sprint successful

The future `research-random-entry-diagnostic-anchor-001` scaffold
sprint is **successful** if and only if all of the following
hold at its tip commit:

1. **Strategy module** [`src/forex_bot/strategies/random_entry_anchor.py`](../../src/forex_bot/strategies/random_entry_anchor.py)
   implements the `Strategy` protocol with a deterministic-seed
   coin-flip entry and no broker imports. The seed is fed
   per-bar from `(master_seed, pair, bar_timestamp)` so the
   strategy is reproducible across runs.
2. **`StrategyConfig.random_entry_anchor`** sub-model added to
   [`src/forex_bot/config.py`](../../src/forex_bot/config.py)
   with the frozen seed-construction parameters + ATR-stop /
   time-stop parameters + the candidate's null-model flag.
3. **Tests** in
   [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py)
   pinning:
   - determinism (same seed → same signals → same trades),
   - 50 / 50 long-short distribution within statistical bounds
     for the configured seed,
   - no broker imports / no CAMPAIGN_002 / CAMPAIGN_010 key
     references (structural grep),
   - no-lookahead (signal at bar `t` depends only on
     `(master_seed, pair, t)` — not on `close[t]`, not on
     `close[t+1]`),
   - frozen-parameter validation (config rejects invalid seed
     types, invalid pair lists, etc.),
   - approval / safety regression (`approved_strategies.yaml`
     still empty, `random_entry_anchor` NOT in any active loop).
4. **Research config** [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml)
   loads via `load_settings(...)` with `trading_enabled=false`,
   `allow_order_submission=false`, `allow_live_trading=false`,
   the standard 7-pair H4 universe, and `risk.max_open_positions=1`.
5. **CAMPAIGN_011 pre-commit checklist**
   [`docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
   committed with the frozen parameters, the seed-sequence
   derivation, the gate vector (inherited from CAMPAIGN_010's
   pre-commit for clean comparability), and the verbatim
   declaration that this is a null model that **cannot be
   approved**.
6. **CAMPAIGN_011 status doc** [`docs/research/CAMPAIGN_011_STATUS.md`](docs/research/CAMPAIGN_011_STATUS.md)
   recording the candidate-scaffold-only status.
7. **Non-evidence smoke** confirms config-load PASS, unit suite
   PASS, walk-forward dry-run PASS.
8. **All standing safety checks** PASS at the sprint's tip:
   pytest, ruff, archive validator, freeze checker, secret
   scanner, loop-refusal checks, no live-loop, no broker call,
   no `.env` read.

## 8. What would immediately REJECT the candidate before implementation

The future scaffold sprint must abort if any of these become true:

- **Random is found to be tunable.** If any "seed selection" rule
  is motivated by prior campaign output or by C5's own pilot
  results, abort — that is parameter search disguised as seed
  selection.
- **Approval is requested.** If at any point in the scaffold
  sprint a request to add `random_entry_anchor` to
  `configs/approved_strategies.yaml` appears (even as a
  comment), abort — by design, C5 cannot be approved.
- **Paper / demo / live enablement is attempted.** Same — null
  model cannot run live.
- **Engine / financing / risk-policy code is modified.** C5's
  whole point is that the existing infrastructure validates a
  null model; modifying that infrastructure invalidates the
  validation.
- **The seed sequence is changed after seeing pilot trades.** The
  pre-commit fixes the seed sequence; any post-pilot change is
  pick-the-best-seed (a variant of pick-the-best-fold).
- **The universe is reduced "because some pairs are noisy".**
  Per the guardrails §3, universe is part of family identity;
  changing it is a different candidate.
- **The gates are loosened "because random isn't supposed to
  pass".** The gates are the same as CAMPAIGN_010's, and that is
  the point — the comparison must use identical gates.

## 9. Cooldown / re-attempt rule

If CAMPAIGN_011 (the future C5 implementation) is REJECTED by
the evidence sprint, **that is the expected outcome and is not a
failure of the sprint**. The diagnostic anchor's value is in the
gate vector it produces; the verdict classification (REJECT,
INCONCLUSIVE, etc.) is *the result*.

If CAMPAIGN_011 unexpectedly **passes** the pre-committed gates
(extremely unlikely under random entry on H4 majors with
spread + ATR-stop costs — CAMPAIGN_005 set the baseline at
−0.095 R per trade), the **expected response is to investigate
the seed / fold structure for accidental information leakage,
not to celebrate**:

- Confirm the seed sequence is genuinely uncorrelated with bar
  timestamp.
- Confirm no fold's bar set overlaps with the seed-derivation
  inputs.
- Treat a "passing" random anchor as a bug report against the
  pipeline, not as an edge.

Either outcome (REJECT or unexpected PASS) is informative; the
sprint design accommodates both.

## 10. C2 / C3 / C4 are NOT discarded

| candidate | status after this sprint | recommended subsequent sprint |
|---|---|---|
| C2 (carry overlay) | **deferred** — blocked on MODELED financing | `research-financing-modeled-capture-credentialed-001` to unblock, then revisit |
| C3 (regime switcher) | **deferred** — the strongest "real" candidate, but ranked second to C5 for the next sprint because (a) it carries the parameter-overlap soft warning and (b) the pipeline-validation value of C5 should come first | `research-new-candidate-strategy-discovery-003` (after CAMPAIGN_011 completes) — re-evaluate C3 against the now-6 rejected families (TF, VB, PB, MR, SB, plus the C5 null-model anchor that any candidate must structurally beat) |
| C4 (vol-expansion straddle) | **deferred** — blocked on engine paired-entry support | `infra-engine-paired-entry-support-001` to unblock, then revisit |

The selection of C5 is **not** the abandonment of the other
candidates. It is the **ordering decision** that says: validate
the pipeline first, then evaluate candidates that have a chance
of finding an edge.

## 11. Independent-verifier expectation (for C5)

The free / local verifier (`research/parity_verifier/`) is
capability-locked to CAMPAIGN_002 `trend_following 0.1.0` today.
For C5:

- **Extension is not required for the REJECT verdict.** Item 5
  of the six-evidence ladder (independent corroboration) is a
  paper-promotion gate, not a research-pass gate. C5 cannot be
  paper-promoted (null model), so item 5 is structurally not
  binding here.
- **Extension is uniquely valuable for C5.** Because C5 has zero
  tunable parameters, an independent re-implementation can be
  **exact** (not WARN-band). A future
  `infra-free-local-parity-verifier-random-entry-001` sprint
  could add C5 coverage to the verifier with low effort, and
  the resulting comparison would be deterministic
  (same seeds → same trades → same metrics).
- **The verifier extension is recommended as a follow-up**, not
  a precondition for CAMPAIGN_011. The CAMPAIGN_011 scaffold
  sprint should ship without verifier coverage; the future
  evidence sprint should ship without verifier coverage; a
  subsequent verifier sprint should add coverage and produce
  an exact-equivalence corroboration report.

## 12. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **Paper / demo / live remain blocked.**
- No strategy code edited this phase.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 13. Cross-links

- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)
  (Phase 2 scoring)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
  §7 (C5 specification in the prior shortlist)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §4 (null-model whitelist entry)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
  (anti-overfit guardrails)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
  (CAMPAIGN_010 cooldown rule)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
  (Phase 4 detailed design)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  (the gate vector C5 will inherit for clean comparability)
- [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)
  (the single-window precedent CAMPAIGN_011 strictly improves on)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)

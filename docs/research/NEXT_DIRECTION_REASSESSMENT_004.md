# Next-Direction Reassessment (Phase 3)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
`strategy_evidence: false`

Phase 3 reassessment for the discovery-004 sprint. Scores the
deferred candidates (C2 / C4) + infrastructure paths against the
**now-7 rejected baseline** (5 prior + CAMPAIGN_011 null +
CAMPAIGN_012 real) and recommends a single next path. **No
implementation; no backtest; no broker call.**

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_011 is the null baseline only, not a trading candidate.

## 1. Paths under reassessment

| id | path | type |
|---|---|---|
| **C2** | Carry-aware long-only AUD/NZD overlay | candidate |
| **C4** | Volatility-expansion paired straddle | candidate |
| **C6+** | New real candidate families (see Phase 4 for shortlist) | candidate |
| **infra-A** | `research-financing-modeled-capture-credentialed-001` (MODELED financing unblock for C2 and any future carry candidate) | infrastructure |
| **infra-B** | `infra-engine-paired-entry-support-001` (paired-entry engine support for C4 and any future paired/spread candidate) | infrastructure |
| **infra-C** | `infra-free-local-parity-verifier-<FAMILY>-NNN` (verifier extension for a future paper-promotion candidate) | infrastructure |
| **infra-D** | `infra-ruff-lean-parity-archive-cleanup-001` (clear 3 pre-existing ruff findings in `research/lean_parity/`) | infrastructure |

## 2. Scoring rubric

Each path is scored on the following 15 axes (qualitative; YES /
LIMITED / NO / N/A, with brief rationale).

| axis | what it measures |
|---|---|
| expected research value | how much would a positive or negative result move the project forward? |
| distinctness from CAMPAIGN_002 | structurally different signal family? |
| distinctness from CAMPAIGN_010 | structurally different signal family? |
| distinctness from CAMPAIGN_011 (null) | not a re-parameterized random-entry? |
| distinctness from CAMPAIGN_012 | structurally different signal family? |
| implementation complexity | small / medium / large LOC + scope |
| engine compatibility | bespoke engine supports this without modification? |
| data availability | local store + provenance ready? |
| walk-forward compatibility | inherits CAMPAIGN_010 / 011 / 012 plan structure? |
| financing dependency | requires ESTIMATED only, or needs MODELED? |
| MODELED-financing dependency | strict MODELED dependency (blocker) vs not |
| portfolio-risk implications | concurrent positions / pair concentration / new risk shape |
| independent-verifier extension feasibility | how hard to add to the existing CAMPAIGN_002-locked verifier? |
| overfitting risk | how easily could the family be re-fit to a winning fold? |
| current-infrastructure honest evaluation | can the candidate be evaluated **right now** with no infra change? |

## 3. Scoring table

| axis | **C2** carry overlay | **C4** vol-expansion straddle | **C6+** new families | **infra-A** financing | **infra-B** paired-entry | **infra-C** verifier ext | **infra-D** ruff cleanup |
|---|---|---|---|---|---|---|---|
| expected research value | HIGH (if MODELED unblocks) | HIGH (unique signal class) | MEDIUM-HIGH (depends on family) | HIGH (unblocks C2 + future carry) | MEDIUM (unblocks C4 only) | LOW today (no PASS candidate) | LOW (cosmetic) |
| distinctness from CAMPAIGN_002 | YES (carry, not momentum) | YES (vol-expansion, not trend) | YES (each family inherits the §3 "genuinely new" bar) | N/A (infra) | N/A | N/A | N/A |
| distinctness from CAMPAIGN_010 | YES (no session window dependency) | YES (event-driven, not session) | YES | N/A | N/A | N/A | N/A |
| distinctness from CAMPAIGN_011 (null) | YES (deterministic carry signal) | YES (deterministic event trigger) | YES (each requires its own determinism case) | N/A | N/A | N/A | N/A |
| distinctness from CAMPAIGN_012 | YES (no regime gate) | YES (paired structure, not single-leg trend) | YES (each must not be a C3 retune) | N/A | N/A | N/A | N/A |
| implementation complexity | medium (carry signal + financing) | LARGE (engine paired-entry + 2-leg position state) | varies (some families are small, others medium) | medium (financing capture script + fixture loader) | LARGE (engine paired-entry + risk + financing semantics) | medium (per-family adapter) | trivial (3 ruff fixes) |
| engine compatibility | **YES** (single-instrument long-only fits bespoke engine) | **NO** (engine lacks paired-entry / spread state) | varies (most fit if single-leg) | YES (infra; no engine change) | infra changes the engine | YES (verifier is isolated) | YES (engine untouched) |
| data availability | YES (H4 store covers majors + commodity pairs) | YES (H4 covers; calendar feed needed for events) | YES for most (H4 store; some need calendar/economic data) | depends on credentialed pilot success | YES (no new data) | YES (no new data) | YES |
| walk-forward compatibility | YES (inherits 8-fold rolling/frozen) | LIMITED (paired entries need 2-leg fold semantics) | YES for most | YES (financing is overlay) | LIMITED (engine change ripples) | YES | YES |
| financing dependency | **MODELED required for live**; ESTIMATED OK for research-only | ESTIMATED OK (vol-expansion holds < 1 day typically) | varies | YES (this IS the unblock) | ESTIMATED unchanged | none | none |
| MODELED-financing dependency | **BLOCKER for live promotion** | not strict | varies | unblocks | none | none | none |
| portfolio-risk implications | new: long-only single-direction; carry concentration | new: 2-leg correlated; basket-style risk | varies | none | new: paired-position semantics | none | none |
| verifier extension feasibility | medium (re-implement carry calc) | HIGH effort (re-implement 2-leg + correlation) | varies | N/A | enables future verifier work for paired candidates | enabling | N/A |
| overfitting risk | LOW-MEDIUM (frozen carry rates + simple long-only) | MEDIUM (event-window selection bias) | varies | N/A | N/A | N/A | N/A |
| current-infrastructure honest evaluation | **NO** without MODELED unblock | **NO** without paired-entry support | **YES for most** new families | YES (infra is what makes it honest) | YES (infra is what makes it honest) | YES (verifier is post-evidence) | YES |

## 4. Per-path analysis

### 4.1 C2 — Carry-aware long-only AUD/NZD overlay

| dimension | finding |
|---|---|
| status | **DEFERRED** (already in [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md)); blocker unchanged |
| primary blocker | **MODELED financing refused at 4 layers** in `src/forex_bot/financing.py`; ESTIMATED is fine for *research evidence* but the live-promotion blocker stands |
| if evaluated under ESTIMATED only | the carry signal is meaningful for *research-only* edge detection, but the verdict cannot lead to paper / demo / live promotion because the live-promotion financing gate would fail |
| recommendation | **DEFER** until `research-financing-modeled-capture-credentialed-001` (infra-A) runs and lifts MODELED |
| alternative | could be evaluated as `RESEARCH_PASS_UNAPPROVED` even without MODELED, but the binding null-baseline comparison gate is informationally limited because the financing component cannot be properly stressed |

### 4.2 C4 — Volatility-expansion paired straddle

| dimension | finding |
|---|---|
| status | **DEFERRED** (already in discovery-003 reassessment); blocker unchanged |
| primary blocker | **engine lacks paired-entry support** — single-instrument single-position invariant in `BacktestEngine` and `RiskEngine` |
| effort to unblock | LARGE — paired-entry support is a multi-week engine change (2-leg position state, correlated risk sizing, paired exit logic, engine PnL reconciliation, walk-forward fold semantics for 2-leg positions) |
| if engine supported it | C4 would be a genuinely new signal class (vol-expansion event window, paired-position structure) |
| recommendation | **DEFER** unless someone is willing to scope `infra-engine-paired-entry-support-001` (infra-B) as a multi-sprint effort |

### 4.3 C6+ — New real candidate families

| dimension | finding |
|---|---|
| status | **ACTIVE OPTION** for this sprint's Phase 4 |
| primary requirement | each proposal must pass the [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) §3 "genuinely new" criteria |
| examples allowed by the addendum | cross-pair currency-strength rotation; options-event-window long-vol proxy (calendar-data dependent); simple market-state classifier using already-available H4 features (if no full-sample leakage); volatility contraction/expansion filter not requiring paired entries |
| examples disallowed | regime-switcher variants; C3 retunes; C2 without MODELED unblock; C4 without paired-entry engine; mean-reversion variants (already REJECTED via CAMPAIGN_008/009) |
| recommendation | **VIABLE** — Phase 4 will propose a shortlist; Phase 5 picks one |

### 4.4 infra-A — `research-financing-modeled-capture-credentialed-001`

| dimension | finding |
|---|---|
| scope | a credentialed pilot to capture real OANDA `DAILY_FINANCING` events under a separately-authorized broker account; populate MODELED fixture set; lift the 4-layer refusal in `src/forex_bot/financing.py` after fixtures match observed events within a documented tolerance |
| safety risks | **HIGH** — requires live broker credentials (not allowed by default project rules); requires `account/transaction` endpoint queries (forbidden by this sprint's safety rules); requires explicit human authorization separate from any Claude Code sprint |
| current-sprint authorization | this discovery-004 sprint **cannot** authorize or run infra-A; it can only recommend it |
| value | unlocks C2 (carry overlay) for live promotion + future carry candidates; **does not by itself produce strategy evidence** |
| recommendation | **HOLD** for human authorization; not a sprint Claude Code should start unilaterally |

### 4.5 infra-B — `infra-engine-paired-entry-support-001`

| dimension | finding |
|---|---|
| scope | extend `BacktestEngine` + `RiskEngine` + walk-forward harness + financing semantics to support 2-leg paired positions with single trade entity ("straddle", "spread", etc.); update fold semantics; update PnL reconciliation; update CSV + summary writers; add tests |
| effort | **LARGE** (multi-sprint; touches the most safety-critical part of the engine) |
| safety risks | medium — touches engine PnL paths; requires extensive tests to ensure single-leg behaviour is unchanged for CAMPAIGN_002 / 010 / 011 / 012 historical evidence |
| value | unlocks C4 (vol-expansion straddle) and any future paired/spread candidate |
| current-sprint authorization | recommendable; large scope means it would be 4-6 sprints of its own |
| recommendation | **HOLD** unless a paired-position candidate has clear independent hypothesis support (C4 alone is not sufficient justification for the engine-rewrite scope) |

### 4.6 infra-C — `infra-free-local-parity-verifier-<FAMILY>-NNN`

| dimension | finding |
|---|---|
| scope | per-family verifier extension to corroborate a future paper-promotion candidate |
| current need | **none today** — no candidate has reached `RESEARCH_PASS_UNAPPROVED`; CAMPAIGN_012's REJECT does not need verifier corroboration |
| value | item 5 of the six-evidence ladder — required only if a candidate passes walk-forward + financing + risk |
| recommendation | **DEFER until a candidate reaches RESEARCH_PASS_UNAPPROVED** |

### 4.7 infra-D — `infra-ruff-lean-parity-archive-cleanup-001`

| dimension | finding |
|---|---|
| scope | resolve the 3 pre-existing ruff findings in `research/lean_parity/algorithms/` (2× RUF100 + 1× I001) |
| value | cosmetic; the LEAN-parity archive is frozen historical evidence and not in any test path |
| effort | trivial (small sprint) |
| safety risks | none |
| does it block anything? | **NO** — the validators all pass with these 3 findings; the freeze gate ignores them |
| recommendation | **VERY LOW PRIORITY** — should not displace a candidate-discovery or higher-value infra path |

## 5. Candidate vs infrastructure comparison

| comparison | finding |
|---|---|
| C2 vs infra-A | C2 cannot be evaluated honestly for live without infra-A; infra-A is a credentialed pilot outside this sprint's authority. C2 is essentially **gated by infra-A**. |
| C4 vs infra-B | C4 cannot be evaluated at all without infra-B; infra-B is a multi-sprint engine rewrite. C4 is **gated by infra-B**. |
| C6+ vs all infra | C6+ candidates that fit the bespoke engine + ESTIMATED financing can be evaluated honestly **today** with no infrastructure change. **infra is unnecessary for most C6+ paths**. |
| infra-A vs infra-B vs infra-C vs infra-D | infra-C and infra-D are not urgent (no candidate needs them today). infra-A and infra-B both require human authorization the discovery-004 sprint cannot grant. |

**The clear comparison conclusion:** if a viable C6+ family can be
identified, it is the highest-value, lowest-risk next step. The
infrastructure paths are valuable but require either human
authorization (infra-A) or significant engine work (infra-B) before
they pay off, and infra-C / infra-D are not blocking anything today.

## 6. Blockers (binding)

| blocker | impact | unblock path |
|---|---|---|
| MODELED financing refused at 4 layers | C2 + any future carry-only family | infra-A (credentialed pilot; separately authorized; **out of scope for this sprint**) |
| engine lacks paired-entry support | C4 + any future paired/spread family | infra-B (engine rewrite; multi-sprint; **out of scope for this sprint**) |
| verifier capability-locked to CAMPAIGN_002 | item 5 of six-evidence ladder for any non-`trend_following` paper-promotion candidate | infra-C per-family (**not blocking today**) |
| 3 pre-existing ruff findings in `research/lean_parity/algorithms/` | cosmetic only | infra-D (low priority) |
| CAMPAIGN_002 / 010 / 011 / 012 rejected-family lineages | shrinks the legitimate proposal surface | (none — codified in §1 of guardrails addendum) |

## 7. Recommendation

**RECOMMENDED PATH: discovery-driven C6+ family selection.**

- Phase 4 will produce a shortlist of 3–5 genuinely-new candidate
  families (per the [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
  §3 criteria).
- Phase 5 will select exactly one.
- Phase 6 will design the selected candidate.
- Phase 7 will write the scaffold + evidence branch specs.

**Why this is preferred over infrastructure paths:**

1. **C6+ can be evaluated honestly today** with no engine or
   financing-source change.
2. **infra-A requires human authorization** (credentialed pilot
   touching account/transaction endpoints — Claude Code cannot
   start this).
3. **infra-B requires large engine work** (multi-sprint scope) that
   only pays off for C4 alone today; not worth committing to until a
   paired-position candidate has independent hypothesis support
   beyond C4's specific design.
4. **infra-C is post-PASS** — no candidate has passed; infra-C cannot
   be useful until one does.
5. **infra-D is cosmetic** — does not unblock anything.

**Fallback (if Phase 4 cannot produce a viable C6+ candidate):**

- Recommend infra-A (`research-financing-modeled-capture-credentialed-001`)
  as the next sprint, acknowledging it requires human authorization
  before it can begin.
- Document infra-B as the post-MODELED secondary path.

**Phase 5 will resolve which option (C6+ candidate vs infra-A
fallback) is selected.**

## 8. Rationale for deferring non-selected paths

| path | deferral reason |
|---|---|
| **C2 carry overlay** | gated by infra-A; even research-only evaluation under ESTIMATED produces only `RESEARCH_PASS_UNAPPROVED` that cannot reach paper; until infra-A runs, the work has limited value |
| **C4 vol-expansion straddle** | gated by infra-B (multi-sprint engine rewrite); not worth the engine scope until paired-position has additional independent justification |
| **infra-A** | requires human authorization (credentialed broker account; account/transaction endpoint queries); discovery-004 cannot start it; recommended only if Phase 4 fails |
| **infra-B** | very large scope; only one candidate (C4) currently justifies it; defer until a clearer multi-candidate need emerges |
| **infra-C** | no candidate has reached `RESEARCH_PASS_UNAPPROVED`; verifier extension is post-PASS by design |
| **infra-D** | cosmetic; does not block any validation or any candidate evaluation |

## 9. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 818 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## 10. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md) (Phase 0)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) (Phase 1)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (Phase 2)
- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md) (predecessor C2 / C3 / C4 scoring)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md) (Phase 4 — to be written)
- [`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md) (Phase 5 — to be written)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

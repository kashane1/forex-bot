# Next-Direction Reassessment (Phase 4)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
`strategy_evidence: false`

Phase 4 reassessment for the discovery-005 sprint. Scores the
deferred candidates (C2 / C4 / C7 / C8 / C9 from discovery-004) +
infrastructure paths against the **now-8 rejected baseline** (5 prior
+ CAMPAIGN_011 null + CAMPAIGN_012 real + CAMPAIGN_013 real) and the
**new binding turnover-amplification anti-pattern** (Patterns M–Q +
R–W), and recommends a single next path. **No implementation; no
backtest; no broker call.**

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 all
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. CAMPAIGN_011 is the null baseline only, not a
> trading candidate.

## 1. Paths under reassessment

| id | path | type | source |
|---|---|---|---|
| **C2** | Carry-aware long-only AUD/NZD overlay | candidate | reaffirmed deferred from discovery-002/003/004 |
| **C4** | Volatility-expansion paired straddle | candidate | reaffirmed deferred from discovery-002/003/004 |
| **C6** | Cross-pair currency strength rotation | candidate | **REJECTED in CAMPAIGN_013** — out of scope; cooldown binding (Phase 1) |
| **C7** | Calendar-Event Window Anomaly (CEWA) | candidate | from discovery-004 shortlist |
| **C8** | Multi-Window Volatility-Compression Breakout (MWVCB) | candidate | from discovery-004 shortlist |
| **C9** | Time-of-Day Cost-Adjusted Mean Reversion on Spreads (TODCAMRS) | candidate | from discovery-004 shortlist (distinctness 5/6) |
| **C10+** | New genuinely-new families (Phase 5 will shortlist) | candidate | this sprint |
| **infra-A** | `research-financing-modeled-capture-credentialed-001` (MODELED financing unblock) | infrastructure | reaffirmed |
| **infra-B** | `infra-engine-paired-entry-support-001` (paired-entry engine support) | infrastructure | reaffirmed |
| **infra-C** | `infra-free-local-parity-verifier-<FAMILY>-NNN` (verifier extension per family) | infrastructure | reaffirmed |
| **infra-D** | `infra-ruff-lean-parity-archive-cleanup-001` (3 pre-existing findings) | infrastructure | reaffirmed |

Note: **C6 is excluded from candidate reassessment** because CAMPAIGN_013
ran it to REJECT; per the Phase 1 closeout, C6 is in binding cooldown
for at least 3 discovery sprints. It appears in the table only as
historical rejected evidence.

## 2. Scoring rubric

Each path is scored on the following 18 axes (qualitative; YES /
LIMITED / NO / N/A, with brief rationale). Axes 1–15 are inherited
from discovery-004's Phase 3; axes 16–18 are new for discovery-005.

| axis | what it measures |
|---|---|
| 1. expected research value | how much would a positive or negative result move the project forward? |
| 2. distinctness from CAMPAIGN_002 | structurally different signal family? |
| 3. distinctness from CAMPAIGN_010 | structurally different signal family? |
| 4. distinctness from CAMPAIGN_011 (null) | not a re-parameterized random-entry? |
| 5. distinctness from CAMPAIGN_012 | structurally different signal family? |
| **6. distinctness from CAMPAIGN_013** | **structurally different signal family from cross-pair rotator?** |
| 7. implementation complexity | small / medium / large LOC + scope |
| 8. engine compatibility | bespoke engine supports this without modification? |
| 9. data availability | local store + provenance ready? |
| 10. walk-forward compatibility | inherits CAMPAIGN_010 / 011 / 012 / 013 plan structure? |
| 11. financing dependency | requires ESTIMATED only, or needs MODELED? |
| 12. MODELED-financing dependency | strict MODELED dependency (blocker) vs not |
| 13. portfolio-risk implications | concurrent positions / pair concentration / new risk shape |
| 14. independent-verifier extension feasibility | how hard to add to the existing CAMPAIGN_002-locked verifier? |
| 15. overfitting risk | how easily could the family be re-fit to a winning fold? |
| 16. **turnover profile** | **expected trade count vs CAMPAIGN_011 null floor (1,177)** |
| 17. **explicit cost-awareness** | **does the proposal include a per-trade cost section per Pattern Q?** |
| 18. current-infrastructure honest evaluation | can the candidate be evaluated **right now** with no infra change? |

## 3. Scoring table

| axis | **C2** carry overlay | **C4** straddle | **C7** CEWA | **C8** MWVCB | **C9** TODCAMRS | **C10+** new families | **infra-A** financing | **infra-B** paired-entry | **infra-C** verifier ext | **infra-D** ruff cleanup |
|---|---|---|---|---|---|---|---|---|---|---|
| 1. research value | HIGH (if MODELED unblocks) | HIGH (unique signal class) | HIGH (calendar fixture is reusable) | MEDIUM (close to C4 lineage) | MEDIUM (close to CAMPAIGN_008/009) | MEDIUM-HIGH (depends on family) | HIGH (unblocks C2 + future carry) | MEDIUM (unblocks C4 only) | LOW today (no PASS candidate) | LOW (cosmetic) |
| 2. dist. CAMPAIGN_002 | YES (carry, not momentum) | YES (vol-expansion) | YES (event-conditional, not trend) | YES (vol-compression breakout) | YES (counter-trend) | YES (per §3 criteria) | N/A | N/A | N/A | N/A |
| 3. dist. CAMPAIGN_010 | YES (no session window) | YES (event, not session) | YES (event windows ≠ session windows) | YES (no Asian-range trigger) | YES (no breakout direction) | YES | N/A | N/A | N/A | N/A |
| 4. dist. CAMPAIGN_011 | YES (deterministic carry) | YES (deterministic event trigger) | YES (deterministic event trigger) | YES (deterministic vol-comp signal) | YES (deterministic spread+close trigger) | YES (each requires determinism case) | N/A | N/A | N/A | N/A |
| 5. dist. CAMPAIGN_012 | YES (no regime gate) | YES (paired, not single-leg trend) | YES (event-conditional, not regime-gated trend) | LIMITED (vol-state-conditional; needs careful Phase 6 vs Pattern J) | YES (no vol-percentile gate) | YES (each must not be C3 retune) | N/A | N/A | N/A | N/A |
| **6. dist. CAMPAIGN_013** | **YES (carry-ranked, not log-return-ranked; if no cross-sectional structural component the distinctness is clean)** | **YES (paired structure, no cross-sectional rank)** | **YES (event-window-conditional; no cross-pair ranking)** | **YES (vol-state-conditional, not cross-sectional rank)** | **YES (single-pair counter-trend on spread artifact, not cross-pair direction)** | **YES (each must not be C6 retune; Patterns R–W bind)** | N/A | N/A | N/A | N/A |
| 7. complexity | medium | LARGE | MEDIUM-HIGH | MEDIUM | MEDIUM | varies | medium | LARGE | medium | trivial |
| 8. engine compat | YES (single-leg long-only) | NO (engine lacks paired-entry) | YES (single-leg, reads event fixture) | YES (single-leg, reads D1AGG + H4) | YES (single-leg single-instrument) | varies (most fit single-leg) | YES (infra; no engine change) | infra changes the engine | YES (verifier isolated) | YES (engine untouched) |
| 9. data availability | YES (H4 store covers majors) | YES (H4 + calendar needed for events) | YES (H4 + NEW calendar fixture) | YES (H4 + existing D1AGG aggregator) | YES (H4 with spreads in store) | YES for most | depends on credentialed pilot | YES (no new data) | YES (no new data) | YES |
| 10. walk-forward compat | YES (inherits 8-fold) | LIMITED (paired entries need 2-leg fold semantics) | YES (event fixture available per fold) | YES (inherits 8-fold) | YES (inherits 8-fold) | YES for most | YES (financing overlay) | LIMITED (engine change ripples) | YES | YES |
| 11. financing dep | MODELED req'd for live; ESTIMATED OK for research | ESTIMATED OK (short hold) | ESTIMATED OK (short hold) | ESTIMATED OK | ESTIMATED OK (very short hold) | varies | YES (this IS the unblock) | ESTIMATED unchanged | none | none |
| 12. MODELED-fin dep | **BLOCKER for live promotion** | not strict | not strict | not strict | not strict | varies | unblocks | none | none | none |
| 13. portfolio-risk | new: carry concentration | new: 2-leg correlated | new: event-window clustering | new: vol-compression clustering | new: spread-time-of-day clustering | varies | none | new: paired-position semantics | none | none |
| 14. verifier ext feas | medium | HIGH | medium-high (event fixture replay) | medium | medium | varies | N/A | enables future verifier for paired | enabling | N/A |
| 15. overfit risk | LOW-MEDIUM | MEDIUM | MEDIUM (event-set selection bias) | MEDIUM (close to CAMPAIGN_004) | MEDIUM (close to CAMPAIGN_008/009) | varies | N/A | N/A | N/A | N/A |
| **16. turnover profile** | **LOW (carry trade hold ≥ multi-day; expected ~200-600 trades/4y)** | **LOW (vol-event; expected ~200-800 trades/4y)** | **LOW (event windows finite per year; expected ~150-400 trades/4y)** | **MEDIUM-LOW (vol-compression hits are sparse; expected ~400-1,200 trades/4y)** | **MEDIUM (spread bucket per H4; expected ~800-2,500 trades/4y; possibly more)** | **varies (per family hypothesis; Pattern M ceiling binds)** | N/A | N/A | N/A | N/A |
| **17. cost-awareness** | **YES (carry IS the cost-driven thesis)** | **YES (vol-expansion has small holding; cost-section trivial)** | **YES (short hold, finite event set)** | **YES (vol-compression filter implies finite firings)** | **MEDIUM (very short hold → slippage modeling sensitivity)** | **MUST INCLUDE per Pattern Q** | N/A | N/A | N/A | N/A |
| 18. infra-honest eval | **NO** w/o MODELED | **NO** w/o paired-entry | YES (calendar fixture is one-time small commit) | YES | YES | YES for most | YES (infra is the unblock) | YES (infra is the unblock) | YES (verifier is post-evidence) | YES |

## 4. Per-path analysis

### 4.1 C2 — Carry-aware long-only AUD/NZD overlay

| dimension | finding |
|---|---|
| status | **DEFERRED** (unchanged from discovery-002/003/004); blocker unchanged |
| primary blocker | **MODELED financing refused at 4 layers** in `src/forex_bot/financing.py`; ESTIMATED is fine for *research evidence* but the live-promotion blocker stands |
| CAMPAIGN_013 impact | C2 is structurally distant from CAMPAIGN_013 (different mechanism: carry vs cross-pair rank); the CAMPAIGN_013 REJECT does not change C2's deferral status |
| turnover profile | LOW — multi-day-to-multi-week carry positions; ~200-600 trades over 4 years; well below the null floor |
| cost section | the **cost IS the thesis** (carry differential as edge after spread/slippage); trivially passes Pattern Q |
| if evaluated under ESTIMATED only | the carry signal is meaningful for *research-only* edge detection, but the verdict cannot lead to paper / demo / live promotion because the live-promotion financing gate would fail |
| recommendation | **DEFER** until `research-financing-modeled-capture-credentialed-001` (infra-A) runs and lifts MODELED |

### 4.2 C4 — Volatility-expansion paired straddle

| dimension | finding |
|---|---|
| status | **DEFERRED** (unchanged from discovery-003/004); blocker unchanged |
| primary blocker | **engine lacks paired-entry support** — single-instrument single-position invariant in `BacktestEngine` and `RiskEngine` |
| CAMPAIGN_013 impact | C4 is structurally distant from CAMPAIGN_013 (paired structure, not cross-pair rank; vol-driven, not log-return ranked); the CAMPAIGN_013 REJECT does not change C4's deferral status. CAMPAIGN_013 *did* exercise multi-pair orchestration patterns at the runner layer, which is *adjacent* to but not identical with the paired-entry engine support C4 needs |
| turnover profile | LOW — vol-expansion events are sparse; ~200-800 trades over 4 years |
| cost section | straddle structure has explicit per-leg cost handling; trivially passes Pattern Q |
| effort to unblock | LARGE — paired-entry support is a multi-sprint engine change (2-leg position state, correlated risk sizing, paired exit logic, engine PnL reconciliation, walk-forward fold semantics) |
| recommendation | **DEFER** unless someone is willing to scope `infra-engine-paired-entry-support-001` (infra-B) as a multi-sprint effort |

### 4.3 C7 — Calendar-Event Window Anomaly (CEWA)

| dimension | finding |
|---|---|
| status | **ACTIVE; PROMOTED to lead candidate** (was discovery-004 fallback) |
| CAMPAIGN_013 impact | C7's structural distinctness from CAMPAIGN_013 is **strong** — event-window-conditional counter-trend is mechanistically unrelated to cross-pair currency-strength rotation. C6's REJECT (and the turnover-amplification slope) **strengthens** the case for C7's low-turnover finite-event-set design |
| turnover profile | **LOW** — event windows are finite per year (~30-60 high-impact USD events: NFP monthly, FOMC ~8/year, ECB ~8/year, BoJ + BoE + key NFP-revisions); expected ~150-400 trades over 4 years across 7 pairs (well below CAMPAIGN_011's 1,177 null floor); **explicitly disqualifies Pattern M and Pattern V** |
| cost section | event windows have short hold (2-6 H4 bars); spread + slippage are the dominant per-trade cost; financing is small (< 1 day typically); trivially passes Pattern Q |
| primary requirement | new committed calendar fixture (JSON / CSV of historical event timestamps from public sources: BLS for NFP, FOMC.gov for FOMC, ECB.europa.eu for ECB, BoJ.or.jp for BoJ, BoE for BoE); ~10 KB; no broker call; no real-time fetch; deterministic |
| no-lookahead | event-window access must use only `event_time <= bar_complete_time` semantics; this is a new no-lookahead invariant for the scaffold sprint |
| scaffold complexity | MEDIUM-HIGH — strategy module ~350 LOC; event-calendar loader; ≥ 30 unit tests; fixture file ~10 KB; new no-lookahead invariants for event-time access |
| recommendation | **VIABLE; LEAD CANDIDATE** for Phase 5 / 6 |

### 4.4 C8 — Multi-Window Volatility-Compression Breakout (MWVCB)

| dimension | finding |
|---|---|
| status | **VIABLE with elevated proximity-risk; Phase 5 should weigh** |
| CAMPAIGN_013 impact | C8 is structurally distant from CAMPAIGN_013 (vol-state-conditional, not cross-pair-rank); CAMPAIGN_013 REJECT does not directly impact C8 |
| **CAMPAIGN_004 / CAMPAIGN_012 proximity** | C8 sits next to CAMPAIGN_004 (vol-breakout, REJECTED) AND adjacent to CAMPAIGN_012's "trade conditional on vol-percentile regime" (REJECTED) — needs careful Phase 6 justification |
| turnover profile | MEDIUM-LOW — cross-timeframe AND-gate is restrictive; expected ~400-1,200 trades over 4 years |
| cost section | vol-compression triggers + breakout-direction exits: per-trade cost section is straightforward |
| **discovery-005-specific risk** | C8's "trade after vol-compression breakout" mechanism is in the direction-trading family that turnover-amplification slope speaks to (CAMPAIGN_002/010/012/013 all directional); Phase 6 must explicitly justify why C8's compression-then-break direction is not the same falsified directional signal as CAMPAIGN_002/010/012 |
| recommendation | **MEDIUM** — viable but Phase 6 defense burden is higher post-CAMPAIGN_013 |

### 4.5 C9 — Time-of-Day Cost-Adjusted Mean Reversion on Spreads (TODCAMRS)

| dimension | finding |
|---|---|
| status | **VIABLE with elevated proximity-risk; weakest of shortlist** |
| CAMPAIGN_013 impact | C9 is structurally distant from CAMPAIGN_013 (single-pair counter-trend on spread artifact, not cross-pair rank); CAMPAIGN_013 REJECT does not directly impact C9 |
| **CAMPAIGN_008/009 proximity** | C9 sits next to CAMPAIGN_008/009 (mean-reversion, REJECTED) — *direction* (counter-trend) is the same; only the *trigger* (spread-time-of-day) differs. Distinctness 5/6 (weakest of shortlist) |
| turnover profile | MEDIUM — spread bucket per H4 bar; expected ~800-2,500 trades over 4 years (closer to CAMPAIGN_011 null floor; possibly above) |
| cost section | very short hold (1-2 H4 bars) means slippage modeling is critical; the existing `FillModel` must be defended; per-trade cost is a meaningful fraction of expected per-trade move |
| **discovery-005-specific risk** | The C9 mechanism *is* a cost-aware thesis ("spread-time-of-day artifact"), but the short hold + medium turnover are vulnerable to the very pattern (slippage modeling errors compounding cost) that turnover amplification surfaces. Pattern Q burden is high |
| recommendation | **MEDIUM-LOW** — viable but Phase 6 defense burden is highest; consider deferring to discovery-006 unless Phase 5 cannot find a stronger candidate |

### 4.6 C10+ — New genuinely-new families

| dimension | finding |
|---|---|
| status | **ACTIVE OPTION** for this sprint's Phase 5 |
| primary requirement | each proposal must pass the [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) §3 "genuinely new" criteria (11 axes including turnover budget + cost section) |
| examples allowed by the addendum | low-frequency weekly/daily bias with H4 execution; structure-based basket exposure filter (if no paired-entry needed); fundamental-event-conditional candidates with calendar fixture |
| examples disallowed | cross-pair rank variants; C3 retunes; C2 without MODELED unblock; C4 without paired-entry engine; mean-reversion variants; trend-following variants; session-breakout variants; pullback variants; vol-breakout variants; high-turnover firehose entries |
| recommendation | **VIABLE** — Phase 5 will propose a shortlist; Phase 6 picks one |

### 4.7 infra-A — `research-financing-modeled-capture-credentialed-001`

| dimension | finding |
|---|---|
| scope | a credentialed pilot to capture real OANDA `DAILY_FINANCING` events under a separately-authorized broker account; populate MODELED fixture set; lift the 4-layer refusal in `src/forex_bot/financing.py` after fixtures match observed events within a documented tolerance |
| safety risks | **HIGH** — requires live broker credentials (not allowed by default project rules); requires `account/transaction` endpoint queries (forbidden by this sprint's safety rules); requires explicit human authorization separate from any Claude Code sprint |
| CAMPAIGN_013 impact | unchanged — infra-A is a financing-source unblock; CAMPAIGN_013's REJECT does not affect its scope or priority |
| current-sprint authorization | this discovery-005 sprint **cannot** authorize or run infra-A; it can only recommend it |
| value | unlocks C2 (carry overlay) for live promotion + future carry candidates; **does not by itself produce strategy evidence** |
| recommendation | **HOLD** for human authorization; not a sprint Claude Code should start unilaterally |

### 4.8 infra-B — `infra-engine-paired-entry-support-001`

| dimension | finding |
|---|---|
| scope | extend `BacktestEngine` + `RiskEngine` + walk-forward harness + financing semantics to support 2-leg paired positions with single trade entity ("straddle", "spread", etc.); update fold semantics; update PnL reconciliation; update CSV + summary writers; add tests |
| effort | **LARGE** (multi-sprint; touches the most safety-critical part of the engine) |
| CAMPAIGN_013 impact | CAMPAIGN_013 *did* successfully implement multi-pair orchestration at the runner layer (cross-pair runner integration contract satisfied on all 8 folds); this is adjacent to but not identical with paired-entry engine support. infra-B remains separately scoped |
| safety risks | medium — touches engine PnL paths; requires extensive tests to ensure single-leg behaviour is unchanged for CAMPAIGN_002 / 010 / 011 / 012 / 013 historical evidence |
| value | unlocks C4 (vol-expansion straddle) and any future paired/spread candidate |
| recommendation | **HOLD** unless a paired-position candidate has clear independent hypothesis support |

### 4.9 infra-C — `infra-free-local-parity-verifier-<FAMILY>-NNN`

| dimension | finding |
|---|---|
| scope | per-family verifier extension to corroborate a future paper-promotion candidate |
| CAMPAIGN_013 impact | CAMPAIGN_013 was REJECT; its verifier extension is **deferred indefinitely** (would be larger than CAMPAIGN_012's extension due to cross-pair runner contract re-implementation; not warranted for a REJECT verdict) |
| current need | **none today** — no candidate has reached `RESEARCH_PASS_UNAPPROVED`; CAMPAIGN_013's REJECT does not need verifier corroboration |
| value | item 5 of the six-evidence ladder — required only if a candidate passes walk-forward + financing + risk |
| recommendation | **DEFER until a candidate reaches RESEARCH_PASS_UNAPPROVED** |

### 4.10 infra-D — `infra-ruff-lean-parity-archive-cleanup-001`

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
| C2 vs infra-A | C2 cannot be evaluated honestly for live without infra-A; infra-A is a credentialed pilot outside this sprint's authority. C2 is essentially **gated by infra-A** |
| C4 vs infra-B | C4 cannot be evaluated at all without infra-B; infra-B is a multi-sprint engine rewrite. C4 is **gated by infra-B** |
| C7 vs all infra | C7 introduces a *small new data dependency* (calendar fixture, one-time committed JSON / CSV) but otherwise fits the bespoke engine + ESTIMATED financing today. Distinct from all 8 rejected families |
| C8 vs all infra | C8 fits engine + data + ESTIMATED financing today, but has elevated CAMPAIGN_004/012 proximity risk |
| C9 vs all infra | C9 fits engine + data + ESTIMATED financing today, but has CAMPAIGN_008/009 proximity risk + Pattern Q burden |
| C10+ vs all infra | depends on family; most candidates that fit the bespoke engine + ESTIMATED financing can be evaluated honestly today |
| infra-A vs infra-B vs infra-C vs infra-D | infra-C and infra-D are not urgent; infra-A and infra-B require human authorization the discovery-005 sprint cannot grant |

**The clear comparison conclusion:** if a viable C10+ family or
a viable C7 can be identified, it is the highest-value, lowest-risk
next step. The infrastructure paths are valuable but require either
human authorization (infra-A) or significant engine work (infra-B)
before they pay off, and infra-C / infra-D are not blocking
anything today.

## 6. Blockers (binding)

| blocker | impact | unblock path |
|---|---|---|
| MODELED financing refused at 4 layers | C2 + any future carry-only family | infra-A (credentialed pilot; separately authorized; **out of scope for this sprint**) |
| engine lacks paired-entry support | C4 + any future paired/spread family | infra-B (engine rewrite; multi-sprint; **out of scope for this sprint**) |
| verifier capability-locked to CAMPAIGN_002 | item 5 of six-evidence ladder for any non-`trend_following` paper-promotion candidate | infra-C per-family (**not blocking today**) |
| 3 pre-existing ruff findings in `research/lean_parity/algorithms/` | cosmetic only | infra-D (low priority) |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 rejected-family lineages | shrinks the legitimate proposal surface | (none — codified in §1 of guardrails 005 addendum) |
| turnover-amplification anti-pattern (Patterns M–Q) | binds future candidates' turnover budget | (none — codified in `TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`) |
| cross-pair-rotation cooldown (CAMPAIGN_013 closeout) | C6 / cross-sectional FX-rank variants out of scope for ≥ 3 discovery sprints | (none — codified in `CAMPAIGN_013_REJECTION_CLOSEOUT.md` §5) |

## 7. Recommendation

**RECOMMENDED PATH: a new candidate sprint, with C7 (CEWA) as the
lead recommendation and C10+ shortlist exploration in Phase 5.**

- Phase 5 will produce a shortlist of 3–5 genuinely-new candidate
  families (per the [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md)
  §3 criteria), with C7 included.
- Phase 6 will select exactly one.
- Phase 7 will design the selected candidate.
- Phase 8 will write the scaffold + evidence branch specs.

**Why this is preferred over infrastructure paths:**

1. **C7 / C10+ can be evaluated honestly today** with at most a small
   one-time calendar-fixture commit (C7) or no new dependency at all
   (most C10+).
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

**Why C7 over C8 / C9:**

- C7 is structurally furthest from all 8 rejected families
  (event-window-conditional is mechanistically novel for this repo).
- C7 has the **lowest turnover profile** (event windows are finite
  per year; ~150-400 trades expected vs CAMPAIGN_011's 1,177 null
  floor) — explicitly disqualifies Patterns M and V.
- C7's small new data dependency (calendar fixture) is **bounded,
  one-time, deterministic, and broker-free** — much smaller risk
  surface than infra-A or infra-B.
- C7's defense against turnover-amplification is **structural** (the
  event set itself is finite), not parameter-tuned.

**Fallback (if Phase 5 cannot produce a viable C7 or C10+ candidate):**

- Recommend infra-A (`research-financing-modeled-capture-credentialed-001`)
  as the next sprint, acknowledging it requires human authorization
  before it can begin.
- Document infra-B as the post-MODELED secondary path.

**Phase 6 will resolve which option (C7 / C10+ vs infra-A fallback)
is selected.**

## 8. Rationale for deferring non-selected paths

| path | deferral reason |
|---|---|
| **C2 carry overlay** | gated by infra-A; even research-only evaluation under ESTIMATED produces only `RESEARCH_PASS_UNAPPROVED` that cannot reach paper; until infra-A runs, the work has limited value |
| **C4 vol-expansion straddle** | gated by infra-B (multi-sprint engine rewrite); not worth the engine scope until paired-position has additional independent justification beyond C4 |
| **C6 cross-pair rotation** | **REJECTED in CAMPAIGN_013; binding cooldown for ≥ 3 discovery sprints** per `CAMPAIGN_013_REJECTION_CLOSEOUT.md` §5 |
| **C8 MWVCB** | viable but elevated CAMPAIGN_004 / CAMPAIGN_012 proximity risk; defense burden higher post-CAMPAIGN_013 (the direction-trading anti-pattern); consider after C7 if C7 rejects |
| **C9 TODCAMRS** | viable but weakest distinctness (5/6) due to CAMPAIGN_008/009 proximity + highest Pattern Q burden (slippage modeling sensitivity); consider after C7 if C7 rejects |
| **infra-A** | requires human authorization (credentialed broker account; account/transaction endpoint queries); discovery-005 cannot start it; recommended only if Phase 5 fails |
| **infra-B** | very large scope; only one candidate (C4) currently justifies it; defer until a clearer multi-candidate need emerges |
| **infra-C** | no candidate has reached `RESEARCH_PASS_UNAPPROVED`; verifier extension is post-PASS by design |
| **infra-D** | cosmetic; does not block any validation or any candidate evaluation |

## 9. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 875 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## 10. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md) (Phase 0)
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md) (Phase 1)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (Phase 2; binding turnover guardrail)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (Phase 3)
- [`NEXT_DIRECTION_REASSESSMENT_004.md`](NEXT_DIRECTION_REASSESSMENT_004.md) (predecessor reassessment)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md) (predecessor shortlist; sources for C7 / C8 / C9)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md) (Phase 5 — to be written)
- [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) (Phase 6 — to be written)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

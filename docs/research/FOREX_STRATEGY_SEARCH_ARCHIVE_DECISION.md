# Forex Strategy-Search Programme — Archive Decision

**Sprint:** `research-forex-strategy-search-archive-001` · Phase 3
**Type:** Formal archive decision. Documentation only.
**Date:** 2026-05-31
**Freeze:** intact. Paper/demo/live remain blocked.

---

## 1. Decision

**Archive the forex strategy-search programme.**

Standing status: **`ARCHIVED_STRATEGY_SEARCH`**. No active campaigns, no approved
strategies, no front-gate work, no factor discovery or validation on the current
corpus. The research platform is frozen as a reusable asset.

This is the pre-registered **Option E** from the programme-direction decision,
triggered by the FX Futures Carry Diagnostic verdict:
**`CARRY_DOES_NOT_SURVIVE_IN_FUTURES`**.

---

## 2. Why the programme is being archived

### 2a. Every shortlisted mechanism has a terminal verdict

The final evidence inventory (`FOREX_STRATEGY_SEARCH_FINAL_EVIDENCE_INVENTORY.md`)
classifies every major effort. Summary:

- **31 campaigns** — zero approved; split between rejected, cost-defeated, and
  financing-defeated.
- **Factor shortlist S1–S5** — exhausted. S4 is real but economically insignificant.
- **Front gates** — all survivors eventually rejected at train gate or earlier.
- **Non-time-bar directional lane** — retired.
- **Carry** — the canonical FX factor — non-predictive even in CME futures with the
  financing wall removed.

### 2b. The root-cause question is answered

The programme's open question was: *is recurring failure cost-defeated (maybe
fixable with a better venue) or genuinely non-predictive?*

Evidence progression:

1. **Spot era:** dominant proximate killer = cost. When effects were real (C1,
   S4, C029 gross), cost killed them. When cost was survivable, effects were null.
2. **Cross expansion:** added breadth, not cost relief. S4 found genuine structure
   still ~10× inside the band.
3. **Futures venue:** structurally removes nightly financing. Carry — the most
   futures-favourable factor — returned statistically zero predictive content
   (primary h3 +0.04 %/qtr, NW-t = 0.09; Holm rejects nothing; 24y ex-JPY
   negative and below every null).

**Conclusion:** the binding limit is **idea quality / market efficiency**, not
merely retail spot cost structure. A better venue cannot rescue a non-predictive
signal.

### 2c. No remaining reachable experiment attacks the binding constraint

Per `REMAINING_UNTESTED_MECHANISMS_AFTER_CARRY.md` and the futures diagnostic:

| Mechanism | Status |
|-----------|--------|
| Broker-financing realism | Foreclosed by inference (confirms a loss) |
| FX futures carry | **Executed → null** |
| C1 on futures intraday | Data-gated (paid feed); C1 already failed replication |
| S4 on any venue | Real but sub-cost; staleness-bound; venue-independent |
| Institutional ECN/L2 | Gated behind unavailable data/access |
| Alternative asset classes | Effectively a new project |

Continuing to mine the same corpus and mechanisms would repeat known failures
(see `DO_NOT_REPEAT_LIST.md`).

### 2d. Pre-registered trigger met

From `FINAL_PROGRAMME_DIRECTION_DECISION.md`:

> Pre-committed fallback: if the futures diagnostic shows the same cost wall
> holds … the programme moves to **Option E — Archive strategy search**.

The carry diagnostic result is stronger than "same cost wall" — it shows the
strongest candidate is **non-predictive**, not merely cost-defeated. Archive is
mandated, not discretionary.

---

## 3. Evidence that justified the decision

| Evidence | Verdict | Role in decision |
|----------|---------|------------------|
| C1 validation + cross replication | real but weak / failed replication | No generalizable directional factor |
| S2 / S3 currency strength | rejected | Cross-sectional prediction absent |
| S4 triangular RV | real but weak | Only genuine factor; economically insignificant |
| C026 timeframe ladder | cost-defeated | Pure cost gradient; no TF floor |
| C027 front-gate survivor | rejected | Last spot directional hope falsified |
| C029 range bars | cost-defeated | Alt clock ≠ edge |
| C031 vol-managed TSMOM | cost-defeated | Financing ≈4× spread |
| Spot carry validation | real but weak | Accrual exists; predictive leg null |
| **Futures carry diagnostic** | **rejected** | **Tie-breaker: non-predictive in fair venue** |

Supporting governance evidence:

- `configs/approved_strategies.yaml` — empty throughout programme.
- `check_research_freeze.py` — paper/demo loops refuse all strategies.
- 31 campaigns, 0 approvals — consistent terminal record.

---

## 4. What would be required to reopen the programme

Reopening is **not** a parameter tweak or a "one more campaign." It requires at
least **one** of the following **new inputs**, none of which exist in-repo today:

### 4a. New market (different cost/regulatory structure)

- Non-FX asset class (equities, rates, commodities) with a documented economic
  mechanism — effectively a **new project**, not a restart of this programme.
- Institutional-grade FX venue with materially different cost/access (ECN, prime
  brokerage) — requires data/access not currently held.

### 4b. New data class (unlocks untested mechanisms)

- **True tick / L2 order book** — unlocks microstructure lane that H16/H03/S4
  could only proxy on M1 mid.
- **Multi-decade fundamentals** — enables FX value (different mechanism from
  carry/momentum); requires sources beyond FRED OECD 3M.
- **Positioning / flow data** (COT, dealer positioning, options-implied) — new
  decision variables not exhausted on price-only corpus.
- **Verified broker swap/financing time series** — for honest carry P&L on spot,
  though spot carry predictive leg was already null.

### 4c. New external thesis (structurally distinct)

- A documented economic / market-structure mechanism with objective, codable
  rules — **written before coding**.
- Must be structurally different from every closed family: trend, pullback, ADX,
  MTF-confluence, microstructure fade, compression/expansion, slow-macro-context,
  cross-sectional momentum, RV spread, carry, TSMOM.
- Must **not** map onto a closed lane after stripping instrument names
  (see `DO_NOT_REPEAT_LIST.md` §3 hidden re-tunes).

### 4d. Gating conditions (ALL required if reopening)

Even with a valid new input:

1. Precommitted hypothesis + cost/stop/multiple-testing model (locked-definition
   doc before any run).
2. Standard falsification panel: intrabar stop + conservative cost + MC haircut +
   year/half-split + latency-independence.
3. Train/validation support without touching TEST; lockbox opens once only.
4. Explicit separation of "effect exists" vs "tradable edge exists."
5. Front-gate or cost-feasibility screen before any full campaign.
6. Human review before any entry in `configs/approved_strategies.yaml`.

### 4e. Explicitly insufficient to reopen

- Any indicator threshold change (ADX 25, z=2.0→2.5, etc.).
- Timeframe swap without new mechanism (M5 instead of M15).
- Single-pair focus without pair-specific mechanism.
- "Almost flat / less-bad" results.
- Re-running rejected campaigns with relaxed gates.
- Mining the same data with new slicing (multiple-testing by another name).
- Re-tuning C1, C027, C029, H16, H03, C028, C031, or any closed family on
  crosses, futures, or alt bars.

---

## 5. What archiving means concretely

| Action | Status |
|--------|--------|
| Strategy campaigns | **Stopped** — no CAMPAIGN_032+ |
| Factor discovery/validation | **Stopped** on current corpus |
| Front-gate screening | **Stopped** |
| `configs/approved_strategies.yaml` | **Empty** — remains enforced |
| Paper/demo/live loops | **Blocked** — refuse all strategies |
| Research platform (lab, data, gates) | **Preserved** — frozen asset |
| Documentation | **Consolidated** — this archive package |

Archiving is **not**:

- A claim that no FX edge exists anywhere in the world.
- A claim that the infrastructure was wasted — it produced clean verdicts.
- Permission to silently weaken the freeze or run live trading.

---

## 6. Relationship to prior standing decisions

| Prior decision | Disposition |
|----------------|-------------|
| `PAUSE_STRATEGY_RESEARCH` (2026-05-28) | **Superseded** by `ARCHIVED_STRATEGY_SEARCH` |
| `FINAL_PROGRAMME_DIRECTION_DECISION` Option C | **Completed** — futures diagnostic executed |
| Non-time-bar lane retirement | **Affirmed** — remains closed |
| C022/C023 family retirement | **Affirmed** — remains closed |
| Cross-factor S1–S5 shortlist | **Affirmed exhausted** |

---

## 7. Compliance confirmation

- **Campaign created this sprint?** No.
- **Strategy approved?** No.
- **Paper/demo/live enabled?** No.
- **Closed lanes reopened?** No.
- **Freeze weakened?** No.

---

## 8. Cross-references

- Trigger verdict: `FX_FUTURES_CARRY_VERDICT.md`
- Programme implication: `FX_FUTURES_CARRY_PROGRAMME_IMPLICATION.md`
- Evidence ledger: `FOREX_STRATEGY_SEARCH_FINAL_EVIDENCE_INVENTORY.md`
- Lessons: `FOREX_STRATEGY_SEARCH_FINAL_LESSONS.md`
- Future directions (non-active): `FOREX_RESEARCH_FUTURE_OPPORTUNITIES.md`
- Prior restart criteria: `STRATEGY_RESEARCH_RESTART_CRITERIA.md` (incorporated above)
